from odoo import api, fields, models, _


class StockPickingPaymentTerms(models.Model):
    _inherit = 'stock.picking'

    dr_payment_term_id = fields.Char('Payment Terms', compute = '_compute_get_payment_terms')
    dr_legacy_invoice = fields.Char('Legacy Invoice', compute = '_compute_get_legacy_invoice')
    dr_sale_note = fields.Char('Legacy Invoice', compute = '_compute_get_legacy_invoice')


    def _compute_get_payment_terms(self):
        if self:
            for record in self:
                find_sales = self.env['sale.order'].search([('picking_ids','=',record.id)])
                if find_sales:
                    for x in find_sales:
                        record.dr_payment_term_id = x.payment_term_id.name

    def _compute_get_legacy_invoice(self):
        if self:
            for stock in self:
                find_sales = self.env['sale.order'].search([('picking_ids','=',stock.id)])
                if find_sales:
                    for x in find_sales:
                        find_invoice = self.env['account.invoice'].search([('id','in',x.invoice_ids.ids)])
                        if find_invoice:
                            for invoice in find_invoice:
                                stock.dr_legacy_invoice = invoice.legacy_invoice
                    stock.dr_sale_note = x.note


class StockMoves(models.Model):
    _inherit = 'stock.move'

    @api.one
    def QuantityInSales(self):
        qty = 0.000
        move_line = self
        if move_line.sale_line_id:
            #Check if UOM type is  Bigger than the reference Unit of Measure
            if move_line.sale_line_id.product_uom.uom_type == 'bigger' and move_line.product_uom.uom_type == 'reference':
                qty = move_line.quantity_done /  move_line.sale_line_id.product_uom.factor_inv
            elif move_line.sale_line_id.product_uom.uom_type == 'reference' and move_line.product_uom.uom_type == 'bigger':
                qty = move_line.quantity_done *  move_line.product_uom.factor_inv
            else:
                qty = move_line.quantity_done
        else:
            qty = move_line.sale_line_id.price_unit
        return qty
