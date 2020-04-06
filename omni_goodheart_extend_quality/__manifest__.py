# -*- coding: utf-8 -*-
{
    'name': "Quality Module Extend",

    'summary': """
        Customizatiom of Quality Control""",

    'description': """
        Customizatiom of Quality Control
        * Added Field in Quality Check(Result)

    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','quality'],

    # always loaded
    'data': [
        'views/quality_views.xml',
    ],
}