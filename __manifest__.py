{
    'name': 'Payment Provider: chapa',
    'version': '17.0.1.1',
    'category': 'Hidden',
    'summary': 'chapa Payment Gateway For Website',
    'description': "This module enables seamless payments through chapa, "
                   "ensuring secure and convenient online transactions.",
    'author': "Abduselam M.",
    'company': '__',
    'maintainer': 'Abdulselam M.',
    'website': "https://abdulselamt.github.io/portfolio/home.html",
    'depends': ['payment','account'],
    'data': [
        'views/payment_chapa_templates.xml',
        'views/payment_method_data.xml',
        'views/payment_provider_views.xml',
        'views/payment_transaction_views.xml',
        'data/payment_provider_data.xml',
        'data/invoice_payment_link.xml'
    ],
  
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
