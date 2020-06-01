# -*- coding: utf-8 -*-

from collections import namedtuple
import json
import time

from itertools import groupby
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter
import logging
_logger = logging.getLogger(__name__)



class stockPutInPack(models.Model):
	_inherit = 'stock.picking'

	start_box_number = fields.Integer('Start Box #.', store=True)
	done_qty_per_box = fields.Integer('units/pack', store=True)

	def _put_in_pack_auto(self):
		package = False
		if self.done_qty_per_box > 0:
			for pick in self.filtered(lambda p: p.state not in ('done', 'cancel')):
				operations = pick.move_line_ids.filtered(lambda o: not o.result_package_id)
				operation_ids = self.env['stock.move.line']
				if operations:
					package = self.env['stock.quant.package'].create({})
					# raise Warning(package.name)
					box_number = self.start_box_number
					for operation in operations:
						operation.write({
							'qty_done': self.done_qty_per_box
							})
						if float_compare(operation.qty_done, operation.product_uom_qty, precision_rounding=operation.product_uom_id.rounding) >= 0:
							operation_ids |= operation
						else:
							# raise Warning(float_compare(operation.qty_done, operation.product_uom_qty, precision_rounding=operation.product_uom_id.rounding))
							quantity_left_todo = float_round(
								operation.product_uom_qty - operation.qty_done,
								precision_rounding=operation.product_uom_id.rounding,
								rounding_method='UP')
							done_to_keep = operation.qty_done
							new_operation = operation.copy(
								default={'product_uom_qty': 0, 'qty_done': operation.qty_done})
							operation.write({'product_uom_qty': quantity_left_todo, 'qty_done': 0.0})
							new_operation.write({'product_uom_qty': done_to_keep, 'box_number': box_number})
							operation_ids |= new_operation
							box_number = box_number + 1

					operation_ids.write({'result_package_id': package.id})
				else:
					raise UserError(_('Please process some quantities to put in the pack first!'))
		else:
			raise UserError(_('Pcs/Box must be non-zero.'))
		return package


	def put_in_pack_auto(self):
		package = False
		if self.done_qty_per_box > 0:
			for pick in self.filtered(lambda p: p.state not in ('done', 'cancel')):
				operations = pick.move_line_ids.filtered(lambda o: not o.result_package_id)
				get_resrv_goods = 0
				for operation in operations:
					get_resrv_goods = operation.product_uom_qty
				total_box = int(get_resrv_goods / self.done_qty_per_box)

				# raise Warning(pick.move_line_ids)
				for x in range(total_box):
					package = self._put_in_pack_auto()

				box_number = self.start_box_number
				for op in pick.move_line_ids:
					op.write({
						'box_number': box_number
						})
					for package in op.result_package_id:
						package.write({
							'name': str(op.lot_id.name) + '-' + str(box_number)
							})
					box_number = box_number + 1
					
		else:
			raise UserError(_('Pcs/Box must be non-zero.'))
		return package




class stockMoveLineBoxNumber(models.Model):
	_inherit = 'stock.move.line'

	box_number = fields.Integer('Box #')

	@api.onchange('package_id')
	def onChangePackageId(self):
		find_result_package_id = self.env['stock.move.line'].search([('result_package_id','in', self.package_id.ids)], limit=1)
		if find_result_package_id:
			for x in find_result_package_id:
				self.box_number = x.box_number
		# raise Warning(find_result_package_id)
