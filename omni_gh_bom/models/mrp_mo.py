from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
import logging
_logger = logging.getLogger(__name__)

class mrpMO(models.Model):
	_inherit = 'mrp.production'

	@api.model
	def create(self,vals):

		res = super(mrpMO, self).create(vals)

		if res:
			for mo in res:
				for move_raw in mo.move_raw_ids:
					for bom in mo.bom_id.bom_line_ids:
						# _logger.info("PRODUCT NAME: " + str(move_raw.product_id.name))
						# _logger.info("PRODUCT: " + str(move_raw.product_id.id == bom.product_id.id))
						if move_raw.product_id.id == bom.product_id.id:
							# _logger.info("PRODUCT IS TRUE: " + str(move_raw.product_id.id == bom.product_id.id))
							# _logger.info("BOM PRODUCT IS TRUE: " + str(bom.product_id.name))
							# _logger.info("BOM ROUND: " + str(bom.round_up))
							if str(bom.round_up_checkbox) == str(True):
								_logger.info("PRODUCT IS TRUE: " + str(move_raw.product_id.id == bom.product_id.id) +
									"\nBOM PRODUCT IS TRUE: " + str(bom.product_id.name) +
									"\nBOM ROUND TRUE: " + str(str(bom.round_up_checkbox) == str(True)))
								# data1 = round(move_raw.product_uom_qty)
								# _logger.info("BOM PRODUCT IS TRUE: " + str(bom.product_id.name))
								# _logger.info("BOM ROUND TRUE: " + str(str(bom.round_up) == str(True)))
								move_raw.write({
									'round_up': bom.round_up_checkbox
									})

		# raise Warning(res)
		return res
