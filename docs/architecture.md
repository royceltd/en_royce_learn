# Architecture and decisions

## Boundaries

Learning is a tenant-local Frappe app. It neither connects to the internal Royce ERP
nor manages subscription invoices. No network connection is needed for guides or progress.

The versioned `content/catalog.json` is the authoritative source in v1. Its written guides
are mirrored into Learning Guide records during installation/migration, keeping stable
IDs for Link fields and generic Desk access. Custom library endpoints read the bundled
catalog; editing those mirrored records is not a supported authoring workflow.

Learning paths reference guide IDs in the same catalog. App requirements and DocType
permissions filter both paths and guides. Payroll and SMS paths appear only when their
required apps are installed and the user can access the relevant screen.

## Data

- Learning Guide: managed content and stable guide IDs.
- Learning Progress: one deterministic primary key per `(user, guide)`; includes the
  completed content version. Completion never resets merely because a guide is opened again.
- Learning Setup Task: one deterministic key per `(company, step)`; confirmation status,
  actor, timestamp, and optional note.

Evidence-based tasks are evaluated live using permission-aware `frappe.get_list` calls.
Cancelling qualifying transactions changes the current evidence, rather than retaining a
misleading permanent completion flag. A return invoice does not count as the first invoice.
A submitted Receive Payment Entry must have a positive Sales Invoice reference allocation.

Confirmation and personal progress writes use parameterized MariaDB upserts to handle
concurrent requests without duplicate rows. This release targets Royce's MariaDB workload
stack, not a PostgreSQL tenant database. No transaction commits are issued inside endpoints;
Frappe handles request transactions. SQL upserts do not create Frappe Version records;
confirmation rows retain the latest actor/time, rather than a complete audit history.

## Multi-company semantics

Company, invoice, and payment access is checked on the server. User Permissions filter
company choices. Items, customers, and users are shared masters in ERPNext; simply counting
them would incorrectly complete setup across companies. An administrator confirms their
readiness separately for each company.

Only a user with write access to the selected Company may confirm tasks, and the task's
screen must also be readable. Staff without that access can read their relevant guidance.
Dashboard percentages describe **tasks visible to the current user's permissions**; they
must not be used as an authoritative platform-wide customer readiness percentage.

## Security

- Signed-in System Users only; Guest and Website User access is denied.
- POST-only mutation endpoints use Frappe's standard authentication/CSRF handling.
- Learning writes always target the authenticated user, never a caller-supplied user ID.
- Generic DocType permissions are read/select only. Query and document permission hooks
  restrict guides, personal progress, and company confirmations.
- Administrator retains Frappe's normal superuser access; site administrators are trusted.
- Content is displayed as text, never injected as arbitrary HTML.
- Videos accept only valid YouTube IDs and load from youtube-nocookie.com after an explicit
  user action. There are no external fetch URLs, arbitrary iframe sources, or credentials.
- No ERP business documents are created, submitted, cancelled, or changed by learning actions.

## Compatibility references

Implementation checked against primary v16 source:

- [Permission hook calls use ptype](https://github.com/frappe/frappe/blob/version-16/frappe/permissions.py)
- [Form refresh event](https://github.com/frappe/frappe/blob/version-16/frappe/public/js/frappe/form/form.js)
- [Document insertion and set_name](https://github.com/frappe/frappe/blob/version-16/frappe/model/document.py)
- [Workspace Sidebar Item schema](https://github.com/frappe/frappe/blob/version-16/frappe/desk/doctype/workspace_sidebar_item/workspace_sidebar_item.json)

Source compatibility review is not a substitute for running the app on the pinned staging image.
