# Royce Learn

Tenant onboarding and contextual learning for **Frappe/ERPNext version 16**.
Version 0.1.0: implementation candidate; staging acceptance is required before production.

## Included

- Getting Started dashboard with a company selector and separate company checklists.
- Company-specific submitted sales invoice and allocated customer payment evidence.
- Explicit confirmations for company details, team access, shared item/customer masters,
  and opening balances; opening balances can be marked not applicable with a reason.
- Per-user learning progress, ordered learning paths, and full-text guide search.
- Nine packaged written guides, with optional YouTube video references.
- Contextual help on Company, User, Customer, Item, Sales Invoice, and Payment Entry.
- v16 Workspace, Workspace Sidebar, and Desktop Icon metadata.
- Server-side app/permission gating, including generic Frappe document/list access.

Subscription billing, Astro synchronization, quizzes, email reminders, industry-specific
templates, central analytics, and AI assistance are not part of this release.

## Installation on a staging bench

Use Python 3.14 to match the existing Royce app baseline. Frappe and ERPNext must both be v16.
Add this repository to the bench using its actual repository URL once published:

```sh
bench get-app --branch version-16 <actual-royce-learn-repository-url>
bench --site <staging-site> install-app royce_learn
bench build --app royce_learn
bench --site <staging-site> migrate
bench --site <staging-site> clear-cache
```

Open Royce Learn from the Desk, or navigate to the `royce-learn` Page.
Installation seeds content; it does not modify ERP business data or override the user's home page.
Company checklists are derived on demand, so existing and newly provisioned companies work
without an additional tenant bootstrap command. Confirmations are persisted when completed.

See [production rollout](docs/production-rollout.md), [architecture](docs/architecture.md),
and [content maintenance](docs/content-maintenance.md).

## Verification

Local fast checks:

```sh
python -m unittest discover -s tests -v
python -m compileall -q royce_learn
node --check royce_learn/public/js/contextual_help.js
node --check royce_learn/royce_learn/page/royce_learn/royce_learn.js
```

Real v16 integration tests on a disposable staging site:

```sh
bench --site <test-site> set-config allow_tests true
bench --site <test-site> run-tests --app royce_learn --module royce_learn.royce_learn.test_integration
```

The local environment has no Frappe bench; the integration suite and live UI checks have
not been run here. Local Python syntax/unit checks passed on Python 3.14.3, and Ruff passed.
Do not treat local checks as production acceptance.

License: MIT, consistent with the existing Royce app repositories.
