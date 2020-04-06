# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 
import logging
_logger = logging.getLogger(__name__)

class StockPickingType(models.Model):
	_inherit = 'stock.picking.type'

	belongs_to_company = fields.Boolean('Belong to the user\'s current company', compute="_belong_to_company", search="_search_company_operation",)
	company_id = fields.Many2one('res.company',string='Company', related='warehouse_id.company_id',readonly=True)


	@api.multi
	@api.depends('warehouse_id.company_id')
	def _belong_to_company(self):
		for operation_type in self:
			operation_type.belong_to_company = (operation_type.warehouse_id.company_id.id == self.env.user.company_id.id)

	@api.multi
	def _search_company_operation(self , operator, value):
		if value:
			recs = self.search([('company_id', operator, self.env.user.company_id.id)])
		elif operator == '=':
			recs = self.search([('company_id', '!=', self.env.user.company_id.id)])
		else:
			recs = self.search([('company_id', operator, self.env.user.company_id.id)])
		return [('id', 'in', [x.id for x in recs])]