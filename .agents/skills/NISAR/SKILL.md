---
name: nisar-cab-automation
description: 'Interact with NISAR at https://nisar.niaid.nih.gov/ for CAB request creation, field population, and CAB ID capture. Use when the user asks to open, fill, validate, or troubleshoot NISAR CAB forms. Requires NIAID network or VPN access.'
---

# NISAR CAB Automation Skill

Use this skill when working with NISAR CAB workflows in this repository.

## General Context

- Production Deployment Requests (DRs) originate in Jira.
- DR records contain CAB details that must be transcribed into NISAR CAB requests.
- NISAR organizes CAB requests by system.
- The correct system must be identified from the Jira DR before creating/submitting the NISAR CAB request.

## NISAR Instance

- CAB landing page: `https://nisar.niaid.nih.gov/CAB/ManageCabReq.aspx`
- CAB form page (new request): `https://nisar.niaid.nih.gov/CAB/CabReq.aspx?Id=0`
- CAB view page (existing request): `https://nisar.niaid.nih.gov/CAB/ViewCab.aspx?Id=<CAB_ID>`

## Scope

Use for:
- Verifying NISAR access from the current environment
- Opening the CAB form and validating required fields
- Mapping Jira CAB data to NISAR form fields
- Applying DR-to-system mapping so the CAB request is created under the correct NISAR system
- Populating NISAR fields through Selenium automation
- Capturing generated CAB ID after submission
- Reporting field-level population status and errors

Do not use for:
- Auto-submitting CAB forms without user review
- Bypassing manual validation or approval steps
- Running NISAR automation when VPN/network access is unavailable

## Access and Safety Rules

1. NISAR is internal; confirm NIAID network or VPN connectivity first.
2. Keep submit action manual by default unless explicitly requested.
3. Never log secrets or sensitive tokens.
4. If URL resolution fails (`ERR_NAME_NOT_RESOLVED`), report network/VPN prerequisite.

## Workflow

1. Load config and confirm NISAR URLs.
2. Resolve target NISAR system from Jira DR metadata and mapping rules.
3. For existing DR-to-system lookup, fetch Jira CAB ID (`customfield_10917`) and open `ViewCab.aspx?Id=<CAB_ID>`.
4. Read NISAR system values from `Change Item(s) *` and `Change Items (System)` fields.
5. If system resolution is ambiguous, stop and request user confirmation.
6. Navigate to CAB landing page.
7. Open CAB request form.
8. Validate expected form fields (XPath checks).
9. Populate fields from mapped source values.
10. Pause for user review and manual submit.
11. Detect submit completion by URL change.
12. Extract CAB ID from redirect URL when available.
13. Return structured success/failure summary.

## Field Mapping Guidance

- Prefer central mappings from `main.py`:
  - `XPATH_FIELDS`
  - `JIRA_TO_XPATH_MAP`
- Keep mapping changes centralized and deterministic.
- Preserve existing checkbox/radio fallback behavior (label click, JS fallback).

## Error Handling Checklist

- `ERR_NAME_NOT_RESOLVED`: missing VPN/network route
- `401 Unauthorized` on `ViewCab.aspx`: unauthenticated HTTP session; use authenticated browser session
- Unknown or ambiguous DR-to-system mapping: halt and request explicit system selection
- Missing required XPath field: stop and report field list
- Selenium element state failures: retry with label or JS fallback
- Form launch failures: stop and report exact interaction step
- CAB ID not found post-submit: report as submitted-without-id

## Completion Criteria

A NISAR task is complete when:
1. Required fields are present or missing fields are reported.
2. Field population results are logged per field.
3. User had a review step before submission.
4. Submission outcome is clear (`skipped`, `submitted`, or `CAB ID captured`).
5. Any errors include actionable context and next step.
