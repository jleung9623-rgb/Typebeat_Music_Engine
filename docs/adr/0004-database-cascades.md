# Architectural Decision Record 0004 - Database Cascade Casings

## Tags: #DB-INT
## Status: Accepted

### Context
Deleting core entities (Tracks or Artists) left orphaned rows in junction tables, leading to relational drift and potential foreign key constraint crashes during subsequent lookups.

### Decision
Implement database-level ondelete="CASCADE" on all junction table Foreign Keys. For the compositions table, apply ondelete="SET NULL" for the artist_id to ensure file persistence records are not deleted if an artist is removed from the library.

* **Implemented Code Format**: return {"status": "success" | "error", "message": str(e)}

### Consequences
* **Stability**: Manual cleanup of junction tables is no longer required.
* **Persistence**: Metadata regarding generated MIDI files is preserved even after entity deletion.