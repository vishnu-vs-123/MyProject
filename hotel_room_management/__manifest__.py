# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Hotel Room Management',
    'version': '1.1',
    'summary': 'Hotel Room Management software',
    'sequence': 10,
    'description': """Hotel Room Management software""",
    'category': '',
    'website': 'https://www.odoo.com/page/billing',
    'depends': ['base', 'mail'],
    'data': ['security/ir.model.access.csv',
             'views/room.xml', 'views/sequence.xml', 'views/order_food.xml'],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}
