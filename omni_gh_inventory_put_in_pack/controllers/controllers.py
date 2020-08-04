# -*- coding: utf-8 -*-
from odoo import http

# class OmniGhMo(http.Controller):
#     @http.route('/omni_gh_mo/omni_gh_mo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/omni_gh_mo/omni_gh_mo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('omni_gh_mo.listing', {
#             'root': '/omni_gh_mo/omni_gh_mo',
#             'objects': http.request.env['omni_gh_mo.omni_gh_mo'].search([]),
#         })

#     @http.route('/omni_gh_mo/omni_gh_mo/objects/<model("omni_gh_mo.omni_gh_mo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('omni_gh_mo.object', {
#             'object': obj
#         })