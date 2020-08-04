# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
import time
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
from odoo.addons import decimal_precision as dp
import logging
import pytz
_logger = logging.getLogger(__name__)



class manufacturingRequest(models.Model):
	_name = 'omni.gh.sale.manufacturing'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Manufacturing Request"
	_order = 'date_needed desc, id desc'

	name = fields.Char('Purchase Request No', required=True, index=True, copy=False, default='New')
	date_needed = fields.Date('Date Needed')
	remarks = fields.Text('Remarks')
	state = fields.Selection([
		('draft', 'Draft MR'),
		('modification', 'For MR Modification'),
		('sent', 'MR Submitted'),
		('done', 'MR Approved'),
		('cancel', 'MR Cancelled')
		], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
	mr_ref = fields.Char('MO#', index=True)
	sale_manufacturing_line = fields.One2many('omni.gh.sale.manufacturing.line', 'sale_manufacturing_id', 
		string='Requests Lines', copy=True)
	start_dt = fields.Datetime(string="Start shift")
	end_dt = fields.Datetime(string='End shift')
	equipments = fields.Many2one('maintenance.equipment', 'Equipment')
	production_schedule_count = fields.Integer(string='# of Production Schedule', compute='_get_production_schedule_count', readonly=True)


	# @api.depends('state','done')
	def _get_production_schedule_count(self):
		production_schedule = self.env['omni.gh.production.schedule']
		data = production_schedule.search([('sale_manufacturing','=',self.id)])

		count = 0
		if data:
			for x in data:
				count += 1;

		self.update({
			'production_schedule_count': count
			})
		# raise Warning(count)

	@api.multi
	def action_view_production_schedule(self):
		production_schedule = self.env['omni.gh.production.schedule']
		data = production_schedule.search([('sale_manufacturing','=',self.id)])
		action = self.env.ref('omni_gh_production_schedule.action_mrp_production_schedule').read()[0]
		if len(data) > 1:
			action['domain'] = [('id', 'in', data.ids)]
		elif len(data) == 1:
			action['views'] = [(self.env.ref('omni_gh_production_schedule.mrp_production_schedule_form').id, 'form')]
			action['res_id'] = data.ids[0]
		else:
			action = {'type': 'ir.actions.act_window_close'}
		return action

	@api.model
	def create(self, vals):
		getTotalSM = self.env['omni.gh.sale.manufacturing'].search([])
		getTotalSM = len(getTotalSM) + 1
		if vals.get('name', 'New') == 'New':
			vals['name'] = 'SM/' + str(getTotalSM)
		return super(manufacturingRequest, self).create(vals)

	@api.multi
	def write(self, vals):
		return super(manufacturingRequest, self).write(vals)

	@api.one
	def submit_mr(self):
		self.write({'state':'sent'})

	@api.one
	def modify_mr(self):
		self.write({'state':'modification'})

	@api.one
	def approved_mr(self):
		self.write({'state':'done'})

		production_schedule = self.env['omni.gh.production.schedule']


		if self.sale_manufacturing_line:
			for x in self.sale_manufacturing_line:
				production_schedule.create({
					'name': self.name + ' ' + x.product_id.name,
					'start_dt': self.start_dt,
					'end_dt': self.end_dt,
					'equipments': self.equipments.id,
					'product_id': x.product_id.id,
					'description': self.remarks,
					'sale_manufacturing': self.id
					})

	@api.one
	def cancelled_mr(self):
		self.write({'state':'cancel'})


class manufacturingRequestLine(models.Model):
	_name = 'omni.gh.sale.manufacturing.line'
	_description = "Sale Manufacturing Request Lines"


	sale_manufacturing_id = fields.Many2one('omni.gh.sale.manufacturing', string='Requests Reference', required=True, ondelete='cascade', index=True, copy=False)
	product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict', required=True)
	product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
	product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)