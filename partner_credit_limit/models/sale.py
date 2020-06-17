# See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class SaleOrder(models.Model):
	_inherit = "sale.order"

	@api.model
	def create(self, vals):
		partner = self.env['res.partner'].search([('id', '=', vals['partner_id'])])
		if partner:
			for info in partner:
				if info.one_in_one_terms:
					sales = self.env['sale.order'].search([
						('partner_id', '=', vals['partner_id']), 
						('invoice_status', 'not in', [('invoiced')])
						])
					findInvoice = self.env['account.invoice'].search([('partner_id', '=', vals['partner_id']),('state', 'not in', ['paid','cancel'])])

					total_unpaid = 0

					if len(sales) > 0:
						raise UserError(_('Partner still has pending Sales Order or unpaid Invoice .'))
					elif len(findInvoice) > 0:
						raise UserError(_('Partner still has pending Sales Order or unpaid Invoice .' ))


		result = super(SaleOrder, self).create(vals)
		return result

	@api.multi
	def check_limit(self):
		# final_credit, so_credit = 0.0, 0.0
		# partner = self.credit_limit
		# sales = self.env['sale.order'].search([('partner_id', '=', self.partner_id.id), ('invoice_status', 'not in', [('upselling','to invoice')])])
		# for sale in sales:
		#     total_unpaid = 0
		#     total_unpaid = total_unpaid + sale.amount_total
		#
		# for order in self:
		#     total_paid = 0.0
		#     so_total = order.amount_total + order.amount_tax
		#     for invoice_id in self:
		#         invoice_id = invoice_id.invoice_ids
		#         for invoice_id in invoice_id:
		#             if invoice_id.state == 'paid':
		#                 total_paid += invoice_id.payments_widget
		#     final_credit += so_total - total_paid
		#     if final_credit > partner.credit_limit:
		#         raise UserError('Error')
		# return True

		self.ensure_one()
		partner = self.partner_id
		moveline_obj = self.env['account.move.line']
		movelines = moveline_obj.search(
			[('partner_id', '=', partner.id),
			 ('account_id.user_type_id.name', 'in', ['Receivable', 'Payable']),
			 ('full_reconcile_id', '=', False)]
		)
		debit, credit = 0.0, 0.0
		today_dt = datetime.strftime(datetime.now().date(), DF)
		for line in movelines:
			# if line.date_maturity < today_dt:
			credit += line.debit
			debit += line.credit
		sales = self.env['sale.order'].search([('partner_id', '=', self.partner_id.id), ('invoice_status', 'not in', [('invoiced')])])
		total_unpaid = 0
		for sale in sales:
			total_unpaid = total_unpaid + sale.amount_total
		# raise Warning(total_unpaid)

		if (credit - debit + self.amount_total) > partner.credit_limit:
			# raise Warning ('total_unpaid Clean')
			if not partner.over_credit:
				msg = 'Can not confirm Sale Order,Total mature due Amount ' \
					  '%s as on %s !\nCheck Partner Accounts or Credit ' \
					  'Limits !' % (credit - debit, today_dt)
				raise UserError(_('Credit Over Limits !\n' + msg))
			partner.write({'credit_limit': credit - debit + self.amount_total})

		elif total_unpaid > partner.credit_limit:
			# raise Warning ('total_unpaid UnClean')
			if not partner.over_credit:
				msg = 'Can not confirm Sale Order,Total mature due Amount ' \
					  '%s as on %s !\nCheck Partner Accounts or Credit ' \
					  'Limits !' % (credit - debit, today_dt)
				raise UserError(_('Credit Over Limits !\n' + msg))
			partner.write({'credit_limit': credit - debit + self.amount_total})

		return True

	@api.multi
	def action_confirm(self):
		res = super(SaleOrder, self).action_confirm()
		for order in self:
			order.check_limit()

		return res
