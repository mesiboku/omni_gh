from odoo import api, fields, models, _

class UniqueDR(models.Model):
    _inherit = 'stock.picking'

    sup_delivery_receipt_new = fields.Char('Sales Delivery Receipt No.')

    _sql_constraints = [
        ('sup_delivery_receipt_new', 'unique(sup_delivery_receipt_new)', 'Sales DR No duplicates are not allowed. Please use another Sales DR No.')
    ]
