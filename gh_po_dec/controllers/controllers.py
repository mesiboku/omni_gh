# -*- coding: utf-8 -*-
from odoo import http

# class Goodheart(http.Controller):
#     @http.route('/goodheart/goodheart/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/goodheart/goodheart/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('goodheart.listing', {
#             'root': '/goodheart/goodheart',
#             'objects': http.request.env['goodheart.goodheart'].search([]),
#         })

#     @http.route('/goodheart/goodheart/objects/<model("goodheart.goodheart"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('goodheart.object', {
#             'object': obj
#         })