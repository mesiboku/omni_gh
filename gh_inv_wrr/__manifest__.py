# -*- coding: utf-8 -*-
{
    'name': "Goodheart Warehouse Receiving Report",

    'summary': """
        Adds Warehouse Receiving Report to list of printable documents in Inventory.""",

    'description': """
        Adds Warehouse Receiving Report to list of printable documents in Inventory.
    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_invoicing','purchase','sale_management','quality','web','omni_goodheart_stock_operation','omni_goodheart_stock_move_operation_hide_cols','omni_goodheart_purchase_req','omni_goodheart_override_product_template','gh_po_ext'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/report_wrr.xml',        
        'views/stock_picking_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}