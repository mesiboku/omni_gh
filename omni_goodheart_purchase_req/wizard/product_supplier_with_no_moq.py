from odoo import api, models, fields, _
from odoo.exceptions import UserError


class RepairCancel(models.TransientModel):
    _name = 'purchase.request.add.supplier'
    _description = 'Added new Supplier in Product'

    vendor_list = fields.Text('Vendor List')
    purchase_request_id = fields.Many2one('purchase.request', string="Purchase Request")

    
    def confirm_create_purchase_quotation(self):
        self.purchase_request_id.create_purchase_order()
        return {'type': 'ir.actions.act_window_close'}