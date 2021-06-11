# -*- coding: utf-8 -*-
{
    "name": "Travel Request",
    "version": "14.0.1.0.0",
    "category": "Human Resources",
    "summary": """
        Travel Request.
    """,
    "depends": ["project", "hr", "hr_expense"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/mail_template.xml",
        "view/travel_request_view.xml",
        "view/travel_expenses_view.xml",

    ],
    "installable": True,
    "auto_install": False,
}
