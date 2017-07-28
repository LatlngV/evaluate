# -*- coding: utf-8 -*-
{
    "name": "评价",
    "summary": "这是公司内部的评价",
    "author": "Latlng",
    "sequence": "1",
    "version": "1.0",
    "depends": ["hr", "survey"],
    "data": [
        "security/employee_evaluate_security.xml",
        "security/ir.model.access.csv",
        "views/start_survey_view.xml",
        "views/survey_view.xml",
        "views/passive_evaluate_view.xml",
        "views/evaluate_menuitem_view.xml",
        "report/evaluate_report.xml",
        "report/evaluate_report_template.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "description": """
这是公司内部的评价系统
=====================
    """,
}
