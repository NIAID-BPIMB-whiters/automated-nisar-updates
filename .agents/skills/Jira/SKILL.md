---
name: jira-niaid
description: 'Interact with NIAID Jira at https://jira.niaid.nih.gov/ for issue lookup, triage, creation, comments, and workflow transitions. Use when the user asks to query Jira issues, create/update tickets, sync CAB metadata, or troubleshoot Jira API calls. Prefer secure auth through environment variables and avoid writing tokens to source files.'
---

# Jira NIAID Skill

Use this skill when working with Jira in this repository, especially for CAB automation workflows tied to NISAR.

## General Context

- Production Deployment Requests (DRs) are created in Jira.
- Each DR contains CAB details data (typically in CAB custom fields/description content).
- Those CAB details must be transcribed into a NISAR CAB request.
- NISAR organizes CAB requests by system, so the DR must be mapped to the correct system before creating the NISAR record.

## Scope

Use for:
- Finding issues by key, JQL, or saved filter
- Reading issue fields (summary, status, assignee, custom fields)
- Extracting CAB details payload from DR records for downstream NISAR population
- Identifying the target NISAR system from DR metadata, text, or mapped rules
- Creating new issues and adding comments
- Updating issue fields (including CAB-related fields)
- Moving issues through workflow transitions
- Validating Jira connectivity and API responses

Do not use for:
- Browser-only UI walkthroughs when API data is sufficient
- Storing or exposing Jira PAT values in code, logs, or commits

## Jira Instance

- Base URL: `https://jira.niaid.nih.gov/`
- REST API root (v2): `https://jira.niaid.nih.gov/rest/api/2`

## Authentication Rules

1. Prefer PAT from environment variable: `JIRA_PAT`.
2. If repository config is used, do not print or commit token values.
3. Always send bearer auth:

```http
Authorization: Bearer <token>
Content-Type: application/json
Accept: application/json
```

## Recommended API Patterns

### 1) Search issues (JQL)

```http
POST /rest/api/2/search
```

Request body:

```json
{
  "jql": "project = CAB ORDER BY updated DESC",
  "fields": ["summary", "status", "assignee", "customfield_10916", "customfield_10917", "customfield_10918"],
  "maxResults": 50
}
```

## CAB Field Map (Known)

- `customfield_10916`: CAB Description (free-text payload used for CAB details extraction)
- `customfield_10917`: CAB ID (write-back field after NISAR CAB creation)
- `customfield_10918`: Requested Presentation Date (primary date attribute for determining whether a DR is going to CAB this week)

## DR to NISAR System Mapping

When users ask which system a DR is mapped to, use this sequence:

1. Query Jira issues and include `customfield_10917` (CAB ID).
2. For each CAB ID, open NISAR view URL:
  - `https://nisar.niaid.nih.gov/CAB/ViewCab.aspx?Id=<CAB_ID>`
3. Read system mapping from NISAR CAB page fields:
  - `Change Item(s) *` (primary change item)
  - `Change Items (System)` (mapped system label/value)

If NISAR direct HTTP calls return `401 Unauthorized`, use an authenticated browser session to read the page. If NISAR cannot be accessed, report that explicitly and provide Jira-side fallback context (for example `customfield_10911` Platform) as a non-authoritative approximation.

When users ask for "DRs going to CAB this week," prefer Jira-side filtering using `Requested Presentation Date` (`customfield_10918`) and statuses such as `Ready to Present` and `Add to NISAR`.

Example JQL:

```jql
status in ("Ready to Present", "Add to NISAR")
AND "Requested Presentation Date" >= startOfWeek()
AND "Requested Presentation Date" <= endOfWeek()
ORDER BY "Requested Presentation Date" ASC
```

### 2) Get issue by key

```http
GET /rest/api/2/issue/{issueKey}
```

Use `fields` query when possible to reduce payload size.

### 3) Update CAB ID (example custom field)

```http
PUT /rest/api/2/issue/{issueKey}
```

Request body:

```json
{
  "fields": {
    "customfield_10917": "CAB-12345"
  }
}
```

### 4) Add comment

```http
POST /rest/api/2/issue/{issueKey}/comment
```

Request body:

```json
{
  "body": "CAB submitted to NISAR. CAB ID: CAB-12345"
}
```

### 5) Transition issue

- List transitions:

```http
GET /rest/api/2/issue/{issueKey}/transitions
```

- Apply transition:

```http
POST /rest/api/2/issue/{issueKey}/transitions
```

Request body:

```json
{
  "transition": {
    "id": "31"
  }
}
```

## Error Handling Checklist

- `401/403`: token invalid, expired, or missing permissions
- `404`: issue key or endpoint incorrect
- `400`: bad field id, invalid transition, or malformed request body
- `429`: rate limited; retry with backoff
- `5xx`: Jira service issue; retry with bounded attempts

## Implementation Guidance for This Repo

- Reuse the existing config keys in `config.json`: `jira_url`, `jira_pat`, `jira_filter_url`, `cab_field`.
- Prefer shared helper functions in `main.py` for HTTP calls.
- Keep field IDs centralized and documented.
- Treat `customfield_10918` (Requested Presentation Date) as the authoritative week-bucket field for CAB scheduling reports.
- For DR-to-system reporting, treat NISAR `ViewCab.aspx` system fields as authoritative; Jira platform data is fallback only.
- Treat system identification as a required step before handing data to NISAR.
- If multiple systems are plausible from the DR, require explicit user confirmation.
- For CAB automation, ensure the `customfield_10917` write happens only after a valid NISAR CAB ID is captured.

## Completion Criteria

A Jira interaction task is complete when:
1. API call returns expected status code.
2. Requested field/issue state actually changed.
3. A concise success/failure summary is printed without leaking secrets.
4. Any failed updates include issue key, HTTP status, and safe error text.
