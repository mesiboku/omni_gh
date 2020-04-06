# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
# if use relativedelta 
from dateutil.relativedelta import relativedelta 
# from dateutil.parser import parser
import time
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
import fnmatch
from odoo.addons import decimal_precision as dp
import pytz
import logging
_logger = logging.getLogger(__name__)
from odoo.exceptions import UserError, ValidationError

# class omni_gh_mo(models.Model):
#     _name = 'omni_gh_mo.omni_gh_mo'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100




class manPowerTracking(models.Model):
	_name = 'omni.gh.manpower.tracking'
	
	_description = 'Manpower Tracking'


	@api.model
	def create(self, vals):

		res = super(manPowerTracking, self).create(vals)

		if res:
			if res.track_shifts:
				manpower = self.env['omni.gh.manpower.operator']

				for data in res.track_shifts.schedule_sheets_draft:
					manpower.create({
						'mp_role': data.mp_role.id,
						'mp_equipment': data.mp_equipment.id,
						# 'mp_operator': data.mp_operator.id,
						'manpower': res.id
						})

		return res


	@api.multi
	def write(self, vals):
		
		res = super(manPowerTracking, self).write(vals)

		return res



	@api.onchange('track_shifts')
	def onchange_shift(self):
		if self:
			if self.track_shifts:
				self.update({
						'start_dt': self.track_shifts.start_dt,
						'end_dt': self.track_shifts.end_dt
						})



	name = fields.Char('Shift Name', default=lambda x: _('New'))
	track_dt = fields.Date(string = 'Track Date', required = True)
	start_dt = fields.Float(string="Start shift")
	end_dt = fields.Float(string='End shift')
	# track_shifts = fields.Selection([
	# 	('s1','Shift 1'),
	# 	('s2','Shift 2'),
	# 	('s3','Shift 3')], string='Shifts',
	# 	copy=False, default='s1', track_visibility='onchange')
	track_shifts = fields.Many2one('omni.gh.manpower.shifts','Shift Template')
	schedule_sheets = fields.One2many('omni.gh.manpower.operator','manpower', string = 'Manpower Tracking')


class manpowerOperator(models.Model):
	_name = 'omni.gh.manpower.operator'

	mp_role	= fields.Many2one('omni.gh.list.role', string = 'Roles')

	mp_equipment = fields.Many2one('maintenance.equipment', 'Equipment')

	mp_operator = fields.Many2one('omni.gh.list.operator', string='Operator')

	manpower = fields.Many2one('omni.gh.manpower.tracking','Manpower', readonly=True)

	manpower_draft = fields.Many2one('omni.gh.manpower.shifts','Manpower', readonly=True)


class operators(models.Model):
	_name = 'omni.gh.list.operator'


	name = fields.Char('Full name')

	status = fields.Selection([
		('A','Active'),
		('I','Inactive')], string='Status', default='A')

class manpowerRole(models.Model):
	_name = 'omni.gh.list.role'

	name = fields.Char('Role name')

	code = fields.Char('Role code', size=5)

class manpowerShifts(models.Model):
	_name = 'omni.gh.manpower.shifts'

	name = fields.Char('Shift Name', default=lambda x: _('New Shift'))
	start_dt = fields.Float(string="Start shift")
	end_dt = fields.Float(string='End shift')
	schedule_sheets_draft = fields.One2many('omni.gh.manpower.operator','manpower_draft', string = 'Manpower Tracking')