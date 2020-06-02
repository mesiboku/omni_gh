# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
from math import floor
_logger = logging.getLogger(__name__)
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP


NUMBER_OF_RECORDS_PER_PAGE = 15.00

class GHCallSheet(models.Model):
	_inherit = 'seven_call_sheet.call_sheet'

	@api.multi
	def _group_by_invoice_ids(self, invoice_ids):
		self.ensure_one()
		pages = 15
		if invoice_ids:
			num_of_records = len(invoice_ids)
			total_number_of_pages = int(floor(num_of_records/NUMBER_OF_RECORDS_PER_PAGE))

			if total_number_of_pages ==0:
				total_number_of_pages +=1
			elif  (num_of_records/NUMBER_OF_RECORDS_PER_PAGE) % total_number_of_pages != 0.00000:
				total_number_of_pages +=1
			list_of_records_per_page = []

			for i in range(int(total_number_of_pages)):
				list_of_records_per_page.append([])

			invoice_number_increment = 1
			for invoice_id in invoice_ids:

				page_designation = int(floor(invoice_number_increment/ NUMBER_OF_RECORDS_PER_PAGE))
				
				if (invoice_number_increment/ NUMBER_OF_RECORDS_PER_PAGE) %  (page_designation +1) != 0.0:
					page_designation += 1
				_logger.info('TOTAL_NUMBER OF PAGES' + str(total_number_of_pages))
				_logger.info(page_designation)
				list_of_records_per_page[page_designation -1].append(invoice_id)
				invoice_number_increment +=1
			return list_of_records_per_page
		return False

	@api.multi
	def _get_call_sheet_line_via_invoice(self, callsheet_id ,invoice_id):
		self.ensure_one()
		call_sheet_line_obj = self.env['seven_call_sheet.call_sheet_line'].search([('invoice_id', '=', invoice_id),
																				   ('call_sheet_id', '=', callsheet_id)])
		if call_sheet_line_obj:
			return call_sheet_line_obj
		return False