---
status: testing
phase: 02-organizer-scoped-assignments
source: [02-SUMMARY.md]
started: 2026-04-22T14:50:00Z
updated: 2026-04-22T14:50:00Z
---

## Current Test
<!-- OVERWRITE each test - shows where we are -->

number: 1
name: Coordinator Listing and Management UI
expected: |
  Log in as a Sub-Admin (Organizer). Open the "Manage" modal for a hackathon and switch to the "Coordinators" tab. Verify that any already-assigned coordinators are listed with their emails and responsibility badges, and that a "Remove" button is visible for each.
awaiting: user response

## Tests

### 1. Coordinator Listing and Management UI
expected: Log in as a Sub-Admin (Organizer). Open the "Manage" modal for a hackathon and switch to the "Coordinators" tab. Verify that any already-assigned coordinators are listed with their emails and responsibility badges, and that a "Remove" button is visible for each.
result: pending

### 2. Assignment with Granular Responsibilities
expected: Using the assignment form in the "Coordinators" tab, enter a user's email and check specific responsibility boxes (e.g., "Problems", "Analytics"). Click "Assign" and verify the user is added to the list with the correct badges, and a success toast appears.
result: pending

### 3. Coordinator Unassignment
expected: Click the "Remove" (user-minus icon) button next to a coordinator in the list. Confirm the prompt. Verify the coordinator is removed from the list and a success toast appears.
result: pending

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0

## Gaps

