# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools.translate import _
from odoo.tools.misc import formatLang, format_date
from odoo.exceptions import UserError

LINE_FILLER = '*'
INV_LINES_PER_STUB = 9

class account_payment_report(models.Model):
    _inherit = 'account.payment'

    checkvoucher_amount_total = fields.Char('Amount Tax', compute = '_compute_get_amount_total')
    dr_dates = fields.Char('DR Dates')
    dr_number = fields.Char('DR Numbers')
    particulars_invoice_ids = fields.Many2many('account.invoice', 
                                               'partic_account_invoice_payment_rel', 
                                               'payment_id', 
                                               'invoice_id', 
                                               string="Particulars", 
                                               copy=False,
                                            )


    @api.onchange('particulars_invoice_ids', 'partner_id')
    def particulars_invoice_ids_onchange(self):
        #Check Total Added Invoices
        total_particulars = 0.00
        #for particular in self.particulars_invoice_ids:
        #    total_particulars +=particular.amount_total
        #if total_particulars > self.amount:
        #    raise UserError(_('Total Amount of Selected Pariculars is greater than the Payment Amount.'))

        res ={}
        res['domain'] = {'particulars_invoice_ids': [('type','=','in_invoice'), ('state','=','open'), ('partner_id','=', self.partner_id and self.partner_id.id or False)]}
        return res


    def _compute_get_amount_total(self):
        if self:
            for record in self:
                find_invoice = self.env['account.invoice'].search([('payment_ids','=',record.id)])
                if find_invoice:
                    for x in find_invoice:
                        record.checkvoucher_amount_total = x.amount_tax

    def fill_line(self, amount_str):
    	return amount_str and (amount_str+' ').ljust(200, LINE_FILLER) or ''

    @api.multi
    def getAmountInWords(self):
    	self.ensure_one()
    	return self.check_amount_in_words

    @api.multi
    def getJournalItems(self):
    	self.ensure_one()
    	account_move_line = self.env['account.move.line'].search([('payment_id', 'in', self.ids)])
    	return account_move_line or False

    @api.multi
    def getJLItems(self):
        self.ensure_one()
        account_move_line = self.env['account.move.line'].search([('payment_id', 'in', self.ids),('credit', '>', 0.00)], limit=1)
        return account_move_line and account_move_line.account_id and account_move_line.account_id.name  or ''

    @api.multi
    def getDeliverDates(self):
        
        self.ensure_one()
        return self.dr_dates
        sale_order_names = []
        purchase_order_names = []
        # Get All the Source Document
        if self.invoice_ids:
            for invoice in self.invoice_ids:
                if invoice.type =='out_invoice':
                    if len(sale_order_names) == 0:
                        sale_order_names.append(invoice.origin)
                    else:
                        if invoice.origin not in sale_order_names:
                            sale_order_names.append(invoice.origin)
                elif invoice.type =='in_invoice':
                    if len(purchase_order_names) == 0:
                        purchase_order_names.append(invoice.origin)
                    else:
                        if invoice.origin not in purchase_order_names:
                            purchase_order_names.append(invoice.origin)

        sale_order_obj = self.env['sale.order'].search([('name', 'in', sale_order_names)])
        po_order_obj = self.env['purchase.order'].search([('name', 'in', purchase_order_names)])

        #Sale Order
        delivery_date = ""
        for sale in sale_order_obj:
            for picking in sale.picking_ids:
                schedule_date = fields.Datetime.from_string(picking.scheduled_date).date()
                #raise Warning(schedule_date.day)
                str_day = str(schedule_date.day).zfill(2)
                str_month = str(schedule_date.month).zfill(2)
                str_year = str(schedule_date.year)
                str_del_date = str_month + '/' + str_day + '/' + str_year[2:4]                
                delivery_date += str_del_date + "-"

        if delivery_date[len(delivery_date)-1:len(delivery_date)] == '-':
            delivery_date = delivery_date[0:len(delivery_date)-1]

        return delivery_date

    @api.multi
    def getSaleInvoice(self):
        self.ensure_one()
        return self.dr_number
        if self.invoice_ids:
            invoices = ""
            for invoice in self.invoice_ids:
                invoices += invoice.number + "/"
            if invoices[len(invoices)-1:len(invoices)] == '/':
                invoices = invoices[0:len(invoices)-1]
            return invoices
        return False



