
# AIDLC Command Center

## Purpose

This folder contains the governance instructions and approval
evidence used to support CustomerConnect API delivery.

## Approval Register

File: `approval_register.csv`

Each row records one human decision about a specific artifact
and version.

### Data Dictionary

| Column | Required | Definition |
|---|---|---|
| approval_id | Yes | Unique approval record ID, e.g. APR-001 |
| artifact_id | Yes | Stable identifier of the deliverable |
| artifact_path | Yes | Repository-relative file path |
| artifact_version | Yes | Version reviewed by the human |
| approver_role | Yes | Role authorized to make the decision |
| decision_status | Yes | APPROVED, REJECTED, or NEEDS_REVISION |
| evidence_reference | Yes | Reference to the human decision evidence |
| decision_date | Yes | Decision date in YYYY-MM-DD format |

### Valid Decision Statuses

- APPROVED: Human accepts the specified artifact version.
- REJECTED: Human does not accept the deliverable.
- NEEDS_REVISION: Changes are required before approval.

### Operating Rules

1. One row represents one decision about one artifact version.
2. Do not change a REJECTED or NEEDS_REVISION record to
   APPROVED. Record a new decision instead.
3. Approval requires review of the complete artifact.
4. Only an authorized human can make the approval decision.
5. An artifact change after approval requires renewed review
   before the changed version is treated as approved.
6. Never create an approval record based solely on AI judgment.
7. Never invent decision evidence or dates.
8. Reference only non-sensitive evidence suitable for GitHub.

### Initial Approval Example

APR-001 records the Product Owner's approval of
AI_OPERATING_INSTRUCTIONS.md version 1.0 during M1.2 Task 2.

The current evidence reference points to the project conversation.
It is not yet a permanent, independently verifiable GitHub link.

### Validation Boundaries

The future Python approval validator will check:
- Required columns and non-empty fields
- Allowed decision status values
- Required artifact file existence
- Matching artifact version and approval record
- Presence of an evidence reference

The validator cannot independently prove:
- The approver's identity
- Whether the human fully understood the artifact
- Whether the decision was appropriate
- Whether a conversation reference is authentic

Human review remains mandatory.

## Related Files

- `AI_OPERATING_INSTRUCTIONS.md`: AI roles, guardrails,
  deliverable requirements, and approval rules.
- `approval_register.csv`: Human decision records.
