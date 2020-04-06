# -*- coding: utf-8 -*-
from odoo import http

# class GhReceivingAdvice(http.Controller):
#     @http.route('/gh_receiving_advice/gh_receiving_advice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gh_receiving_advice/gh_receiving_advice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('gh_receiving_advice.listing', {
#             'root': '/gh_receiving_advice/gh_receiving_advice',
#             'objects': http.request.env['gh_receiving_advice.gh_receiving_advice'].search([]),
#         })

#     @http.route('/gh_receiving_advice/gh_receiving_advice/objects/<model("gh_receiving_advice.gh_receiving_advice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gh_receiving_advice.object', {
#             'object': obj
#         })