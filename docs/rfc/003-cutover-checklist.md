# RFC-003: Production Cutover Checklist

## Pre-cutover
- [ ] Parity tests green against legacy and target APIs
- [ ] SQLite -> Postgres migration dry-run completed
- [ ] Row-count and checksum verification completed
- [ ] Staging load test meets latency/error SLO
- [ ] Rollback playbook approved

## Cutover Day
- [ ] Freeze schema changes
- [ ] Final data sync window started
- [ ] Switch read traffic to target API (10%)
- [ ] Validate error rate + p95 latency
- [ ] Increase traffic 10% -> 50% -> 100%

## Post-cutover (24–72h)
- [ ] Monitor incident dashboard and alerts
- [ ] Validate background jobs/queues
- [ ] Confirm analytics/event integrity
- [ ] Keep legacy stack warm for rollback window

## Rollback Triggers
- [ ] Error rate > agreed threshold for 15 min
- [ ] p95 latency breach > agreed threshold for 30 min
- [ ] Data inconsistency detected in critical tables

## Rollback Steps
- [ ] Route traffic back to legacy service
- [ ] Pause target writes
- [ ] Capture diagnostics and timeline
- [ ] Postmortem and remediation plan
