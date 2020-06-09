# -*- coding: utf-8 -*-
{
    'name': "Override Stock Move _run_fifo",

    'summary': """
        Override Stock Move _run_fifo. to run as Sudo""",

    'description': """
        This will override the _run_fifo as sudo to fixed the concern
    """,

    'author': "OmniTechnical",
    'website': "http://www.omnitechnical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    # Created By Samuel Salvador 
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','stock_account'],

    # always loaded
    #'data': [],
}