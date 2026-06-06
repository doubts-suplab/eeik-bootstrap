# RCA Tracker

> Tracks production incidents and their Root Cause Analysis status. Updated by the `incident-handler` and `rca-agent` agents after each incident.

---

## Active Incidents

<!-- Incidents currently open or in RCA -->

| Incident | Severity | Status | Declared | RCA Due | Owner |
|----------|---------|--------|----------|---------|-------|
| None currently active | | | | | |

---

## Completed RCAs

| Incident | Severity | Duration | Root Cause Summary | Corrective Actions | Closed |
|----------|---------|----------|-------------------|-------------------|--------|
| None yet | | | | | |

---

## Corrective Action Tracker

Track all open corrective actions across all past incidents:

| Ref | Incident | Action | Owner | Due Date | Status |
|-----|----------|--------|-------|----------|--------|
| None yet | | | | | |

---

## Incident History

<!-- Full incident records are linked here once RCA is complete -->

<!-- Format:
### INCIDENT-NNN: {Title}
**Date:** YYYY-MM-DD
**Severity:** P1/P2/P3
**Duration:** Xh Ym
**Services:** {affected services}
**Root Cause:** {one-line summary}
**RCA Document:** `docs/rca/INCIDENT-NNN.md`
**Corrective Actions:** {N} open / {N} closed
-->

---

## SLA Targets

| Severity | Time to Acknowledge | Time to RCA Publication |
|----------|--------------------|-----------------------|
| P1 | < 5 minutes | < 48 hours post-resolution |
| P2 | < 15 minutes | < 72 hours post-resolution |
| P3 | < 4 hours | < 1 week post-resolution |
