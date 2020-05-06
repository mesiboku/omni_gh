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

class purchaseuom(models.Model):
    _inherit = 'purchase.order.line'
    
    product_qty = fields.Float(digits=dp.get_precision('Purchase Quantity'))