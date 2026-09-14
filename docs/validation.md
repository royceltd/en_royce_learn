# Validation record

Local checks completed on 2026-09-14:

- Python 3.14.3: 14 unit tests passed.
- Python compilation passed.
- Ruff lint and format checks passed.
- Node syntax checks passed for contextual help and the learning dashboard.
- v16 primary-source review checked permission-hook argument names, the form refresh
  event, standard sidebar metadata, and stable document naming during insertion.

These unit tests use a Frappe test double for server API behavior. They exercise permission
rejection and evidence query construction; they do not prove database query behavior or
framework installation. Pure catalog tests cover search and metadata validation.

Not run: real Frappe/ERPNext integration suite, fresh/existing tenant installation,
MariaDB execution/concurrency, Python package build, or browser/UI acceptance. No Frappe
bench is installed in the local execution environment. Follow production-rollout.md
before treating this candidate as production-ready.
