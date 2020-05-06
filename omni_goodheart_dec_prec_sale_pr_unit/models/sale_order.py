# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp

class sale_order(models.Model):
    _inherit = 'sale.order.line'
    
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Sale Order Line Price Unit'), default=0.0)