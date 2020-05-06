# -*- coding: utf-8 -*-
{
    'name': "Omnitechnical Customization for Manufacturing Module - Bills of Material",

    'summary': """
        Manufacturing Customization - Bills of Material""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Omnitechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mrp'],

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