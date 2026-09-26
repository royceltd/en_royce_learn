"""Generate this app's standard Frappe metadata: DocTypes, the getting-started Page,
Workspace, Workspace Sidebar and Desktop Icon. Development only; commit the output.

Guides are NOT generated: edit royce_learn/content/catalog.json directly
(docs/content-maintenance.md). tests/test_generated_assets.py fails if this script's
output and the committed files ever differ."""

import json
from pathlib import Path

ROOT = Path(__file__).parent / "royce_learn"
MODULE = ROOT / "learning"


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def field(name, kind, label, **kwargs):
    return {"fieldname": name, "fieldtype": kind, "label": label, **kwargs}


schemas = {
    "Learning Guide": [
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
    "Learning Progress": [
        field("user", "Link", "User", options="User", reqd=1, in_list_view=1),
        field("guide", "Link", "Guide", options="Learning Guide", reqd=1, in_list_view=1),
        field("status", "Select", "Status", options="In Progress\nCompleted", reqd=1, in_list_view=1),
        field("completed_at", "Datetime", "Completed At"),
        field("completed_version", "Data", "Completed Version"),
    ],
    "Learning Setup Task": [
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
            "module": "Learning",
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
    # Deliberately NOT named "royce_learn"/"royce-learn" -- see the Workspace
    # comment below for why. Folder/file names match the Page's own "name"
    # (Frappe's page-loading convention), so both had to move together.
    MODULE / "page" / "getting_started" / "getting_started.json",
    {
        "doctype": "Page",
        "name": "getting-started",
        "page_name": "getting-started",
        "module": "Learning",
        "title": "Learning",
        "standard": "Yes",
        "system_page": 0,
        "roles": [{"role": "Desk User"}, {"role": "System Manager"}],
    },
)
workspace_content = [
    {"id": "rl-header", "type": "header", "data": {"text": '<span class="h4">Learning</span>', "col": 12}},
    {
        "id": "rl-shortcut",
        "type": "shortcut",
        "data": {"shortcut_name": "Getting Started & Guides", "col": 4},
    },
]
write(
    MODULE / "workspace" / "learning" / "learning.json",
    {
        "doctype": "Workspace",
        # MUST equal app_title ("Learning") -- Frappe v16 matches the app's
        # Desktop Icon, Workspace and Workspace Sidebar by that exact string
        # (frappe/desk/doctype/desktop_icon/desktop_icon.py). Two real bugs came
        # from getting this wrong, both found live in production 2026-09-14,
        # when the app was still titled "Royce Learn":
        # (1) the Workspace's route (/app/royce-learn then, /app/learning now)
        #     collided with the content Page's own route -- the router always
        #     resolves a bare /app/<workspace> as the Workspace first, silently
        #     making the Page unreachable and its own shortcut a no-op back to
        #     itself. Fixed by moving the *Page* to "getting-started" instead
        #     (see above), not the Workspace.
        # (2) renaming the Workspace itself ("Royce Learn Hub") to dodge (1)
        #     broke Frappe's own app<->workspace naming convention: it started
        #     auto-generating a second, orphaned Workspace Sidebar (app=None)
        #     alongside the real one, producing two visibly different Desk
        #     icons for one app and losing this app's own sidebar context in
        #     favor of whatever ERPNext workspace was last active. The
        #     Workspace's name must match app_title for both the app-switcher
        #     and sidebar-grouping to collapse into one correctly; it is the
        #     Page's name that has to move, never this one.
        "name": "Learning",
        "label": "Learning",
        "title": "Learning",
        "module": "Learning",
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
            {"label": "Getting Started & Guides", "type": "Page", "link_to": "getting-started", "color": "Blue"}
        ],
    },
)
write(
    ROOT / "workspace_sidebar" / "learning.json",
    {
        "doctype": "Workspace Sidebar",
        "name": "Learning",
        "title": "Learning",
        "app": "royce_learn",
        "standard": 1,
        "header_icon": "education",
        "items": [{"label": "Learning", "link_type": "Workspace", "link_to": "Learning", "type": "Link"}],
    },
)
write(
    ROOT / "desktop_icon" / "learning.json",
    {
        "doctype": "Desktop Icon",
        "name": "Learning",
        "label": "Learning",
        "app": "royce_learn",
        "standard": 1,
        "hidden": 0,
        "icon_type": "Link",
        "link_type": "Workspace Sidebar",
        "link_to": "Learning",
        "icon": "education",
        "bg_color": "blue",
        "roles": [],
        "logo_url": "/assets/royce_learn/icons/royce_learn.svg",
    },
)

for folder in [MODULE, MODULE / "doctype", MODULE / "page", MODULE / "workspace"]:
    folder.mkdir(parents=True, exist_ok=True)
for folder in [MODULE, *[p for p in MODULE.rglob("*") if p.is_dir()]]:
    (folder / "__init__.py").touch()
