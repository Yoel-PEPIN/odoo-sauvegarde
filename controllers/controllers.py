# -*- coding: utf-8 -*-
from odoo import http

# class Autosauvegarde(http.Controller):
#     @http.route('/autosauvegarde/autosauvegarde/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/autosauvegarde/autosauvegarde/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('autosauvegarde.listing', {
#             'root': '/autosauvegarde/autosauvegarde',
#             'objects': http.request.env['autosauvegarde.autosauvegarde'].search([]),
#         })

#     @http.route('/autosauvegarde/autosauvegarde/objects/<model("autosauvegarde.autosauvegarde"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('autosauvegarde.object', {
#             'object': obj
#         })