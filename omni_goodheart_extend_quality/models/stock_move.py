from datetime import datetime
from dateutil.relativedelta import relativedelta
import random

from odoo import api, fields, models, _, SUPERUSER_ID
from collections import defaultdict

class StockMove(models.Model):
	_inherit= 'stock.move'

	# def _action_assign(self):
	# 	super(StockMove,self)._action_assign()		

	# Overrides th create Quality Checks for the Following
	def _create_quality_checks(self):
		# Used to avoid duplicated quality points
		quality_points_list = set([])

		pick_moves = defaultdict(lambda: self.env['stock.move'])
		for move in self:
			pick_moves[move.picking_id] |= move

		for picking, moves in pick_moves.items():
			for check in picking.sudo().check_ids:
				point_key = (check.picking_id.id, check.point_id.id, check.team_id.id, check.product_id.id)
				quality_points_list.add(point_key)
			quality_points = self.env['quality.point'].sudo().search([
				('picking_type_id', '=', picking.picking_type_id.id),
				'|', ('product_id', 'in', moves.mapped('product_id').ids),
				'&', ('product_id', '=', False), ('product_tmpl_id', 'in', moves.mapped('product_id').mapped('product_tmpl_id').ids)])
			for point in quality_points:
				if point.check_execute_now():
					if point.product_id:
						point_key = (picking.id, point.id, point.team_id.id, point.product_id.id)
						if point_key in quality_points_list:
							continue
						self.env['quality.check'].sudo().create({
							'picking_id': picking.id,
							'point_id': point.id,
							'team_id': point.team_id.id,
							'product_id': point.product_id.id,
							'company_id': picking.company_id.id,
							'is_create_from_po_so': True,
						})
						quality_points_list.add(point_key)
					else:
						products = picking.move_lines.filtered(lambda move: move.product_id.product_tmpl_id == point.product_tmpl_id).mapped('product_id')
						for product in products:
							point_key = (picking.id, point.id, point.team_id.id, product.id)
							if point_key in quality_points_list:
								continue
							self.env['quality.check'].sudo().create({
								'picking_id': picking.id,
								'point_id': point.id,
								'team_id': point.team_id.id,
								'product_id': product.id,
								'company_id': picking.company_id.id,
								'is_create_from_po_so': True,
							})
							quality_points_list.add(point_key)

class StockMoveLine(models.Model):
	_inherit = 'stock.move.line'

	@api.model
	def create(self, values):
		res = super(StockMoveLine, self).create(values)
		#Search For Quality Alert if there is already been a Quality Check
		if res:
			pick_obj = res.move_id and res.move_id.picking_id
			picking_id = res.move_id and res.move_id.picking_id and res.move_id.picking_id.id or False
			if picking_id:
				quality_check_obj = self.env['quality.check'].search([('is_create_from_po_so','=', True),('picking_id','=', picking_id)])
				if quality_check_obj:
					for qty in quality_check_obj:
						if qty.stock_move_line_id:
							for x in quality_check_obj:
								if x.stock_move_line_id:
									for y in x.stock_move_line_id:
										y = res.id

						# for qca in quality_check_obj:
						# 	qca.stock_move_line_id = res.id
						# return  res
			#Create a New QAC when product of the Movelines is for QAC first.
			quality_points = self.env['quality.point'].sudo().search([
				('picking_type_id', '=', pick_obj.picking_type_id.id),
				'|', ('product_id', 'in', res.mapped('product_id').ids),
				'&', ('product_id', '=', False), ('product_tmpl_id', 'in', res.mapped('product_id').mapped('product_tmpl_id').ids)])
			for point in quality_points:
				if point.check_execute_now():
					if point.product_id:
						self.env['quality.check'].sudo().create({
						    'picking_id': picking_id,
						    'point_id': point.id,
						    'team_id': point.team_id.id,
						    'product_id': point.product_id.id,
						    'company_id': pick_obj.company_id.id,
						    'stock_move_line_id': res.id,
						})
					#else:
					#	products = picking_id.move_lines.filtered(lambda res: move.product_id.product_tmpl_id == point.product_tmpl_id).mapped('product_id')
			return res
