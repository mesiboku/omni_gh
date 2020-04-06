# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero, pycompat

import xlwt 
import xlrd
import datetime
import base64
import os, sys

import logging

_logger = logging.getLogger(__name__)


class UploadPayment(models.TransientModel):
	_name = 'account.payment.upload'


	payment_id  = fields.Many2one('account.payment', string='Payment')

	payment_spreadsheet = fields.Binary(string='Invoice/s Spreadsheet', required=True)
	file_name = fields.Char("File Name")



	@api.one
	def paymentMatching(self):
		account_payment_obj = self.env['account.payment'].browse(self._context.get('active_ids', []))

		if account_payment_obj:
			_logger.info('START----------------------')
			if account_payment_obj.state in ['draft', 'reconciled', 'sent', 'cancelled']:
				raise UserError(_('Cannot Proceed Payment should be in Open Status.'))

			account_payment_obj.write({ 
										'payment_spreadsheet': self.payment_spreadsheet,
										'file_name': self.file_name,
										})

			#Get Credit Account Move Line
			account_move_line_obj = self.env['account.move.line'].search([('payment_id', '=', account_payment_obj.id), 
																		  #('amount_residual', '!=', 0.0), 
																		  #('amount_residual_currency', '!=', 0.0), 
																		  ('credit', '>', 0.00), 
																		  ('debit', '=', 0.00)])
			#raise Warning(account_move_line_obj)
			if account_move_line_obj:
				_logger.info('START---------------------- 2')
				account_payment_obj.generatePaymentMatching(account_move_line_obj.id)

	#@api.model
	#def _run_fifo(self, move, quantity=None):
	#	result = super(StockMove, self)._run_fifo(move.sudo(), quantity)
	#	return result