# -*- coding: utf-8 -*-
{
    'name': "Goodheart Decimal Accuracy - Sale Order Quantities",

    'summary': """
        Creates a record in sale.order called sale Order Quantity""",

    'description': """
        Creates a record in sale.order called sale Order Quantity
    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_invoicing','purchase','sale_management','mrp_plm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}