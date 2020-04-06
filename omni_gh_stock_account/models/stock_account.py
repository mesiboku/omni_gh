# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero, pycompat

class StockMove(models.Model):
	_inherit = 'stock.move'

	@api.model
	def _run_fifo(self, move, quantity=None):
		#Override SUDO
		#Errors Found in CL/INT/00008
		#Creation of Record is in CL but the Destination location is GH		
		result = super(StockMove, self)._run_fifo(move.sudo(), quantity)
		return result