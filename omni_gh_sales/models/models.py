# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError


class stockPickingReturnCountToSales(models.TransientModel):
	_inherit = 'stock.return.picking'


	def create_returns(self):
		if self.picking_id.sale_id:
			for sale_order_line in self.picking_id.sale_id.order_line:
				for return_product in self.product_return_moves:
					if sale_order_line.product_id == return_product.product_id:
						sale_order_line.write({
							'return_count': return_product.quantity
							})
					else:
						data = self.env['mrp.bom'].search([('product_tmpl_id', '=', sale_order_line.product_id.product_tmpl_id.id)])
						# raise Warning(data)
						if data:
							if data.bom_line_ids:
								for x in data.bom_line_ids:
									if x.product_id == return_product.product_id:
										# raise Warning(str(x.product_id.name) + ' ' + str(return_product.product_id.name))
										sale_order_line.write({
											'return_count': return_product.quantity
											})
							# for x in data:
								# if sale_order_line.product_id.id == data
						# for boms in return_product.product_id.bom_ids:
						# 	if boms:
						# 		for bom_line in boms:
						# 			if bom_line:
						# 				for line_ids in bom_line.bom_line_ids:
						# 					if line_ids:
						# 						_logger.info("PRODUCT 1 " + str(sale_order_line.product_id.name))
						# 						_logger.info("PRODUCT 2 " + str(line_ids.product_id.name))
						# 						if sale_order_line.product_id == line_ids.product_id:
						# 							raise Warning(line_ids.product_id.name)
						# 							sale_order_line.write({
						# 								'return_count': return_product.quantity
						# 								})
		# raise Warning('HIT')
		return super(stockPickingReturnCountToSales, self).create_returns()



class saleOrderLine(models.Model):
	_inherit = 'sale.order.line'


	return_count = fields.Float( string='Returned', readonly=True)