# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SOWithRA(models.Model):
    _inherit = 'sale.order'
    received_ra = fields.Boolean(
        string='RA Received',
    )

    pending_ra = fields.Integer(
        string='No of pending RA for store',
        compute="_value_pending_ra"
    )

    @api.multi
    @api.depends('partner_shipping_id')
    def _value_pending_ra(self):
    	cnt = self.env['sale.order'].search_count([('partner_shipping_id','=',self.partner_shipping_id.id),
    		('state','=','sale'), ('received_ra','=',False)])
    	for rec in self:
    		rec.pending_ra = cnt

    state = fields.Selection(selection_add=[('hold', "Hold")])

    @api.multi
    def unhold_state(self):
        for rec in self:
            rec.state = 'draft'

    




# class gh_receiving_advice(models.Model):
#     _name = 'gh_receiving_advice.gh_receiving_advice'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100