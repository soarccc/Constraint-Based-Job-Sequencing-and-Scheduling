# Constraint-Based Job Sequencing and Scheduling

A Python-based scheduling engine that maximizes net profit by assigning time-constrained jobs to discrete time slots while adhering to resource limits, category rules, and dependencies.

Developed for **ENCS3130: Linux Laboratory** at **Birzeit University**.

---

## Overview

This project implements a greedy constraint-satisfaction algorithm to sequence and schedule jobs defined in an input dataset. The scheduler prioritizes jobs by their calculated **Net Value** and attempts to place them into the latest available consecutive time slots prior to their deadlines.

### Key Features
* **Greedy Scheduling Algorithm:** Prioritizes jobs by `Net Value = Profit + Penalty` with tie-breaking logic based on deadline, duration, and cost.
* **Constraint Validation:**
  * **Dependencies:** Ensures prerequisite jobs finish before dependent jobs start.
  * **Category Restrictions:** Limits consecutive or adjacent slot allocations for identical job categories.
  * **Budget & Cost Limits:** Enforces maximum available resource constraints.
* **Data Parsing & Error Handling:** Validates `jobs.txt`, rejecting duplicate IDs, invalid types, circular dependencies, or impossible durations.
* **Automated Reporting:** Prints the detailed execution summary to the console and exports a formatted log to `output/result.txt`.

---

## Input File Format (`jobs.txt`)

The input file contains whitespace-delimited records in the following format:

```text
job_id deadline profit duration penalty depends_on category cost
