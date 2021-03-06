# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.addons import decimal_precision as dp

from odoo.exceptions import UserError, ValidationError

from odoo import api, fields, models, _, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

class BillOfMaterialsLines(models.Model):
	_inherit= 'mrp.bom.line'

	product_manu_qty = fields.Float(
        'Product Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)

	product_allowance_qty = fields.Float(
        'Allowance Quantity', default=0.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)

	product_qty = fields.Float(
        'Total Product Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'), required=True)

class StockPicking(models.Model):
	_inherit ='stock.picking'

	allow_alter_info = fields.Boolean(string='Allow Override', default=False)


class StockMoves(models.Model):
	_inherit ='stock.move'

	product_manu_qty = fields.Float(
        'Product Quantity', default=1.0,
        digits=dp.get_precision('Product Unit of Measure'))


	product_manu_allowance_qty = fields.Float(
        'Allowance Quantity', default=0.0,
        digits=dp.get_precision('Product Unit of Measure'))

	allow_alter_info = fields.Boolean(string='Allow Override', default=False)


class MrpProduction(models.Model):
	_inherit ='mrp.production'

	move_raw_ids = fields.One2many(
        'stock.move', 'raw_material_production_id', 'Raw Materials', oldname='move_lines',
        copy=False, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        domain=[('scrapped', '=', False),('allow_alter_info', '=', False)])


	@api.multi
	def button_mark_done(self):
		res = super(MrpProduction, self).button_mark_done()
		#Create a Transfer V/Production to  WH
		stock_picking_model = self.env['stock.picking']
		total_allow_qty = 0.0
		sequence_int = 0
		for move in self.move_raw_ids:
			total_allow_qty += move.product_manu_allowance_qty
			sequence_int = move.sequence

		if total_allow_qty  <= 0.0:
			return res

		stock_picking_id = stock_picking_model.create({
			'origin': self.name,
			'company_id': self.company_id.id,
			'picking_type_id': self.picking_type_id.id,
			'location_id': self.env.ref('stock.location_production').id,
			'location_dest_id': self.picking_type_id.default_location_dest_id.id,
			'allow_alter_info':True,
			})
		for move in self.move_raw_ids:
			if move.product_manu_allowance_qty > 0.0:
				data = {
						'picking_id': stock_picking_id.id,
						'sequence': sequence_int,
						'name': self.name,
						'reference': self.name,
						'date': self.date_planned_start,
						'date_expected': self.date_planned_start,
						#'bom_line_id': move.bom_line_id.id,
						'product_id': move.product_id.id,
						'product_uom_qty': move.product_manu_allowance_qty, #+ bom_line.product_allowance_qty or 0.0,
						'product_uom': move.product_uom.id,
						'location_id': self.env.ref('stock.location_production').id,
						'location_dest_id': self.picking_type_id.default_location_dest_id.id,  #self.product_id.property_stock_production.id,
						'raw_material_production_id': self.id,
						'company_id': self.company_id.id,
						#'operation_id': bom_line.operation_id.id or alt_op,
						#'price_unit': bom_line.product_id.standard_price,
						'procure_method': 'make_to_stock',
						'origin': self.name,
						'warehouse_id': stock_picking_id.location_id.get_warehouse().id,
						'group_id': self.procurement_group_id.id,
						'propagate': self.propagate,
						'allow_alter_info': True,}
							#'unit_factor': quantity / original_quantity,
				sequence_int +=1
				stock_move_obj = self.env['stock.move'].create(data)
				stock_move_obj.reference = self.name
		stock_picking_id.action_confirm()

		if stock_picking_id.state != 'assigned':
			#raise Warning(stock_picking_id.state)
			stock_picking_idan.action_assign()

		for stock_move in stock_picking_id.move_lines:
			for stock_move_line in stock_move.move_line_ids:
				stock_move_line.qty_done = stock_move_line.product_uom_qty

		# Auto Validate
		pick_to_do = self.env['stock.picking']
		pick_to_do |= stock_picking_id
		pick_to_do.action_done()
		#Create an Internal Transfer for the WH to Scrap
		stock_scrap_obj = self.env['stock.scrap']
		for move in self.move_raw_ids:
			if move.product_manu_allowance_qty > 0.0:
				data ={
						'production_id' : self.id,
						'product_id':  move.product_id.id,
						'scrap_qty': move.product_manu_allowance_qty,
						'product_uom_id': move.product_uom.id,
				}
				res_sc = stock_scrap_obj.create(data)
				if res_sc:
					res_sc.action_validate()
		return res
	
	@api.multi
	def _update_raw_move(self, bom_line, line_data):
		quantity = line_data['qty']
		self.ensure_one()
		move = self.move_raw_ids.filtered(lambda x: x.bom_line_id.id == bom_line.id and x.state not in ('done', 'cancel'))
		if move:
			if quantity > 0:
				move[0].write({'product_uom_qty': quantity,
							   'product_manu_allowance_qty': move.bom_line_id.product_allowance_qty * quantity,})
			elif quantity < 0:  # Do not remove 0 lines
				if move[0].quantity_done > 0:
					raise UserError(_('Lines need to be deleted, but can not as you still have some quantities to consume in them. '))
				move[0]._action_cancel()
				move[0].unlink()
			return move
		else:
			self._generate_raw_move(bom_line, line_data)


	@api.multi
	def _generate_moves(self):
		for production in self:
			production._generate_finished_moves()
			factor = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id) / production.bom_id.product_qty
			boms, lines = production.bom_id.explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
			production._generate_raw_moves(lines)
			# Check for all draft moves whether they are mto or not
			production._adjust_procure_method()
			production.move_raw_ids._action_confirm()
		return True

	def _generate_raw_move(self, bom_line, line_data):
		quantity = line_data['qty']
		# alt_op needed for the case when you explode phantom bom and all the lines will be consumed in the operation given by the parent bom line
		alt_op = line_data['parent_line'] and line_data['parent_line'].operation_id.id or False

		if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom':
		    return self.env['stock.move']
		if bom_line.product_id.type not in ['product', 'consu']:
		    return self.env['stock.move']
		if self.routing_id:
		    routing = self.routing_id
		else:
		    routing = self.bom_id.routing_id
		if routing and routing.location_id:
		    source_location = routing.location_id
		else:
		    source_location = self.location_src_id
		original_quantity = (self.product_qty - self.qty_produced) or 1.0


		#Check the BOM if Generic
		BRAND ='BRAND'
		GENERIC = 'GENERIC'
		stock_quant_model = self.env['stock.quant']
		stock_move_model = self.env['stock.move']

		bln_no_stock_found = True
		check_bom_lines = True

		product_id = bom_line.product_id
		#_logger.info('START' +  bom_line.product_id.name + '(' +  bom_line.product_id.attribute_value_ids.name  + ')')
		if bom_line.product_id.product_tmpl_id.attribute_line_ids:
			_logger.info('START BOM' +  bom_line.product_id.name + '(' +  bom_line.product_id.attribute_value_ids.name  + ')')

			_logger.info(1)
			if bom_line.product_id.attribute_value_ids:
				_logger.info(2)
				if bom_line.product_id.attribute_value_ids.name.upper() == GENERIC:
					_logger.info(3)
					#Validate if Product has a related Product
					if bom_line.product_id.is_check_related_product:
						#Product with Generic Name and the Product will check if has a Related Product
						#If Related Product is Generic then Get all the Variants of the said Related Product
						_logger.info('Related')
						_logger.info(4)
						related_product_id = bom_line.product_id.related_product_id
						related_product_id_variant = bom_line.product_id.related_product_id.attribute_value_ids
						if related_product_id_variant.name.upper() == GENERIC:
							_logger.info(5)
							if related_product_id.product_tmpl_id.product_variant_ids:
								_logger.info(6)
								for variant in related_product_id.product_tmpl_id.product_variant_ids:
									if variant.attribute_value_ids.name.upper() != GENERIC:
										# Check first if Product already reserved in this MO
										# And This will Assume the Product has Quantity and will have no Exemption Occur
										stock_model_obj = stock_move_model.search([('product_id','=', variant.id),('production_id','=', self.id)])
										if stock_model_obj:
											product_id = stock_model_obj.related_product_id
											bln_no_stock_found = False
											check_bom_lines = False
											break

							# If no Reserved in this MO then Check BOM	
							if check_bom_lines:
								_logger.info(7)
								for lp_bom_line in self.bom_id.bom_line_ids:
									#if Exist in BOM then Check for Again for Generic Value
									if lp_bom_line.product_id.id == related_product_id.id:
										related_bom_line_product = lp_bom_line.product_id
										if related_bom_line_product.attribute_value_ids.name.upper() == GENERIC:
											_logger.info(7.1)
											# Loop Again to Check the Variant List and FIFO Sequence
											for variant in related_bom_line_product.product_tmpl_id.product_variant_ids:
												_logger.info(7.2)
												if variant.attribute_value_ids.name.upper() != GENERIC:
													_logger.info(7.3)
													stock_quant_obj = stock_quant_model.search([('product_id', '=', variant.related_product_id.id),('location_id', '=', source_location.id)], order='in_date, id')
													if stock_quant_obj:
														_logger.info(7.4)
														total_qty_stq = stock_quant_obj.quantity - stock_quant_obj.reserved_quantity
														_logger.info('Name ' + product_id.name + '(' + variant.attribute_value_ids.name + ')' + ' T QTY :' + str(total_qty_stq) + ' QTY ' + str(stock_quant_obj.quantity) + ' RES ' + str(stock_quant_obj.reserved_quantity))
														if total_qty_stq >= quantity:
															_logger.info(7.5)
															product_id = variant.related_product_id
															bln_no_stock_found = False
															check_bom_lines = False
															break
										else:
											_logger.info(8)
											bln_no_stock_found = False
											product_id =  related_bom_line_product

						else:
							_logger.info(9)
							bln_no_stock_found = False
							product_id =  bom_line.product_id
					else:
						#Product with Only Generic and its Variants Value and No Link Related Product
						_logger.info(10)
						product_id = bom_line.product_id
						if bom_line.product_id.product_tmpl_id.product_variant_ids:
							_logger.info(11)
							for variant in bom_line.product_id.product_tmpl_id.product_variant_ids:
								if variant.attribute_value_ids.name.upper() != GENERIC:
									#Check if Variant has available Qty to the source Location
									stock_quant_obj = stock_quant_model.search([('product_id', '=', variant.id),('location_id', '=', source_location.id)], order='in_date, id')
									if stock_quant_obj:
										_logger.info(12)

										total_qty_stq = stock_quant_obj.quantity - stock_quant_obj.reserved_quantity
										_logger.info('Name ' + product_id.name + '(' + variant.attribute_value_ids.name + ')' + ' T QTY :' + str(total_qty_stq) + ' QTY ' + str(stock_quant_obj.quantity) + ' RES ' + str(stock_quant_obj.reserved_quantity))
										if total_qty_stq >= quantity:
											product_id = variant
											bln_no_stock_found = False
											_logger.info('YES')
											break
										_logger.info(13)

					if bln_no_stock_found:
						#raise UserError(_('BOM Line Item %s and its variants has no stock. Please check the Quantity.' %(product_id.name))) 
						raise UserError(_('BOM Line Item %s (%s) and its variants has no stock. Please check the Quantity.' %(product_id.name, product_id.attribute_value_ids and product_id.attribute_value_ids.name or 'None'))) 

		_logger.info(bom_line.product_uom_id.name)
		_logger.info(bom_line.product_id.name)

		data = {
			'sequence': bom_line.sequence,
			'name': self.name,
			'date': self.date_planned_start,
			'date_expected': self.date_planned_start,
			'bom_line_id': bom_line.id,
			'product_id': product_id.id, #bom_line.product_id.id,
			'product_uom_qty': quantity , #+ bom_line.product_allowance_qty or 0.0,
			'product_uom': bom_line.product_uom_id.id,
			'location_id': source_location.id,
			'location_dest_id': self.product_id.property_stock_production.id,
			'raw_material_production_id': self.id,
			'company_id': self.company_id.id,
			'operation_id': bom_line.operation_id.id or alt_op,
			'price_unit': product_id.standard_price, #bom_line.product_id.standard_price,
			'procure_method': 'make_to_stock',
			'origin': self.name,
			'warehouse_id': source_location.get_warehouse().id,
			'group_id': self.procurement_group_id.id,
			'propagate': self.propagate,
			'unit_factor': quantity / original_quantity,
			'product_manu_qty': bom_line.product_manu_qty,
			'product_manu_allowance_qty': bom_line.product_allowance_qty * quantity,
		}

		return self.env['stock.move'].create(data)
