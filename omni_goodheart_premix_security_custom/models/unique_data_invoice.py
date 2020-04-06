from odoo import api, fields, models, _

class UniqueLegacyNumber(models.Model):
    _inherit = "account.invoice"

    _sql_constraints = [
        ('legacy_invoice_unique', 'unique(legacy_invoice)', 'Duplicate Exists')
    ]

class StateInvoice(models.Model):
    _inherit = "account.invoice"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

#     @api.one
#     def action_invoice_open(self):
#         self.write({'state': 'open'})
#         return True
