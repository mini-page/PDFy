# Retention Cleanup Runbook

## Purpose

Ensure retained files and temporary artifacts are deleted according to product policy.

## Default Rules

- Files uploaded with `delete_immediately` should be removed after analysis completion.
- Files uploaded with `temporary_cache` should be deleted when their retention window expires.

## Operational Checks

- Verify cleanup jobs are running on schedule.
- Verify object storage deletion success rates.
- Verify expired scan records are marked consistently.
- Alert on repeated deletion failures.

## Failure Handling

- If object deletion fails, retry with backoff.
- If repeated deletion failures occur, mark the scan for manual review and raise an operational alert.
