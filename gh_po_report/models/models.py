# # -*- coding: utf-8 -*-
from odoo import models, fields, api

class ghporeport(models.Model):
    _inherit = 'purchase.order'
    
    del_instructions = fields.Text()
    approved_by = fields.Char()
    verified_by = fields.Char()
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
        
    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
                self.verified_by = self.env.user.name
            else:
                order.write({'state': 'to approve'})
                self.verified_by = self.env.user.name
        return True
        
    @api.multi
    def button_approve(self, force=False):
        self.write({'state': 'purchase'})
        self.approved_by = self.env.user.name
        self._create_picking()
        if self.company_id.po_lock == 'lock':
            self.write({'state': 'done'})
        return {}

    @api.multi
    def get_bom_details_summary(self):
        if self.order_line: 
            product_bom_list = {}
            for order_line_id in self.order_line:
                bom_obj = self.env['mrp.bom'].search([('product_tmpl_id','=', order_line_id.product_id.product_tmpl_id.id),
                                                      ('company_id','=', self.company_id.id),
                                                      ('type','=', 'phantom')], limit=1)
                if bom_obj:
                    quantity_converted = order_line_id.product_qty / bom_obj.product_qty
                    bom_ctr = 1

                    for line_id in bom_obj.bom_line_ids:
                        if line_id.id != bom_obj.bom_line_ids.ids[0]:

                            names = str(line_id.product_id.id) + 'UOM' + str(line_id.product_uom_id.id)
                            product_name =  line_id.product_id.name

                            if line_id.product_id.description_sale:
                                product_name = line_id.product_id.description_sale

                            if names not in product_bom_list:
                                product_bom_list[names] = [
                                    product_name,
                                    line_id.product_uom_id,
                                    quantity_converted * line_id.product_qty]
                            else:
                                product_bom_list[names][2] += (quantity_converted * line_id.product_qty)
                            bom_ctr +=1
            return product_bom_list
        return False

class purchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def get_product_bom_details(self):
        self.ensure_one()
        bom_obj = self.env['mrp.bom'].search([('product_tmpl_id','=', self.product_id.product_tmpl_id.id),
                                         ('company_id','=', self.company_id.id),
                                         ('type','=', 'phantom')], limit=1)
        if bom_obj:

            #raise Warning(bom_obj.bom_line_ids[1:])
            return bom_obj.bom_line_ids[0]

        return False
