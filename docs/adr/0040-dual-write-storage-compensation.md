# Architectural Decision Record 0040 - Distributed Dual-Write and Compensating Transactions

## Module: data_inflow/motifs_upload.py
## Tags: #DUAL-WRITE, #DISTRIBUTED-TRANSACTIONS, #ACID-COMPLIANCE
## Status: Accepted

### Context
Typebeat operates a polyglot database architecture. Vector generation (`typebeat_embedding_model.pt`) and spatial indexing (Qdrant) must execute in parallel with deterministic relational storage (*MySQL*). Because these databases are isolated, a failed SQL insertion (e.g., missing foreign key, data type mismatch) after a successful Qdrant upsert leaves a "ghost vector" in the spatial index—a geometric coordinate pointing to a non-existent relational row. This desynchronization would fatally crash the Markov generation engine when it attempts to look up the physical notes.

### Decision
Engineered a Compensating Transaction protocol within the `upload_batch` extraction loop. The pipeline enforces a rigid execution order:
1. Generate tensor embedding (`embed_neurosymbolic_coordinate`).
2. Upsert to Qdrant via `PointStruct`, binding the coordinate to a generated `shared_vector_id` and injecting the `motif_class` as a payload for future semantic filtering.
3. Execute SQL transaction.
If the SQLAlchemy session throws an error, the exception block immediately executes `qdrant.delete()`, targeting the identical `shared_vector_id` to systematically purge the orphaned vector from the spatial index before raising the exception up the stack.

### Consequences
* **State Synchronization**: Guarantees that the relational taxonomy and the geometric index remain mathematically aligned during mass ingestion.
* **Deferred Fault Tolerance**: If the Qdrant instance crashes immediately after the primary upsert but before the compensation can execute, the ghost vector becomes permanent. This technical debt is accepted, shifting the fault tolerance burden to the read-phase (Markov Engine must query with `limit=3` and silently drop null SQL returns).
* **Namespace Optimization**: Redundant arrays (`numpy`) were structurally purged from the pipeline, streamlining the memory footprint during inference passes.