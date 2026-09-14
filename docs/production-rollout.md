# Production rollout and acceptance

Status: local implementation validated; no staging or production deployment performed.

## Staging acceptance

Use a disposable v16 test tenant with Python 3.14 and MariaDB. Install and migrate on both
a fresh tenant and an existing tenant. Keep tests disabled on production sites.

Verify:

- Desktop icon, sidebar, Workspace shortcut, and Page load on the actual v16 image.
- Contextual help appears on all six supported forms and filters the library correctly.
- Search matches titles, keywords, and written instructions; categories filter results.
- Role-limited staff see only relevant guides/paths and cannot confirm company setup.
- Website users/guests cannot call endpoints; learning progress cannot target another user.
- Generic REST GET/list cannot expose another user's progress or another company's setup;
  normal users cannot mutate managed records through generic APIs.
- Two companies have separate confirmations; selecting an inaccessible company is rejected.
- Draft, cancelled, return, and other-company invoices do not qualify.
- Draft, outgoing, unallocated, zero-allocation, and other-company payments do not qualify.
- A submitted customer receipt allocated to an invoice qualifies.
- Repeated/concurrent confirmations and lesson completion do not produce duplicate rows.
- Reopening completed lessons does not reset completion; content upgrade preserves progress.
- Video controls only appear with a real ID; text containing HTML is displayed safely.
- Mobile layout and keyboard actions remain usable.

Run the included real integration suite. Its two-company check needs two test companies
and must not be skipped for rollout acceptance. Expand transaction fixtures to cover the
manual evidence cases above on the actual pinned image.

## Provisioning integration

In the existing platform, publish the app repository on branch `version-16`, add it to
the workload image's app catalog, and rebuild/stage the image. Add a Control Plane App row
with `frappe_app_name=royce_learn`, `required_apps=["erpnext"]`, initially non-ready. After
acceptance, mark it ready and include it in the selected plans. The existing dependency
sort and per-app installation loop can install it without a separate baseline operation.

These platform changes have not been applied by this app build. For existing customers,
install and migrate the app per tenant using the validated upgrade process; adding it to
a plan does not itself install it on existing sites.

## Release

Record a tested image/repository revision, take backups, deploy to a small canary group,
verify actual user flows, then expand. Do not set the app as every user's home page until
that navigation behavior has been deliberately tested and approved.

## Recovery

If a canary fails, remove customer navigation exposure and revert to the previously tested
app revision/image, then rebuild assets and migrate as appropriate. Preserve the Learn
tables and progress while investigating. App uninstall removes its DocTypes/data; it is
not a data-preserving rollback. Use backups if a destructive uninstall or restore is needed.
