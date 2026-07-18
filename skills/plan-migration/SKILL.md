---
name: plan-migration
description: Use when an agent needs to plan a safe data migration or database schema change; sequences the change into backward-compatible expand/backfill/contract phases with rollback and verification steps rather than executing SQL scripts or migrating data.
---

# Plan Migration

Use this skill to plan a database schema change or large-scale data migration when the user asks for one. The plan's coherence comes from the Expand/Contract pattern (Section 2): every intermediate state stays readable and writable by the running application, so the schema can change with zero downtime.

**Input**: the current schema/state and the target schema/state. The current state can often be discovered by reading migration files or schema definitions already in the repo — ask the user for it only when it cannot be located, along with the database engine and scale context if those are unclear.

**Boundary**: Produces a step-by-step migration and rollback plan; does not execute SQL scripts, alter schemas, or migrate data. Hand the phased plan to plan-implementation to turn it into ordered coding steps, and to plan-testing to design the data-integrity verification strategy.

## Workflow

### 1. State Analysis
Compare the current database schema/state with the desired target schema/state. Identify any breaking changes, such as renaming columns, changing data types, or deleting tables.

### 2. Plan Migration Steps (Expand/Contract Pattern)
Design the migration using the zero-downtime Expand/Contract pattern:
- **Phase 1: Add (Expand)**: Plan adding the new schema elements (e.g., new column or table) without altering existing ones.
- **Phase 2: Dual Write**: Plan a dual-write step where the application writes to both old and new schema elements simultaneously.
- **Phase 3: Backfill**: Plan a backfill step to move historical data from the old schema to the new schema.
- **Phase 4: Read**: Plan the read-cutover, switching the application to read from the new schema exclusively.
- **Phase 5: Drop (Contract)**: Plan removal of the old schema elements.

### 3. Plan Rollback and Verification
For every phase, define the exact rollback procedure if the migration fails at that phase (for the reversible phases this is typically toggling a flag or reverting a deploy). Treat Phase 5 (Drop) as the point of no return: gate it behind a confirmed read-cutover, retention of a backup/snapshot of the old schema and its data, and a defined un-drop/restore path. Define how the user will verify data integrity after the backfill phase; the full verification strategy is plan-testing's job, so hand that seam off there.
