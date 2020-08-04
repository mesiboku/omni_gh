# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Purchase Requisition',
    'version' : '1.1',
    'summary': 'Purchase Requisition',
    'sequence': 30,
    'author': "OmniTechnical",
    'website': "https://www.omnitechnical.com/",
    'description': """    
Purchase Requisition for Good Heart and Coneland
    """,
    'category': 'Addons',
    'depends' : ['stock', 'purchase'],
    'data': [
        'data/purchase_data_requisition_data.xml',
        'security/ir.model.access.csv',
        #'data/data_account_type.xml',
        #'data/account_data.xml',
        #'views/account_menuitem.xml',
        'views/purchase_requisition_views.xml',
        'wizard/new_supplier_product.xml',
        'views/purchase_order.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
