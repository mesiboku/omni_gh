# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
import xlwt 
import xlrd
import datetime
import base64
import os, sys
_logger = logging.getLogger(__name__)
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


NUMBER_OF_RECORDS_PER_PAGE = 15.00

class GHCallSheet(models.TransientModel):
	_name = 'seven_call_sheet.call_sheet_wiz'

	coll_sheet_id  = fields.Many2one('seven_call_sheet.call_sheet', string='Call Sheet')	
	coll_sheet_file_import = fields.Binary(string='Collection Sheet Excel', required=True)
	coll_sheet_export_file_name = fields.Char('Call Sheet Template.xls', compute='_getFilename')
	coll_sheet_file_export = fields.Binary(string='Collection Sheet Excel Template', default=lambda self:self._get_default_file(),attachment=True)

	@api.one
	def _getFilename(self):
		raise Warning(11)
		self.coll_sheet_export_file_name =  'Call Sheet Template.xls'

	@api.model
	def _get_default_file(self):
		addons_paths = tools.config['addons_path']
		addons_lists = addons_paths.split(',')
		xls_dir_path = ""
		if os.path.isdir('/odoo/TemporaryFiles'):
			xls_dir_path = '/odoo/TemporaryFiles'
		else:
			for addons_list in addons_lists:
				if os.path.isdir(addons_list + '/seven_call_sheet'):
					xls_dir_path = addons_list + '/seven_call_sheet'
					break
		FILENAME = xls_dir_path + '/call_sheet_template.xls'

		#FILENAME = '/odoo/TemporaryFiles/call_sheet_template.xls'	
		with open(FILENAME, "rb") as file:
			return base64.b64encode(file.read())


	@api.one
	def createCallSheetLine(self):
		call_sheet_obj = self.env['seven_call_sheet.call_sheet'].browse(self._context.get('active_ids', []))
		if call_sheet_obj:
			call_sheet_obj.write({
					'coll_sheet_file_import': self.coll_sheet_file_import,})			

			call_sheet_obj.generateCollSheetRecord()

		return True