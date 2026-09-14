"""Generate standard Frappe metadata and the bundled guide catalog. Development only."""

import json
from pathlib import Path

ROOT = Path(__file__).parent / "royce_learn"
MODULE = ROOT / "royce_learn"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def field(name, kind, label, **kwargs):
    return {"fieldname": name, "fieldtype": kind, "label": label, **kwargs}


schemas = {
    "Royce Learn Guide": [
        field("title", "Data", "Title", reqd=1, in_list_view=1),
        field("summary", "Small Text", "Summary"),
        field("category", "Data", "Topic", in_list_view=1),
        field("content_version", "Data", "Content Version"),
        field("body", "Long Text", "Written Instructions"),
        field("video_id", "Data", "YouTube Video ID"),
        field("reference_doctype", "Link", "Related Screen", options="DocType"),
        field("required_apps", "Small Text", "Required Apps"),
        field("keywords", "Small Text", "Keywords"),
        field("published", "Check", "Published", default="1"),
    ],
    "Royce Learn Progress": [
        field("user", "Link", "User", options="User", reqd=1, in_list_view=1),
        field("guide", "Link", "Guide", options="Royce Learn Guide", reqd=1, in_list_view=1),
        field("status", "Select", "Status", options="In Progress\nCompleted", reqd=1, in_list_view=1),
        field("completed_at", "Datetime", "Completed At"),
        field("completed_version", "Data", "Completed Version"),
    ],
    "Royce Learn Setup": [
        field("company", "Link", "Company", options="Company", reqd=1, in_list_view=1),
        field("step_id", "Data", "Task", reqd=1, in_list_view=1),
        field(
            "status", "Select", "Status", options="Pending\nComplete\nNot Applicable", reqd=1, in_list_view=1
        ),
        field("confirmed_by", "Link", "Confirmed By", options="User"),
        field("confirmed_at", "Datetime", "Confirmed At"),
        field("note", "Small Text", "Note"),
    ],
}
for name, fields in schemas.items():
    slug = name.lower().replace(" ", "_")
    folder = MODULE / "doctype" / slug
    for item in fields:
        item["read_only"] = 1
    write(
        folder / f"{slug}.json",
        {
            "doctype": "DocType",
            "name": name,
            "module": "Royce Learn",
            "engine": "InnoDB",
            "autoname": "hash",
            "field_order": [f["fieldname"] for f in fields],
            "fields": fields,
            "permissions": [
                {"role": "Desk User", "read": 1, "select": 1},
                {"role": "System Manager", "read": 1, "select": 1},
            ],
            "track_changes": 1,
            "sort_field": "modified",
            "sort_order": "DESC",
            "actions": [],
            "links": [],
            "states": [],
        },
    )
    (folder / f"{slug}.py").write_text(
        "from frappe.model.document import Document\n\n\nclass "
        + name.replace(" ", "")
        + "(Document):\n    pass\n",
        encoding="utf-8",
    )

write(
    MODULE / "page" / "royce_learn" / "royce_learn.json",
    {
        "doctype": "Page",
        "name": "royce-learn",
        "page_name": "royce-learn",
        "module": "Royce Learn",
        "title": "Royce Learn",
        "standard": "Yes",
        "system_page": 0,
        "roles": [{"role": "Desk User"}, {"role": "System Manager"}],
    },
)
workspace_content = [
    {"id": "rl-header", "type": "header", "data": {"text": '<span class="h4">Royce Learn</span>', "col": 12}},
    {
        "id": "rl-shortcut",
        "type": "shortcut",
        "data": {"shortcut_name": "Getting Started & Guides", "col": 4},
    },
]
write(
    MODULE / "workspace" / "royce_learn" / "royce_learn.json",
    {
        "doctype": "Workspace",
        # Deliberately NOT "Royce Learn" -- Frappe slugifies a Workspace's own
        # name to its route, and a bare "Royce Learn" collides with the Page
        # below (route "royce-learn"), which the router always resolves as the
        # Workspace first -- silently making the actual content page
        # unreachable and its own shortcut a no-op back to itself. Real bug,
        # found live in production 2026-09-14. label/title stay "Royce Learn"
        # since only "name" drives routing.
        "name": "Royce Learn Hub",
        "label": "Royce Learn",
        "title": "Royce Learn",
        "module": "Royce Learn",
        "app": "royce_learn",
        "public": 1,
        "is_hidden": 0,
        "icon": "education",
        "content": json.dumps(workspace_content),
        "roles": [],
        "links": [],
        "charts": [],
        "number_cards": [],
        "shortcuts": [
            {"label": "Getting Started & Guides", "type": "Page", "link_to": "royce-learn", "color": "Blue"}
        ],
    },
)
write(
    ROOT / "workspace_sidebar" / "royce_learn.json",
    {
        "doctype": "Workspace Sidebar",
        "name": "Royce Learn",
        "title": "Royce Learn",
        "app": "royce_learn",
        "standard": 1,
        "header_icon": "education",
        "items": [
            {"label": "Royce Learn", "link_type": "Workspace", "link_to": "Royce Learn Hub", "type": "Link"}
        ],
    },
)
write(
    ROOT / "desktop_icon" / "royce_learn.json",
    {
        "doctype": "Desktop Icon",
        "name": "Royce Learn",
        "label": "Royce Learn",
        "app": "royce_learn",
        "standard": 1,
        "hidden": 0,
        "icon_type": "Link",
        "link_type": "Workspace Sidebar",
        "link_to": "Royce Learn",
        "icon": "education",
        "bg_color": "blue",
        "roles": [],
        "logo_url": "/assets/royce_learn/icons/royce_learn.svg",
    },
)

guides = []


def guide(key, title, summary, category, dt, body, apps=None, minutes=3, keywords=None):
    guides.append(
        {
            "id": key,
            "title": title,
            "summary": summary,
            "category": category,
            "doctype": dt,
            "permission": "read",
            "required_apps": apps or ["erpnext"],
            "version": "1.0.0",
            "minutes": minutes,
            "video_id": "",
            "keywords": keywords or [],
            "body": body,
        }
    )


guide(
    "company-details",
    "Confirm your company details",
    "Review the business configuration created during provisioning.",
    "Getting Started",
    "Company",
    """Your provisioned site already has a Company and a Kenya accounting baseline. Review these before entering transactions.

1. Open Company and select the company shown in your Getting Started dashboard.
2. Check the legal business name, abbreviation, country, and default currency.
3. Review company addresses and contact details where configured.
4. Ask your accountant to review the chart of accounts and applicable tax templates.
5. Check that a Fiscal Year covers your transaction dates. Provisioning creates a starting baseline; confirm your own accounting period.
6. Return to Royce Learn and confirm this task for the selected company.

Changing company settings can affect subsequent transactions. Make changes with the appropriate permissions and accounting review.

If you cannot edit Company, ask a company administrator to complete this task. Selecting another company shows a separate checklist.""",
)
guide(
    "users-and-roles",
    "Add your team and review roles",
    "Give each staff member the access needed for their work.",
    "Getting Started",
    "User",
    """1. Ask a System Manager to open User and create a separate account for each staff member.
2. Use System User for staff who need the ERP Desk.
3. Assign roles matching their responsibilities, such as selling or accounting.
4. Review User Permissions where staff should be limited to specific companies.
5. Verify access using the staff member's own account before they begin work.
6. Return to the selected company's checklist and confirm that its team access is ready.

Users belong to the site, rather than a single company. This task requires explicit company confirmation so access for one company does not automatically complete another company's setup.

Use named accounts for daily work and keep administrative access limited. If staff cannot see a screen, review roles and company permissions rather than sharing an administrator account.""",
)
guide(
    "items",
    "Add products or services",
    "Create the items your company will sell or purchase.",
    "Sales",
    "Item",
    """1. Open Item and select New if you have create permission.
2. Enter a clear Item Code and Item Name, then choose an Item Group and stock unit of measure.
3. For services, review whether Maintain Stock should be disabled. For stocked products, configure inventory details with your stock administrator.
4. Review item defaults for the company that will use the item, including accounts and warehouses where applicable.
5. Save the item and confirm it can be selected on the intended transaction.
6. Return to Royce Learn and confirm that the selected company's products or services are ready.

Items are shared site masters. Their existence alone does not prove that they are configured for every company.

If an item cannot be selected, check whether it is disabled, whether the transaction allows it, and whether you have access. Tax treatment needs separate review.""",
    keywords=["product", "service", "inventory"],
)
guide(
    "customers",
    "Add your customers",
    "Create customer records before invoicing.",
    "Sales",
    "Customer",
    """1. Open Customer and choose New if you have create permission.
2. Enter the customer name and select the appropriate customer type, group, and territory.
3. Save, then add or link contact and address records as needed.
4. Review company-specific receivable account defaults with your accountant where required.
5. Check that the customer can be selected on a Sales Invoice for the intended company.
6. Confirm this task on that company's Getting Started checklist.

Customer records are shared within a site. This checklist uses explicit confirmation rather than treating any customer record as setup for all companies.

Avoid duplicate records by searching first. If an address does not appear on an invoice, check that its links point to the correct customer.""",
    keywords=["contact", "address"],
)
guide(
    "opening-balances",
    "Review opening balances",
    "Decide how existing balances will enter your ERP.",
    "Accounting",
    "Journal Entry",
    """Opening balances depend on whether your business is new or migrating existing books.

1. Agree on a cutover date with your accountant.
2. Reconcile balances in the previous system before importing them.
3. Identify general ledger balances, unpaid customer and supplier invoices, stock, and bank balances.
4. Use the appropriate ERPNext opening tools for each category. Do not enter the same balance through multiple tools.
5. Review the resulting trial balance and outstanding reports before starting normal operations.
6. Confirm the task only after reconciliation. If no opening balances apply, choose Not applicable and record the reason.

This guide is a planning checklist, not an accounting entry recipe. Your accountant must determine the actual entries and reconciliation for your business.""",
    minutes=5,
)
guide(
    "sales-invoice",
    "Create and submit a sales invoice",
    "Complete your first company-specific invoicing transaction.",
    "Sales",
    "Sales Invoice",
    """1. Open Sales Invoice and choose New if you have create permission.
2. Select the intended Company and Customer. Check the posting date and due date.
3. Add products or services, quantities, and rates.
4. Review currency, receivable account, addresses, and any applicable taxes with your accountant's approved configuration.
5. Save and review the totals. A saved draft has not completed the accounting transaction.
6. Submit only when the invoice is correct and you have the required permission.
7. Open print preview and check the customer-facing document before sending it.

Royce Learn detects a submitted non-return invoice for the selected company. Drafts and invoices in other companies do not complete the task. If the qualifying invoice is cancelled, the evidence check updates when the dashboard reloads.

If submission fails, read the exact validation message. Common causes include missing account defaults, unavailable stock, or dates outside an active fiscal year. This guide does not assume eTIMS is installed or configured.""",
    minutes=4,
    keywords=["billing", "invoice", "submit"],
)
guide(
    "receive-payment",
    "Receive payment against an invoice",
    "Record and allocate a customer payment.",
    "Accounting",
    "Payment Entry",
    """1. Open the submitted Sales Invoice and use its payment action where available, or create a Payment Entry.
2. Select Receive and Customer, then confirm the Company and customer.
3. Choose the correct bank or cash account and enter the actual payment amount and date.
4. In References, select the Sales Invoice and review the allocated amount.
5. Check any difference or exchange-rate entries with your accountant.
6. Save, review, and submit when correct.
7. Check the invoice's outstanding balance after posting.

Royce Learn checks for a submitted customer receipt in the selected company with a positive allocation to a Sales Invoice. An unallocated advance or draft payment does not complete this task.

If an invoice is missing from the reference list, check its company, customer, submission status, and outstanding amount. Record real payments only; reading this lesson is separate from submitting a payment.""",
    minutes=4,
    keywords=["receipt", "allocation", "bank"],
)
guide(
    "payroll-getting-started",
    "Review your payroll baseline",
    "Understand what Royce Payroll configures and what you still need to prepare.",
    "Payroll",
    "Employee",
    """Royce provisioning can prepare statutory accounts, salary components, a salary structure, payroll periods, and holiday settings through Royce Payroll KE.

1. Ask your payroll administrator to review the effective Payroll Rates record and the generated structure.
2. Create Employee records for the correct company and verify employee identifiers and payroll details.
3. Review Salary Structure Assignments and dates for each employee.
4. Confirm attendance, leave, and holiday configuration before processing payroll.
5. Validate a representative payroll run and its reports before production use.

Generated defaults do not replace review of current statutory rules or employee-specific circumstances. This introductory guide intentionally contains no hard-coded statutory rates.""",
    apps=["erpnext", "hrms", "royce_payroll_ke"],
    minutes=5,
)
guide(
    "sms-getting-started",
    "Configure Royce Talk",
    "Prepare SMS settings before sending notifications.",
    "Royce Apps",
    "RoyceTalk Settings",
    """Installing Royce Talk does not create an SMS account or register a Sender ID.

1. Obtain your approved Sender ID and Royce Talk API credentials through your account process.
2. Open RoyceTalk Settings and configure them using an authorized administrator account.
3. Review balance and perform a test send to a number you control.
4. Review notification templates before enabling automated messages.
5. For marketing campaigns, review recipients and consent before sending.

Royce provisioning leaves the site-wide SMS gateway override disabled. Enabling it affects Frappe's built-in SMS traffic too, so review that setting deliberately.

Keep API credentials private. If sends fail, inspect RoyceTalk SMS Log and the account balance.""",
    apps=["erpnext", "royce_talk"],
)
write(
    ROOT / "content" / "catalog.json",
    {
        "schema_version": 1,
        "guides": guides,
        "paths": [
            {
                "id": "getting-started",
                "title": "Getting Started",
                "summary": "Prepare your company and team.",
                "guides": ["company-details", "users-and-roles", "items", "customers", "opening-balances"],
            },
            {
                "id": "sales-basics",
                "title": "Sales Basics",
                "summary": "Move from customer setup to invoice and payment.",
                "guides": ["customers", "items", "sales-invoice", "receive-payment"],
            },
            {
                "id": "payroll-basics",
                "title": "Payroll Basics",
                "summary": "Review your payroll baseline before processing.",
                "guides": ["payroll-getting-started"],
            },
            {
                "id": "sms-basics",
                "title": "Royce Talk Basics",
                "summary": "Set up customer notifications.",
                "guides": ["sms-getting-started"],
            },
        ],
    },
)
for folder in [MODULE, MODULE / "doctype", MODULE / "page", MODULE / "workspace"]:
    folder.mkdir(parents=True, exist_ok=True)
for folder in [MODULE, *[p for p in MODULE.rglob("*") if p.is_dir()]]:
    (folder / "__init__.py").touch()
