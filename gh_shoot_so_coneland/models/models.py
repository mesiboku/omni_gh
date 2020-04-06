# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	@api.multi
	def get_bom_details_summary(self):
		if self.invoice_line_ids: 
			product_bom_list = {}
			for invoice_id in self.invoice_line_ids:
				bom_obj = self.env['mrp.bom'].search([('product_tmpl_id','=', invoice_id.product_id.product_tmpl_id.id),
													  ('company_id','=', self.company_id.id),
													  ('type','=', 'phantom')], limit=1)
				if bom_obj:
					quantity_converted = invoice_id.quantity / bom_obj.product_qty
					bom_ctr = 1

					for line_id in bom_obj.bom_line_ids:
						if line_id.id != bom_obj.bom_line_ids.ids[0]:

							names = str(line_id.product_id.id) + 'UOM' + str(line_id.product_uom_id.id)
							product_name =  line_id.product_id.name

							if line_id.product_id.description_sale:
								product_name = line_id.product_id.description_sale

							if names not in product_bom_list:
								product_bom_list[names] = [
									product_name,
									line_id.product_uom_id,
									quantity_converted * line_id.product_qty]
							else:
								product_bom_list[names][2] += (quantity_converted * line_id.product_qty)
							bom_ctr +=1
			return product_bom_list
		return False



class AccountInvoiceLine(models.Model):
	_inherit = 'account.invoice.line'

	@api.multi
	def get_product_bom_details(self):
		self.ensure_one()
		bom_obj = self.env['mrp.bom'].search([('product_tmpl_id','=', self.product_id.product_tmpl_id.id),
										 ('company_id','=', self.company_id.id),
										 ('type','=', 'phantom')], limit=1)
		if bom_obj:
			#raise Warning(bom_obj.bom_line_ids[1:])
			return bom_obj.bom_line_ids[0]

		return False







# class goodheart(models.Model):
#     _name = 'goodheart.goodheart'
#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
