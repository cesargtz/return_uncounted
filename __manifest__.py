# -*- coding: utf-8 -*-
{
    'name': "Return Uncounted",

    'summary': """
       return corn uncounted""",


'author': "César Gutierrez",
    'website': "http://www.yecora.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail', 'purchase'],

    # always loaded
    'data': [
        'security/access_rules.xml',
        'security/ir.model.access.csv',
        'views/retunr_uncounted.xml',
        # 'views/templates.xml',
    ],

}