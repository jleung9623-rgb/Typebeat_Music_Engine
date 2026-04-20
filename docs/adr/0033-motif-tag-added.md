# Architectural Decision Record 0033 - Schema Expansion for Higher-Order Stochastic Navigation

## Module: database/models.py
## Tags: #SCHEMA, #STOCHASTIC-LOGIC, #DATA-INFLOW
## Status: Accepted

### Context
The transition matrix previously relied entirely on explicit motif-to-motif integer mapping. This strict mapping prevents the Markov Engine from traversing broader semantic categories or executing grouping logic, which is a mathematical requirement for second-order stochastic generation.

### Decision
Injected the `motif_tag` column into the `Motif` table.

* **Tag Mapping**: Enables transitions_upload.py to map transition probabilities to tagged groups rather than relying strictly on individual motif IDs.

### Consequences
* **Scalability**: Radically increases matrix entropy without causing relational database bloat.

* **Overhead**: Introduces a new required metadata field that must be calculated and validated during the extraction phase, increasing ingestion pipeline cyclomatic complexity. However, it was found to be required for streamlining motif groupings to be used in generating higher-order Markov Chains.