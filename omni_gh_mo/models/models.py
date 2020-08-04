# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
import time
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
import logging
import pytz
_logger = logging.getLogger(__name__)

class mrpProduction(models.Model):
	_inherit = 'mrp.production'



	is_parent = fields.Boolean(default = True)
	is_child_generated = fields.Boolean(default = False)
	child_no = fields.Integer(string = 'No. of child')
	# child_ids = fields.Char()
	parent_id = fields.Many2one(
		'mrp.production', 'Parent of ',
		copy=False, index=True)
	children_ids = fields.One2many(
		'mrp.production', 'parent_id', 'Children')



	@api.multi
	def btn_generate_child(self, cr, default={}):


		if self:
			if str(self.is_parent) == 'True':
				data = []
				if self.child_no:

					if self.child_no > 0:

						mrp_data = self.env['mrp.production'].search([('id','=', self.id)])

						for x in range(self.child_no):


							mrp_prod = self.env['mrp.production']

							for production in self:
								mrp_data_1 = production.copy({
									# 'name': '/',
									'move_raw_ids':[],
									'finished_move_line_ids': [],
									'parent_id': production.id,
									'is_parent': False,
									'child_no': 0
									})
								mrp_data |= mrp_data_1
								# raise Warning(mrp_data_1)
							# raise Warning("ORIG: " + str(self.id) + " COPY: " + str(mrp_data.id))
							# self.children_ids.append(mrp_data.ids)


						self.write({
							'children_ids': str(data),
							'is_child_generated': True,
							})
					else:
						raise UserError(_("Please enter a valid Child no."))

				else:
					raise UserError(_("Please enter number of child"))

			else:
				raise UserError(_("This MO is not a Parent."))


	@api.model
	def create(self, vals):
		# raise Warning(vals['bom_id'])
		product_id = vals['product_id']
		findBOM = self.env['mrp.bom'].search([('product_tmpl_id.product_variant_ids','=', product_id)])
		# raise Warning(findBOM)
		# timezone = pytz.timezone('UTC')
		if len(findBOM) > 1:
			a = []
			b = 0
			if findBOM:
				for c in findBOM:
					a.append([c.id, []]) 
					if c.bom_line_ids:
						for d in c.bom_line_ids:

							findserial = self.env['stock.production.lot'].search([('product_id','=',d.product_id.id)])
							if findserial:
								for y in findserial:
									# _logger.info(y.name)
									a[b][1].append(y.id) 
					b = b + 1
			if a:
				bom_id = []
				# [[bom_id, [lot_id, lot_id]], [bom_id, [lot_id, lot_id]], [bom_id, [lot_id, lot_id]]]
				old_bom = []
				last_bom = 0
				last_create_date = datetime.today()
				for data in a:
					if data:
						# bom_id = data[0]
						findserial = self.env['stock.production.lot'].search([('id','in', data[1]),('product_qty','>',0)], order='create_date asc', limit=1)
						if findserial:
							if last_bom == 0:
								last_bom = data[0]
								last_create_date = findserial.create_date
							else:
								dt_1 = fields.Datetime.from_string(findserial.create_date)
								dt_2 = fields.Datetime.from_string(last_create_date)
								if dt_2.date() > dt_1.date():
									last_bom = data[0]
									last_create_date = findserial.create_date
				vals['bom_id'] = last_bom
				production = super(mrpProduction, self).create(vals)

		else:
			production = super(mrpProduction, self).create(vals)
		return production


	@api.multi
	def action_cancel(self):
		# raise Warning(self.name)
		findStockMove = self.env['stock.picking'].search([('origin','=', self.name)])

		res = super(mrpProduction, self).action_cancel()

		if findStockMove:
			findStockMove.action_cancel()
		return res
