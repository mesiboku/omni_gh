# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

GH_IN_0027_PO_00027 = 8

class ProjectWizard(models.TransientModel):
	_name = 'data.mig.stock.moves'

	name = fields.Char(string='Collection Sheet Excel', default='Stoc Moves')


	@api.model
	def startProcessSpecificIds(self):
		#This will only Target the Records for Specific Ids		
		stock_picking = self.env['stock.picking'].search([('state', '=', 'done'),
														  ('id','=', GH_IN_0027_PO_00027)])

		for stock_move in stock_picking.move_lines:
			for stock_move_line in  stock_move.move_line_ids:
				uom_factor = 0.0
				uom_purchase_factor = stock_move_line.purchase_order_uom_id.factor_inv
				purchase_qty_done = (stock_move_line.qty_done/uom_purchase_factor)
				stock_move_line.write({'purchase_qty_done': purchase_qty_done
								})

	@api.model
	def startProcess(self):
		stock_picking = self.env['stock.picking'].search([('state', '=', 'done'),
														  ('id','not in', [GH_IN_0027_PO_00027])]) 
		if stock_picking:
			_logger.info('START MIGRATION')
			_logger.info('TOTAL NUMBER OF RECORDS: ' + str(len(stock_picking)))

			for stock in stock_picking:
				if stock.purchase_id:
					_logger.info('PICK NUMBER ' + stock.name + ' PO NUMBER ' + stock.purchase_id.name )
					_logger.info('NUMBER OF LINES ' + str(len(stock.move_lines)))
					for stock_move in stock.move_lines:
						_logger.info('MOVES LINE ID ' + str(stock_move.id))

						for stock_move_line in  stock_move.move_line_ids:
							purchase_qty_done = 0.0
							if stock_move_line.purchase_line_move_id:

								if stock_move_line.purchase_order_uom_id != stock_move_line.product_uom_id:
									uom_purchase_factor = 0.0
									uom_factor = 0.0
									if stock_move_line.purchase_order_uom_id.uom_type == 'bigger':
										uom_purchase_factor = stock_move_line.purchase_order_uom_id.factor_inv
									elif stock_move_line.purchase_order_uom_id.uom_type == 'smaller':
										uom_purchase_factor = stock_move_line.purchase_order_uom_id.factor_inv
									else:
										uom_purchase_factor = 1

									if stock_move_line.product_uom_id.uom_type == 'bigger':
										uom_factor = stock_move_line.product_uom_id.factor
									elif stock_move_line.product_uom_id.uom_type == 'smaller':
										uom_factor = stock_move_line.product_uom_id.factor
									else:
										uom_factor = 1
									purchase_qty_done = (stock_move_line.qty_done/uom_factor) / uom_purchase_factor
								else:
									purchase_qty_done = stock_move_line.qty_done

							stock_move_line.write({
								'purchase_qty_done': purchase_qty_done
								})
		return True