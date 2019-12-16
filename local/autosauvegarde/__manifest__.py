# -*- coding: utf-8 -*-
{
    'name': "autosauvegarde",

    'summary': """
        Sauvegarde Auto""",

    'description': """
        Module automatique permettant la sauvegarde de la base de donnée et du filestore tout les jours
    """,

    'author': "Digitom",
    'website': "http://www.digitom.fr",

    'category': 'Uncategorized',
    'version': '13.0.0.1',

     'depends': ['base'],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/cron.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}