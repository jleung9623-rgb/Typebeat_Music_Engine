# Architectural Decision Record 0036 - Pre-Memory Scale Sanitization

## Module: engine/data_initialization.py
## Tags: #DATA-INITIALIZATION, #MEMORY-SAFETY, #STRING-SANITIZATION
## Status: Accepted

### Context
Interval string data utilized for harmonic mapping is highly volatile when fetched from raw CSVs or external initializations, carrying a high probability of trailing spaces, rogue characters, or malformed arrays.

### Decision
Implemented a  *data sanitization block* to remove all commas from the scale interval string before using a list comprehension to consolidate all the interval numbers into a grouping.

* **Pre-Fetch Cleansing**: Cleanses scale interval strings at the exact point of fetching, converting them into a viable format prior to memory allocation.

### Consequences
* **Execution Safety**: Prevents fatal runtime errors within the transposition math by guaranteeing the interval array is clean before the harmonic_analyzer attempts to process it.

* **Data Loss Risk**: Radically anomalous formatting in the source data will be aggressively stripped, potentially resulting in an empty or mathematically invalid array if the source is fully corrupt.