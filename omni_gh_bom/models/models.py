# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
import logging
_logger = logging.getLogger(__name__)



class omniGhBoM(models.Model):
	_inherit = 'mrp.bom'

	round_up = fields.Boolean('Round Up')



class omniGhBoMLine(models.Model):
	_inherit = 'mrp.bom.line'

	round_up_checkbox = fields.Boolean('Round Up')



class Stock_Move(models.Model):
	_inherit = 'stock.move'

	round_up = fields.Boolean('Round Up')



class Rounded_Qty(models.Model):
	_inherit = 'mrp.production'

	@api.multi
	def round_up_qty(self):
		for production in self:
			if production.move_raw_ids:
				for moves in production.move_raw_ids:
					if str(moves.round_up) == 'True':
						round_initial_demand = self.env['stock.picking'].search([('origin','=', production.name)])
						# raise Warning(round_initial_demand)
						data1 = round(moves.product_uom_qty)
						if round_initial_demand:
							for x in round_initial_demand:
								for y in x.move_lines:
									if moves.product_id == y.product_id:
										y.update({
										'product_uom_qty': data1
										})
						moves.update({
						'round_up': True,
						'product_uom_qty': data1
						})
