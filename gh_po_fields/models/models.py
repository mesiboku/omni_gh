# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime

# class goodheart(models.Model):
#     _name = 'goodheart.goodheart'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class pofields(models.Model):
    _inherit = 'purchase.order'

    attention = fields.Char(string='Attention')
    remarks = fields.Char(string='Remarks')
    del_instructions = fields.Text(string='Del. Instruction', store='True')
    state = fields.Selection([
        ('draft', "RFQ"),
        ('sent', "RFQ Sent"),
        ('to approve', "To Approve"),
        ('purchase', "Purchase Order"),
        ('done', "Locked"),
        ('cancel', "Cancelled")
    ], default='draft')

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_sent(self):
        self.state = 'sent'

    @api.multi
    def action_to_approve(self):
        self.state = 'to approve'

    @api.multi
    def action_purchase(self):
        self.state = 'purchase'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'


class customerinvoice(models.Model):
    _inherit = 'account.invoice'

    legacy_invoice = fields.Char(string="Legacy Invoice #", track_visibility='onchange')
    business_style = fields.Char(string="Business Style")
    tin_number = fields.Char(string="TIN")
    store_number = fields.Char(string="Store No.")
    store_name = fields.Char(string="Store Name")
    received_by = fields.Char(string="Received By")
    po_number = fields.Char(string="PO Number")
    date_received = fields.Char(string="Date Received")

class vendorbills(models.Model):
    _inherit = 'account.invoice'

    delivery_date = fields.Char(string="Delivery Date")
    dr_number = fields.Char(string="DR No.")
    bank = fields.Char(string="Bank")
    check_number = fields.Char(string="Check No.")
    received_payment_by = fields.Char(string="Received Payment By")
    date_received = fields.Char(string="Date Received")
    prepared_by = fields.Char(string="Prepared By")
    certified_correct_by = fields.Char(string="Certified Correct By")
    approved_by = fields.Char(string="Approved By")
    recommended_by = fields.Char(string="Recommended By")

class payments(models.Model):
    _inherit = 'account.payment'

    bank = fields.Char(string="Bank")
    branch = fields.Char(string="Branch")
    check_number = fields.Char(string="Check Number")