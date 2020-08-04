# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

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

class salesdp(models.Model):
    _inherit = 'sale.order.line'
    
    product_uom_qty = fields.Float(digits=dp.get_precision('Sale Order Quantity'))
    qty_invoiced = fields.Float(digits=dp.get_precision('Sale Order Quantity'))
    
class salesinvdp(models.Model):
    _inherit = 'account.invoice.line'
    
    quantity = fields.Float(digits=dp.get_precision('Sale Order Quantity'))