# -*- coding: utf-8 -*-
from odoo import http

# class PartnerSevenExtension(http.Controller):
#     @http.route('/partner_seven_extension/partner_seven_extension/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_seven_extension/partner_seven_extension/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_seven_extension.listing', {
#             'root': '/partner_seven_extension/partner_seven_extension',
#             'objects': http.request.env['partner_seven_extension.partner_seven_extension'].search([]),
#         })

#     @http.route('/partner_seven_extension/partner_seven_extension/objects/<model("partner_seven_extension.partner_seven_extension"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_seven_extension.object', {
#             'object': obj
#         })