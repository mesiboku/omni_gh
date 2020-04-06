# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError
from odoo.tools.misc import formatLang

import logging
_logger = logging.getLogger(__name__)

class accountInvoice(models.Model):
	_inherit = 'account.invoice'

	store_number = fields.Char('Store No.', compute="_compute_store_number")

	# @api.depends('partner_shipping_id')
	def _compute_store_number(self):
		for invoice in self:
			invoice.store_number = invoice.partner_shipping_id.name

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	store_number = fields.Char('Store No.', compute="_compute_store_number")

	# @api.depends('invoice_id.store_number')
	def _compute_store_number(self):
		for line in self:
			if line.invoice_id:
				line.store_number = line.invoice_id.store_number


	@api.multi
	def prepare_move_lines_for_reconciliation_widget(self, target_currency=False, target_date=False):
		""" Returns move lines formatted for the manual/bank reconciliation widget

			:param target_currency: currency (Model or ID) you want the move line debit/credit converted into
			:param target_date: date to use for the monetary conversion
		"""
		context = dict(self._context or {})
		ret = []

		if target_currency:
			# re-browse in case we were passed a currency ID via RPC call
			target_currency = self.env['res.currency'].browse(int(target_currency))

		for line in self:
			company_currency = line.account_id.company_id.currency_id
			line_currency = (line.currency_id and line.amount_currency) and line.currency_id or company_currency
			ret_line = {
				'id': line.id,
				'name': line.name and line.name != '/' and line.move_id.name + ': ' + line.name or line.move_id.name,
				'ref': line.move_id.ref or '',
				# For reconciliation between statement transactions and already registered payments (eg. checks)
				# NB : we don't use the 'reconciled' field because the line we're selecting is not the one that gets reconciled
				'account_id': [line.account_id.id, line.account_id.display_name],
				'already_paid': line.account_id.internal_type == 'liquidity',
				'account_code': line.account_id.code,
				'account_name': line.account_id.name,
				'account_type': line.account_id.internal_type,
				'date_maturity': line.date_maturity,
				'date': line.date,
				'journal_id': [line.journal_id.id, line.journal_id.display_name],
				'partner_id': line.partner_id.id,
				'partner_name': line.partner_id.name,
				'currency_id': line_currency.id,
				'store_number': line.store_number,
			}

			debit = line.debit
			credit = line.credit
			amount = line.amount_residual
			amount_currency = line.amount_residual_currency

			# For already reconciled lines, don't use amount_residual(_currency)
			if line.account_id.internal_type == 'liquidity':
				amount = abs(debit - credit)
				amount_currency = abs(line.amount_currency)

			# Get right debit / credit:
			target_currency = target_currency or company_currency
			amount_currency = debit - credit
			amount_currency_str = ""
			total_amount_currency_str = ""
			if line_currency != company_currency and target_currency == line_currency:
				# The payment currency is the invoice currency, but they are different than the company currency
				# We use the `amount_currency` computed during the invoice validation, at the invoice date
				# to avoid exchange gain/loss
				# e.g. an invoice of 100€ must be paid with 100€, whatever the company currency and the exchange rates
				total_amount = line.amount_currency
				actual_debit = debit > 0 and amount_currency or 0.0
				actual_credit = credit > 0 and -amount_currency or 0.0
				currency = line_currency
			else:
				# Either:
				#  - the invoice, payment, company currencies are all the same,
				#  - the payment currency is the company currency, but the invoice currency is different,
				#  - the invoice currency is the company currency, but the payment currency is different,
				#  - the invoice, payment and company currencies are all different.
				# For the two first cases, we can simply use the debit/credit of the invoice move line, which are always in the company currency,
				# and this is what the target need.
				# For the two last cases, we can use the debit/credit which are in the company currency, and then change them to the target currency
				total_amount = abs(debit - credit)
				actual_debit = debit > 0 and amount or 0.0
				actual_credit = credit > 0 and -amount or 0.0
				currency = company_currency

			if line_currency != target_currency:
				amount_currency = target_currency.compute(total_amount, line_currency)
				amount_currency_str = formatLang(self.env, abs(amount_currency), currency_obj=line_currency)
				total_amount_currency_str = formatLang(self.env, target_currency.compute(total_amount, line_currency), currency_obj=line_currency)
			if currency != target_currency:
				ctx = context.copy()
				ctx.update({'date': target_date or line.date})
				total_amount = currency.with_context(ctx).compute(total_amount, target_currency)
				actual_debit = currency.with_context(ctx).compute(actual_debit, target_currency)
				actual_credit = currency.with_context(ctx).compute(actual_credit, target_currency)
			amount_str = formatLang(self.env, abs(actual_debit or actual_credit), currency_obj=target_currency)
			total_amount_str = formatLang(self.env, total_amount, currency_obj=target_currency)

			ret_line['debit'] = abs(actual_debit)
			ret_line['credit'] = abs(actual_credit)
			ret_line['amount_str'] = amount_str
			ret_line['total_amount_str'] = total_amount_str
			ret_line['amount_currency_str'] = amount_currency_str
			ret_line['amount_currency'] = amount_currency
			ret_line['total_amount_currency_str'] = total_amount_currency_str
			ret.append(ret_line)
		return ret
