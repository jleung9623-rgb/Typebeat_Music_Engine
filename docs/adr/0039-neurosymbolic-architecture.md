# Architectural Decision Record 0039 - Neuro-Symbolic Model Architecture and Contrastive Training

## Module: ml/model_architecture.py, ml/train.py
## Tags: #NEURO-SYMBOLIC, #CONTRASTIVE-LEARNING, #DIMENSIONAL-COLLAPSE
## Status: Accepted

### Context
The Markov Engine requires spatial nearest-neighbor traversal to execute continuous, fluid generation logic. Relational databases (*MySQL*) cannot calculate multi-dimensional harmonic similarity across variable-length note matrices. A vector space was required, but relying on an unsupervised neural network (like an Autoencoder) would surrender the spatial geometry to a black box, resulting in vectors clustered by raw mathematical density rather than strict music theory.

### Decision
Constructed a neuro-symbolic bridge utilizing `TypebeatLSTMEncoder` to collapse variable-length sequence matrices `(Batch, Seq_Len, 4)` into static 256-dimensional coordinates. Rejected unsupervised auto-encoding in favor of Contrastive Learning (`TripletMarginLoss`). The spatial topology is now deterministically enforced by the relational logic: the model is penalized until it mathematically pulls harmonically compatible motifs (Positive) toward a baseline (Anchor) while repelling discordant motifs (Negative) in the 256-D vacuum.

### Consequences
* **Harmonic Determinism**: The vector space is strictly governed by human-verified rules, ensuring Qdrant returns musically viable coordinates during generation.
* **Bootstrap Dependency**: Imposes a circular data dependency. Training the network requires populated SQL tables, but SQL insertion requires the generated vectors. Necessitates a multi-phase ingestion protocol: Blind Ingestion (garbage vectors) $\rightarrow$ Relational Training $\rightarrow$ Spatial Reconciliation (overwrite).
* **Hardware Bottleneck**: Training the triplet loader introduces a rigid dependency on GPU (CUDA) infrastructure to prevent severe local processing delays.