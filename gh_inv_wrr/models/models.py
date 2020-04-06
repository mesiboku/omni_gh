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
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class wrrvalues(models.Model):
    _inherit = 'stock.move.line'

    currency_id = fields.Many2one(related='purchase_line_move_id.currency_id')
    wrr_taxes_id = fields.Many2many(compute='onchange_taxes', related='purchase_line_move_id.taxes_id')
    wrr_price_unit = fields.Float(related='purchase_line_move_id.price_unit')
    wrr_price_subtotal = fields.Float(compute='_wrr_compute_amount')
    wrr_price_total = fields.Float(compute='_wrr_compute_amount')
    wrr_price_tax = fields.Float(compute='_wrr_compute_amount')
    purchase_quantity_done = fields.Float(related='move_id.purchase_quantity_done')
    discount = fields.Float(related='purchase_line_move_id.discount')

    @api.depends('purchase_quantity_done', 'wrr_price_unit', 'wrr_taxes_id', 'discount')
    def _wrr_compute_amount(self):
        for line in self:
            price = line.wrr_price_unit * (1 + (line.discount or 0.0) / 100.0)
            wrr_taxes = line.wrr_taxes_id.compute_all(price,
                                                    line.currency_id,
                                                    line.purchase_quantity_done,
                                                    product=line.product_id,
                                                    partner=None,)
            line.update({
                'wrr_price_tax': sum(w.get('amount', 0.0) for w in wrr_taxes.get('taxes', [])),
                'wrr_price_total': wrr_taxes['total_included'],
                'wrr_price_subtotal': wrr_taxes['total_excluded'],
            })

    @api.onchange('wrr_taxes_id')
    def onchange_taxes(self):
        for line in self:
            self.wrr_taxes_id = self.wrr_taxes_id.name.strip() + "   "

class wrrvaluessumline(models.Model):
    _inherit = 'stock.picking'

    currency_id = fields.Many2one(related='purchase_id.currency_id')
    wrr_total = fields.Monetary(string='Current Total', compute='_amount_all_wrr')
    wrr_untaxed_amount = fields.Monetary(compute='_amount_all_wrr')
    wrr_tax = fields.Monetary(compute='_amount_all_wrr')

    sup_delivery_receipt = fields.Char('Delivery Receipt Number')

    _sql_constraints = [
        ('sup_delivery_receipt_unique', 'unique(sup_delivery_receipt)', 'Data Exist')
    ]

    @api.depends('move_lines.move_line_ids.wrr_price_total')
    def _amount_all_wrr(self):
        for picking in self:
            wrr_untaxed_amount = wrr_tax = 0.0
            for line in picking.move_lines:
                for move_line_id in line.move_line_ids:
                    wrr_untaxed_amount += move_line_id.wrr_price_subtotal
                    wrr_tax += move_line_id.wrr_price_tax
            picking.update({
                'wrr_untaxed_amount': picking.currency_id.round(wrr_untaxed_amount),
                'wrr_tax': picking.currency_id.round(wrr_tax),
                'wrr_total': wrr_untaxed_amount + wrr_tax,
            })

    @api.multi
    def generateDelvRecptReport(self):
        self.ensure_one()
        if self.state != 'done':
            raise UserError(_('Printing is not allowed. Please make the Transfer Status as Done before printing.'))
        return self.env.ref('gh_inv_wrr.goodheart_wrr_half').report_action(self)
