# RFC-002: API Compatibility Matrix (Legacy -> Target)

| Domain | Legacy Route | Versioned Legacy | Target Route | Contract Notes |
|---|---|---|---|---|
| Health | `/api/health` | `/api/v1/health` | `/api/v2/health` | Keep `status`, `time` fields stable. |
| Posts List | `/api/posts` | `/api/v1/posts` | `/api/v2/posts` | Maintain default `limit=20`, clamp max 100. |
| Create Post | `/api/posts` (POST) | `/api/v1/posts` | `/api/v2/posts` | Preserve `{ok, post_id}` initially, introduce richer payload behind opt-in header. |
| Create SOS | `/api/sos` (POST) | `/api/v1/sos` | `/api/v2/sos` | Keep `alerting_nearby` status string for compatibility. |
| Incidents | `/api/incidents` | `/api/v1/incidents` | `/api/v2/incidents` | Preserve ordering: newest first. |
| Stats | `/api/stats` | `/api/v1/stats` | `/api/v2/stats` | Preserve count semantics. |
| Events | `/api/events` | `/api/v1/events` | `/api/v2/events` | Keep existing minimal fields. |
| Hostels | `/api/hostels` | `/api/v1/hostels` | `/api/v2/hostels` | Preserve sorting by rating desc. |

## Validation Rules

- Legacy and target responses must pass snapshot comparison for required fields.
- Additional fields are allowed if backward-compatible.
- Error code parity must be preserved for known invalid requests.

## Deprecation Policy

- `/api/*` routes deprecated only after:
  1. 2 release cycles with `/api/v2/*` stable
  2. client migration complete
  3. deprecation notice in docs + response headers
