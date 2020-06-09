# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SalesArea(models.Model):
	_name = 'partner_seven_extension.sales_area'

	name = fields.Char(string='Area Name', size=64, required=True)

class SevenExtension(models.Model):
	_inherit = 'res.partner'

	store_manager = fields.Char(string='Store Manager (PSC Only)')
	store_number = fields.Char(string='Store Number')
	store_name = fields.Char(string='Store Name')
	globe_number = fields.Char(string='Globe Number')
	smart_number = fields.Char(string='Smart Number')
	sun_number = fields.Char(string='Sun Number')
	landline_number = fields.Char(string='Landline')
	area_id = fields.Many2one('partner_seven_extension.sales_area', string='Sales Area')
	store_status_note = fields.Char(string='Store Status Note')