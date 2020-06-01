# -*- coding: utf-8 -*-
{
    'name': "Goodheart Purchase Order Report",

    'summary': """
        Extends Purchase Order Report Template to include additional fields and improvements on design.""",

    'description': """
        Extends Purchase Order Report Template to include additional fields and improvements on design.
    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_invoicing','purchase','sale_management','quality','web','gh_po_ext'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        #'data/report.paperformat.csv',
        'views/templates.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}