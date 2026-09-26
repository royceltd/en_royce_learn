# Content maintenance

## Adding or updating a guide

Edit `royce_learn/content/catalog.json`. Keep existing guide IDs stable. A guide has an ID,
title, summary, category, plain-text body, content version, keywords, estimated minutes,
related DocType, permission requirement, required apps, and optional YouTube video ID.

1. Document the actual feature on the target v16 staging build.
2. Review written instructions against the UI and configuration. Have accounting/payroll
   content reviewed by the responsible domain expert.
3. Add the guide with a new stable ID, or increment its content version when updating.
4. Add its ID to a relevant learning path if appropriate.
5. Supply the 11-character YouTube video ID when a real recording exists. Empty means no video.
6. Run catalog tests, stage the change, and deploy the app update through the normal rollout.

Initial guides are implementation-informed drafts and require staging/content-owner review.
No videos have been recorded or invented.

`catalog.json` is the only source for guides. `build_assets.py` generates the app's Frappe
metadata (DocTypes, the getting-started Page, Workspace, Workspace Sidebar, Desktop Icon) and
never touches the catalog. To change that metadata, edit `build_assets.py` and re-run it; never
edit the generated JSON by hand. `tests/test_generated_assets.py` fails if the two differ.

Sync uses stable IDs and retires removed guides without deleting linked progress. Existing
completion remains valid, with an 'updated since completion' indicator for changed versions.
Learning completion is self-reported; it does not certify understanding or complete setup.

## Future Astro integration

Not implemented in v1. The planned shared feed should use the same guide IDs and schema.
Before integration, define publishing ownership, versioning, authentication where needed,
approved feed hosts, payload limits, validation, and last-known-good behavior. A future sync
must make the imported local catalog the source read by both API and mirrored guide records;
adding a remote URL alone would not switch this release to remote content.

Each tenant should serve validated local content so help remains available during network
outages. No customer ERP data needs to be sent to the public knowledge base.
