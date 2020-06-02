# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Remove Update Qty on Hand',
    'version' : '1.1',
    'summary': 'Update Qty on Hand Button Removed',
    'sequence': 30,
    'author': "OmniTechnical",
    'website': "https://www.omnitechnical.com/",
    'description': """    
Remove button on Product for Good Heart and Coneland
    """,
    'category': 'Addons',
    'depends' : ['stock'],
    'data': [
        'views/product_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
