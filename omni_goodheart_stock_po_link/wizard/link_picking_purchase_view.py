from odoo import models, fields, api

from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class LinkPickingPurchase(models.TransientModel):
	_name = 'link.picking.purchase'

	def _default_picking(self):
		return self.env['stock.picking'].browse(self._context.get('active_id'))

	picking_id = fields.Many2one('stock.picking', string='Picking', default=_default_picking)
	purchase_ids = fields.Many2many('purchase.order', string='Purchase')


	# @api.multi
	def apply(self):
		# self.purchase_id.invoice_ids |= self.invoice_ids
		# return {}

		if not self.purchase_ids:
			raise UserError("You must select at least one purchase to link to this purchase order.")

		for purchase in self.purchase_ids:

			if purchase.partner_id != self.picking_id.partner_id:
				raise UserError("Picking and purchase vendor must be the same.")

			for purchase_lines in purchase.order_line:
				for move_lines in self.picking_id.move_lines:
					# Check if line items match
					if purchase_lines.product_id == move_lines.product_id and purchase_lines.product_uom == move_lines.product_uom:
						move_lines.write({'purchase_line_id': purchase_lines.id})
