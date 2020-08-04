# -*- coding: utf-8 -*-
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
from odoo import fields, api, models

class purchaseformat(models.Model):
    _inherit = 'purchase.order.line'

    discount = fields.Float(string='Discount')

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * (1 + (line.discount or 0.0) / 100.0)
            taxes = line.taxes_id.compute_all(price,
                                                line.order_id.currency_id,
                                                line.product_qty,
                                                product=line.product_id,
                                                partner=line.order_id.partner_id,)

            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                })
            # return super(purchaseformat, self)._compute_amount(self)

class purchaseformattotaldiscount(models.Model):
    _inherit = 'purchase.order'

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.currency_id.round(amount_untaxed),
                'amount_tax': order.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
            })
            # return super(purchaseformattotaldiscount, self)._amount_all()