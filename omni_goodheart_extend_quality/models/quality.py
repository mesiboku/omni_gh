# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
import random

from odoo import api, fields, models, _, SUPERUSER_ID

class QualityCheck(models.Model):
	_inherit= 'quality.check'


	quality_check_result = fields.Text(string="Results")
	stock_move_line_id = fields.Many2one('stock.move.line', string="Stock Move Lines")
	stock_move_line_lot_name = fields.Char(related ='stock_move_line_id.lot_name', string="Stock Move Lines Lot Number")
	stock_move_line_lot_name_2 = fields.Char(compute ='_get_lot_name', string="Stock Move Lines Lot Number")
	is_create_from_po_so = fields.Boolean(string='First Record', default=False)


	@api.depends('stock_move_line_id')
	def _get_lot_name(self):
		if self.stock_move_line_id.lot_id:
			self.stock_move_line_lot_name_2 = self.stock_move_line_id.lot_id.name
		else:
			self.stock_move_line_lot_name_2 = self.stock_move_line_id.lot_name
