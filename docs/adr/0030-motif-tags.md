# Architectural Decision Record 0030 - Motif Tagging Schema Update

## Module: models.py
## Tags: #SCHEMA-DESIGN, #MARKOV-ROUTING, #METADATA
## Status: Accepted

### Context
The baseline transition algorithm required a secondary parameter beyond `SectionClass` to intelligently link corresponding motifs and maintain thematic continuity (e.g., ensuring a "Melancholy" `Verse` maps to a "Melancholy" `Pre-Chorus`).

### Decision
Added a `motif_tag` string column to the `Motif` table.

### Consequences
* **Capability**: Provides the `TransitionBuilder` with the necessary metadata to filter out mathematically valid but musically incoherent paths.

* **Efficiency**: Results in more focused *baseline matrix generation* without requiring complex external NLP or heuristic analysis.