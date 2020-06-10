# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero, pycompat

import xlwt 
import xlrd
import datetime
import base64
import os, sys

import odoo.tools as tools

import logging

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
	_inherit = 'account.payment'


	payment_spreadsheet = fields.Binary(string='Invoice/s Spreadsheet')
	file_name = fields.Char("File Name")

	payment_unmatch_ids = fields.One2many('account.payment.unmatch', 'payment_id', string='Invoice Discrepancy')

	@api.one
	def generatePaymentMatching(self, credit_move_line_id):
		addons_paths = tools.config['addons_path'] 
		addons_lists = addons_paths.split(',')
		xls_dir_path = ""
		if os.path.isdir('/odoo/TemporaryFiles'):
			xls_dir_path = '/odoo/TemporaryFiles'
		else:
			for addons_list in addons_lists:
				if os.path.isdir(addons_list + '/omni_gh_payment_matching_upload'):
					xls_dir_path = addons_list + '/omni_gh_payment_matching_upload'
					break

		uid = self._uid
		FILENAME = xls_dir_path + '/payment_matching_UID'+str(uid) + '.xls'

		#FILENAME = "/odoo/TemporaryFiles/payment_matching_UID"+str(uid) +".xls"
		with open(FILENAME, "wb") as f:
			text = self.payment_spreadsheet
			f.write(base64.b64decode(text))
		xl_workbook = xlrd.open_workbook(FILENAME)
		xl_sheet = xl_workbook.sheet_by_index(0)

		account_invoice = self.env['account.invoice']

		#Remove First all the Payment Log
		account_payment_matching_model = self.env['account.payment.unmatch']
		account_payment_matching_log = self.env['account.payment.unmatch'].search([('payment_id','=', self.id)])
		account_payment_matching_log.unlink()

		for row in range(1, xl_sheet.nrows):
			col_date = ''
			log_info =""
			is_jl_err = False
			col_legacy_invoice_number = str(int(xl_sheet.cell(row, 1).value or 0))
			col_store_number = str(int(xl_sheet.cell(row, 2).value or 0))
			col_amount  = float(xl_sheet.cell(row, 3).value or 0.00)

			_logger.info(col_legacy_invoice_number)

			#Check if there's a legacy invoice
			account_invoice_obj = account_invoice.search([('legacy_invoice', '=', col_legacy_invoice_number)])
			#if col_legacy_invoice_number == '7777':
			#	raise Warning(account_invoice_obj)

			if not account_invoice_obj:
				_logger.info('No Invoice')
				log_info += "* Uploaded Legacy Invoice Number does not exists. \n"


			if account_invoice_obj:				
				if account_invoice_obj.state != 'open':
					log_info += "* Invoice status is %s. \n" %(account_invoice_obj.state)

				if account_invoice_obj.partner_id != self.partner_id:
					log_info += "* Payment Customer info is %s but the Uploaded Invoice Customer info is %s. \n " %(self.partner_id.name, account_invoice_obj.partner_id.name)
				
				if not account_invoice_obj.store_number:
					#Check if Store Number has No Value
					log_info += "* Invoice Number %s but no Store Number info. \n " %(account_invoice_obj.number)
				else:
					#if isinstance(account_invoice_obj.store_number, bool):
					#	log_info += "* Legacy Invoice Number %s has no Store Number info. \n " %(account_invoice_obj.name)
					if len(account_invoice_obj.store_number) == 0:
						log_info += "* Legacy Invoice Number %s has no Store Number info. \n " %(account_invoice_obj.name)
					else:
						if account_invoice_obj.store_number[0:account_invoice_obj.store_number.find(' ')] != col_store_number:
							log_info += "* Invoice Store Number info is %s but the Uploaded Invoice Store Number info is %s. \n " %(account_invoice_obj.store_number[0:account_invoice_obj.store_number.find(' ')], 
																									col_store_number)

				if account_invoice_obj.amount_total != col_amount:
					log_info += "* Invoice Amount to be paid is %.2f but the Uploaded Invoice Amount is is %.2f. \n " %(account_invoice_obj.amount_total, 
																														col_amount)

				_logger.info('HERE------------ACCEPTED')
				#Check if Account status if Open
				if account_invoice_obj.state != 'open':
					_logger.info('HERE------------NOT OPEN')
					account_payment_matching_model.create({
						'payment_id': self.id,
						'col_legacy_invoice_number': col_legacy_invoice_number,
						'col_store_number': col_store_number,
						'col_amount': col_amount,
						'discrepany_log': log_info,
						'invoice_id': account_invoice_obj.id or False,})
					continue

				#Check if Invoice Customer Info does match in Payment Partner
				if account_invoice_obj.partner_id == self.partner_id:
					if account_invoice_obj.store_number:
						#Check if Store Number does match in Uploaded Store Number
						if account_invoice_obj.store_number[0:account_invoice_obj.store_number.find(' ')] == col_store_number:
							#Check if Invoice Amount does match in Uploaded Payment
							if account_invoice_obj.amount_total == col_amount:
								#If All Qualify then Start Invoice Payment
								_logger.info('HERE------------4')
								if account_invoice_obj.account_id.company_id.id != self.env.user.company_id.id:
									_logger.info(account_invoice_obj.number)
									_logger.info(account_invoice_obj.company_id.name)
									_logger.info(account_invoice_obj.account_id.name)
									_logger.info(account_invoice_obj.account_id.company_id.name)
									log_info += "* Legacy Invoice Number %s Discrepancy in Account Receivable COA. \n " %(account_invoice_obj.name)
									is_jl_err = True
								else:
									account_invoice_obj.assign_outstanding_credit(credit_move_line_id)
			if log_info:
				log_info += "** In Spreadsheet Row %d" %(row)
				val = {
					'payment_id': self.id,
					'col_legacy_invoice_number': col_legacy_invoice_number,
					'col_store_number': col_store_number,
					'col_amount': col_amount,
					'discrepany_log': log_info,
					'invoice_id': account_invoice_obj.id or False,}
				if is_jl_err:
					val['is_error_jl'] = True
				account_payment_matching_model.create(val)

	@api.multi
	def write(self, vals):
		res = super(AccountPayment, self).write(vals)
		if res:
			for payment in self:
				if payment.payment_spreadsheet:
					message_header = "<strong>Uploaded File</strong> <br/>"
					attachment = [(payment.file_name, payment.payment_spreadsheet)]
					payment_message_id = payment.message_post(body=message_header, attachments=attachment)
		return res

	def generateAllJLEDisc(self):
		for payment_u in self.payment_unmatch_ids.search([('is_error_jl','=', True)]):
			if payment_u.is_error_jl == True:
				payment_u.realignedJLEntries()

class AccountPaymentUnmatch(models.Model):
	_name = 'account.payment.unmatch'

	payment_id = fields.Many2one('account.payment', 'Payment')
	invoice_id = fields.Many2one('account.invoice', 'Invoice')
	col_legacy_invoice_number = fields.Char('Legacy Invoice')
	col_store_number = fields.Char('Store Number')
	col_amount = fields.Monetary(string='Payment Amount', required=True)
	currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
	discrepany_log = fields.Text(string='Discrepancy')

	#For Invoice Info
	store_number = fields.Char(related='invoice_id.legacy_invoice', readonly=True, copy=False)
	amount_total = fields.Monetary(related='invoice_id.amount_total', readonly=True, copy=False)
	is_error_jl = fields.Boolean(string='Error in  JL Entries', default=False)

	def realignedJLEntries(self):
		for rec in self:
			if rec.invoice_id:
				invoice_company_id = rec.invoice_id.company_id.id
				acct_journal = self.env['account.journal'].search([('name', '=','Customer Invoices'),
																  ('type', '=','sale'),
																  ('company_id', '=',invoice_company_id)])
				acct_acct = self.env['account.account'].search([('name', '=','Account Receivable'),
																  ('code', '=','101200'),
																  ('company_id', '=',invoice_company_id)])
				acct_acct_prod_sale = self.env['account.account'].search([('name', '=','Product Sales'),
																  ('code', '=','200000'),
																  ('company_id', '=',invoice_company_id)])

				if acct_journal:
					if rec.invoice_id.state == 'open':
						#Cancel First the JL Entries
						if rec.invoice_id.move_id:
							rec.invoice_id.move_id.button_cancel()
							#After Cancellation Start Cancel Invoice
							rec.invoice_id.action_invoice_cancel()
							#After Cancellation of Invoice Back To Draft
							rec.invoice_id.action_invoice_draft()						
							rec.invoice_id.account_id = acct_acct.id
							rec.invoice_id.journal_id = acct_journal.id

							#Change the Account for Invoice Lines and  Tax
							for line in  rec.invoice_id.invoice_line_ids:
								line.account_id = acct_acct_prod_sale.id
							#Change the Tax
							for tax_id in  rec.invoice_id.tax_line_ids:
								tax_id.account_id = acct_acct_prod_sale.id							
							rec.invoice_id.action_invoice_open()
							rec.is_error_jl = False
						else:
							raise UserError(_('Invoices Status is not Open'))
