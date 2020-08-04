from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_is_zero, float_compare
from odoo.exceptions import UserError, AccessError
from odoo.tools.misc import formatLang
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.addons import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)




class PurchaseReques(models.Model):
    _name = "purchase.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Purchase Requisition"
    _order = 'date_needed desc, id desc'

    READONLY_STATES = {
        'sent': [('readonly', True)],
        'done': [('readonly', True)],
        'cancel': [('readonly', True)],
    }


    def _compute_purchase(self):
        for order in self:
            purchase = self.env['purchase.order'].search([('purchase_request_id', '=', order.id)])
            order.purchase_count = len(purchase)


    name = fields.Char('Purchase Request No', required=True, index=True, copy=False, default='New')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True, states=READONLY_STATES,\
        default=lambda self: self.env.user.company_id.currency_id.id)

    date_needed = fields.Date('Date Needed')
    remarks = fields.Text('Remarks')

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, states=READONLY_STATES, default=lambda self: self.env.user.company_id.id)

    partner_id = fields.Many2one('res.partner', string='Vendor', states=READONLY_STATES, change_default=True, track_visibility='always')


    state = fields.Selection([
        ('draft', 'Draft PR'),
        ('sent', 'PR Submitted'),
        ('done', 'RFQ Created'),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')    

    order_line = fields.One2many('purchase.request.line', 'order_id', string='Purchase Request Lines', copy=False)

    purchase_count = fields.Integer(compute='_compute_purchase', string='Purchase', default=0, compute_sudo=True)    

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('purchase.request') or '/'
        return super(PurchaseReques, self).create(vals)

    @api.one
    def sent_rfp(self):
        self.write({'state':'sent'})

    @api.multi
    def validate_creation_purchase_order(self):
        #Check
        for rfp in self:            
            supplier_ids = []
            product_supplier_info = self.env['product.supplierinfo']
            #Check Supplier MOQ
            for line in rfp.order_line:
                product_supplier_info_obj = product_supplier_info.search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),('name', '=', line.supplier_id.id)], limit=1)
                if product_supplier_info_obj:
                    if product_supplier_info_obj.min_qty > 0:
                        if product_supplier_info_obj.min_qty != line.product_qty:
                            raise UserError(_('%s order quantity is less than Minimum Order Quantity.\nPlease order minimum of %.3f %s' % (line.product_id.name.upper(), product_supplier_info_obj.min_qty,product_supplier_info_obj.product_uom.name)))

            for line in rfp.order_line:
                if not line.supplier_id:
                    raise UserError(_('Product %s has no Supplier Info. Please define a Supplier.' % line.product_id.name))

            #To Check all the Order Lines product has no define supplier
            list_of_product_supplier_not_exists = ''
            for line in rfp.order_line:
                product_supplier_info_obj = product_supplier_info.search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),('name', '=', line.supplier_id.id)], limit=1)

                if not product_supplier_info_obj:
                    product_supplier_not_exists = ''
                    product_supplier_not_exists = "%s is not listed as Vendor for %s." %(line.supplier_id.name, line.product_id.name)
                    list_of_product_supplier_not_exists = list_of_product_supplier_not_exists + product_supplier_not_exists + '\n'

            #To Check if Supplier has no MOQ(Zero Quantity)
            for line in rfp.order_line:
                product_supplier_info_obj = product_supplier_info.search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),('name', '=', line.supplier_id.id)], limit=1)
                if product_supplier_info_obj:
                    if product_supplier_info_obj.min_qty == 0:
                        product_supplier_no_moq = ''
                        product_supplier_not_exists = "Minimal Order Quantity for %s with Vendor %s is 0." %(line.product_id.name, line.supplier_id.name)
                        list_of_product_supplier_not_exists = list_of_product_supplier_not_exists + product_supplier_not_exists + '\n'


            if list_of_product_supplier_not_exists:
                #raise Warning(list_of_product_supplier_not_exists)
                view = rfp.env.ref('omni_goodheart_purchase_req.view_new_vendor')
                wiz = rfp.env['purchase.request.add.supplier'].create({'vendor_list': list_of_product_supplier_not_exists,
                                                                        'purchase_request_id': rfp.id})
                return {
                    'name': _('Supplier Validation'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'purchase.request.add.supplier',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': rfp.env.context,}
            else:
                rfp.create_purchase_order()
        return True    

    @api.one
    def create_purchase_order(self):
        supplier_ids = []
        product_supplier_info = self.env['product.supplierinfo']
        #Check Supplier MOQ
        #for line in self.order_line:
        #    product_supplier_info_obj = product_supplier_info.search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id),('name', '=', line.supplier_id.id)], limit=1)
        #    if product_supplier_info_obj:
        #        if product_supplier_info_obj.min_qty != line.product_qty:
        #            raise UserError(_('%s order quantity is less than Minimum Order Quantity.\nPlease order minimum of %.3f %s' % (line.product_id.name.upper(), product_supplier_info_obj.min_qty,product_supplier_info_obj.product_uom.name)))

        for line in self.order_line:
            #if not line.supplier_id:
            #    raise UserError(_('Product %s has no Supplier Info. Please define a Supplier.' % line.product_id.name))

            if not supplier_ids:
                supplier_ids.append(line.supplier_id.id)
            else:
                no_supplier = True
                for supplier_id in supplier_ids:
                    if supplier_id == line.supplier_id.id:
                        no_supplier = False
                        break
                if no_supplier:
                    supplier_ids.append(line.supplier_id.id)


        if supplier_ids:
            purchase_order = self.env['purchase.order']
            for supplier_id in supplier_ids:
                purchase_order_lines = []

                purchase_request_lines = self.env['purchase.request.line'].search([('order_id', '=', self.id),
                                                                                   ('supplier_id', '=', supplier_id)])

                if purchase_request_lines:
                    for line in purchase_request_lines:
                        purchase_order_line = (0,0,{
                            'name': line.name,
                            'product_id':  line and line.product_id and line.product_id.id or False,
                            'product_uom':  line and line.product_uom and line.product_uom.id or False,
                            'product_qty':  line and line.product_qty and line.product_qty or 0,
                            'date_planned': fields.Datetime.now(),
                            'price_unit': 0.00,
                            })
                        purchase_order_lines.append(purchase_order_line)

                    res =purchase_order.create({
                            'partner_id': supplier_id,
                            'order_line': purchase_order_lines,
                            'purchase_request_id': self.id,})


        self.write({'state':'done'})
        return True


    @api.one
    def cancel_purchase_request(self):
        self.write({'state':'cancel'})

    @api.one
    def draft_purchase_request(self):
        self.write({'state':'draft'})

    @api.multi
    def action_view_purchase_order(self):
        action = self.env.ref('purchase.purchase_rfq')
        result = action.read()[0]

        result['context'] = {'search_default_todo':1}
        result['domain'] = "[('purchase_request_id','=',%s)]" % (self.id)
        return result          

class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"
    _description = "Purchase Requisition Lines"

    order_id = fields.Many2one('purchase.request', string='Order Reference', index=True, required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Partner')
    supplier_id = fields.Many2one('res.partner', string='Partner')
    date_order = fields.Date(related='order_id.date_needed', string='Order Date', readonly=True)

    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    date_planned = fields.Datetime(string='Scheduled Date', index=True)
    product_uom = fields.Many2one('product.uom', string='Product Unit of Measure', required=True)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)], change_default=True, required=True)
    date_order = fields.Date(related='order_id.date_needed', string='Order Date', readonly=True)
    state = fields.Selection(related='order_id.state', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True, string='Currency', readonly=True)    
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)


    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result


        supplier_ids = []
        product_supplier_info = self.env['product.supplierinfo']

        product_supplier_info_obj = product_supplier_info.search([('product_tmpl_id', '=', self.product_id.product_tmpl_id.id)], order="sequence asc", limit=1)

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        #self.price_unit = self.product_qty = 0.0
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.supplier_id = product_supplier_info_obj and product_supplier_info_obj.name or False
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
        )
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase
        self.product_qty = 1.0
        #self._suggest_quantity()        
        #self._onchange_quantity()
        return result




class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Requesition', readonly=True)


    @api.multi
    def button_confirm(self):
        for order in self:
            for order_line in order.order_line:
                if order_line.price_unit <= 0:
                    raise UserError(_('Product %s Unit Price is Zero Amount.' % order_line.product_id.name))
                if round(order_line.price_unit,3) != round(order_line.product_id.standard_price,3) :
                    if self.env.ref('omni_goodheart_purchase_req.business_owner') not in self.env.user.groups_id:
                        raise UserError(_('Product %s Cost Price is not equal to Purchase Unit Price.\nNeed Business Owner Approval.' % order_line.product_id.name))

        return super(PurchaseOrder, self).button_confirm()
