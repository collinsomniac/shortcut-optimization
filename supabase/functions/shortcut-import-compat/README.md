# shortcut-import-compat

Public **test-only** delivery endpoint for the iOS Shortcut import compatibility
matrix.

Security model:
- no database access;
- no service-role secret;
- no arbitrary URL proxy;
- fixture names must exist in the source-controlled
  `public/shortcut-import-compat/manifest.json`;
- downloaded bytes must match the manifest's exact byte count, SHA-256 and
  `AEA1` magic before they are returned.

The function is intentionally deployed with `verify_jwt=false` because the
fixtures are generic, non-sensitive public test artifacts. Never put private
Shortcut contents, credentials or user-specific data in this matrix.

Request:

~~~text
GET /functions/v1/shortcut-import-compat?name=<fixture-slug>
~~~

Response on success uses `application/x-apple-shortcut` and an attachment
filename so the transport matches the previously successful
`shortcut-public-artifact` path as closely as practical.
