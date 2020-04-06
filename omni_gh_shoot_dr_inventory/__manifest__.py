# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Omnitechnical Goodheart: Inventory Stock Report',
    'version' : '1.1',
    'summary': 'Inventory Stock Report',
    'sequence': 30,
    'author': "OmniTechnical",
    'website': "https://www.omnitechnical.com/",
    'description': """
Inventory Stock Report for Good Heart and Coneland
    """,
    'category': 'Addons',
    'depends' : ['stock', 'purchase'],
    'data': [
        # 'data/purchase_data_requisition_data.xml',
        # 'security/ir.model.access.csv',
        #'data/data_account_type.xml',
        #'data/account_data.xml',
        #'views/account_menuitem.xml',
        # 'views/purchase_requisition_views.xml',
        # 'wizard/new_supplier_product.xml',
        'views/views.xml',
        'views/delivery_receipt_selecta.xml',
        'views/delivery_receipt_others.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
