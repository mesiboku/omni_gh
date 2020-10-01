# -*- coding: utf-8 -*-
{
    'name': "Goodheart Allowance Qty in Manufacturing",

    'summary': """
        Added new Fields to Check the Allowance Quantity.""",

    'description': """
        Allow to Add the Waste Raw Materials for Manufacturing.
    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/mrp_bom_views.xml',
        'security/ir.model.access.csv',
        'views/mrp_production_views.xml',
        'views/stock_move_views.xml',
        'views/product.xml',
        #'views/templates.xml',
        #'views/report_coll_sht.xml',
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo/demo.xml',
    #],
}
