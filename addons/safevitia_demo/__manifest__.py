{
    "name": "Safe Vitia - Escenario demo",
    "summary": "Datos y flujos demostrativos para distribución de agua",
    "version": "17.0.1.0.0",
    "category": "Hidden",
    "author": "Safe Vitia",
    "license": "LGPL-3",
    "depends": [
        "contacts",
        "crm",
        "sale_management",
        "stock",
        "account",
        "l10n_mx",
        "purchase",
        "fleet",
        "web_editor",
    ],
    "assets": {
        "web.assets_backend": [
            ("include", "web_editor.backend_assets_wysiwyg"),
        ],
    },
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
