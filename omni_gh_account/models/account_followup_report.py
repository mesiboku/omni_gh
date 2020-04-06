# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
from odoo.tools.misc import formatLang, format_date
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class report_account_followup_report(models.AbstractModel):
	_inherit = "account.followup.report"

	def get_columns_name(self, options):
		headers = [{}, 
				{'name': _(' Store # '), 'style': 'text-align:center;'}, 
				{'name': _(' Date '), 'class': 'date', 'style': 'text-align:center;'}, 
				{'name': _(' Due Date '), 'class': 'date', 'style': 'text-align:center;'}, 
				{'name': _('Communication'), 'style': 'text-align:right;'}, 
				{'name': _(' Expected Date '), 'class': 'date'}, 
				{'name': _(' Excluded '), 'class': 'date'}, 
				{'name': _(' Total Due '), 'class': 'number', 'style': 'text-align:right;'}
				]
		if self.env.context.get('print_mode'):
			headers = headers[:4] + headers[6:]
		return headers

	def get_lines(self, options, line_id=None):
		# Get date format for the lang
		partner = options.get('partner_id') and self.env['res.partner'].browse(options['partner_id']) or False
		if not partner:
			return []
		lang_code = partner.lang or self.env.user.lang or 'en_US'

		lines = []
		res = {}
		today = datetime.today().strftime('%Y-%m-%d')
		line_num = 0
		for l in partner.unreconciled_aml_ids:
			if self.env.context.get('print_mode') and l.blocked:
				continue
			currency = l.currency_id or l.company_id.currency_id
			if currency not in res:
				res[currency] = []
			res[currency].append(l)
		for currency, aml_recs in res.items():
			total = 0
			total_issued = 0
			aml_recs = sorted(aml_recs, key=lambda aml: aml.blocked)
			for aml in aml_recs:
				amount = aml.currency_id and aml.amount_residual_currency or aml.amount_residual
				date_due = format_date(self.env, aml.date_maturity or aml.date, lang_code=lang_code)
				total += not aml.blocked and amount or 0
				is_overdue = today > aml.date_maturity if aml.date_maturity else today > aml.date
				is_payment = aml.payment_id
				if is_overdue or is_payment:
					total_issued += not aml.blocked and amount or 0
				if is_overdue:
					date_due = {'name': date_due, 'class': 'color-red date'}
				if is_payment:
					date_due = ''
				amount = formatLang(self.env, amount, currency_obj=currency)
				amount = amount.replace(' ', '&nbsp;') if self.env.context.get('mail') else amount
				line_num += 1
				# communication = "%s (%s)" % (aml.invoice_id.name or aml.name,aml.store_number)
				columns = [aml.store_number, format_date(self.env, aml.date, lang_code=lang_code), date_due, aml.invoice_id.name or aml.name, aml.expected_pay_date and aml.expected_pay_date +' '+ aml.internal_note or '', {'name': aml.blocked, 'blocked': aml.blocked}, amount]
				# columns = [format_date(self.env, aml.date, lang_code=lang_code), date_due, communication, aml.expected_pay_date and aml.expected_pay_date +' '+ aml.internal_note or '', {'name': aml.blocked, 'blocked': aml.blocked}, amount]
				if self.env.context.get('print_mode'):
					columns = columns[:3]+columns[5:]
				_logger.info("LOOOO")
				_logger.info(columns)
				lines.append({
					'id': aml.id,
					'name': aml.move_id.name,
					'caret_options': 'followup',
					'move_id': aml.move_id.id,
					'type': is_payment and 'payment' or 'unreconciled_aml',
					'unfoldable': False,
					'columns': [type(v) == dict and v or {'name': v} for v in columns],
				})
				# _logger.info([type(v) == dict and v or {'name': v} for v in columns])
			totalXXX = formatLang(self.env, total, currency_obj=currency)
			totalXXX = totalXXX.replace(' ', '&nbsp;') if self.env.context.get('mail') else totalXXX
			line_num += 1
			lines.append({
				'id': line_num,
				'name': '',
				'class': 'total',
				'unfoldable': False,
				'level': 0,
				'columns': [{'name': v} for v in ['']*(3 if self.env.context.get('print_mode') else 5) + [total >= 0 and _('Total Due') or '', totalXXX]],
			})
			# _logger.info([{'name': v} for v in ['']*(2 if self.env.context.get('print_mode') else 5) + [total >= 0 and _('Total Due') or '', totalXXX]])
			if total_issued > 0:
				total_issued = formatLang(self.env, total_issued, currency_obj=currency)
				total_issued = total_issued.replace(' ', '&nbsp;') if self.env.context.get('mail') else total_issued
				line_num += 1
				lines.append({
					'id': line_num,
					'name': '',
					'class': 'total',
					'unfoldable': False,
					'level': 0,
					'columns': [{'name': v} for v in ['']*(3 if self.env.context.get('print_mode') else 5) + [_('Total Overdue'), total_issued]],
				})
		return lines