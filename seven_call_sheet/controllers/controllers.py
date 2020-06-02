# -*- coding: utf-8 -*-
from odoo import http

# class SevenCallSheet(http.Controller):
#     @http.route('/seven_call_sheet/seven_call_sheet/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/seven_call_sheet/seven_call_sheet/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('seven_call_sheet.listing', {
#             'root': '/seven_call_sheet/seven_call_sheet',
#             'objects': http.request.env['seven_call_sheet.seven_call_sheet'].search([]),
#         })

#     @http.route('/seven_call_sheet/seven_call_sheet/objects/<model("seven_call_sheet.seven_call_sheet"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('seven_call_sheet.object', {
#             'object': obj
#         })