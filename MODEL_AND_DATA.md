# Models, training data, and disclosure boundary

The final population was generated with the public OmegAMP diffusion model. The
official HydrAMP starter library was evaluated as an independently structured
generator family, but did not pass the frozen robust promotion gate.

## Generative model

The OmegAMP source, configuration, training/inference instructions and actual
checkpoint are included under `vendor/omegamp/`. Its distributed generative
training snapshot is included under `training_data/omegamp_generative/`. It
combines AMP positives assembled upstream from AMPScanner, dbAMP and DRAMP with
a broader Peptipedia-derived peptide pool.

The vendored upstream repository declares the MIT license in
`vendor/omegamp/LICENSE` and its package metadata; a copy is retained as
`licenses/OMEGAMP_LICENSE`. Source database names are provenance, not claims
that this repository independently relicenses whole upstream databases.

The checkpoint exceeds GitHub's ordinary single-file limit and is tracked by
Git LFS. Run `git lfs pull` before research-time OmegAMP inference. The
lightweight frozen submission command does not load this checkpoint.

## Public selection models

Candidate selection used broad AMP activity and five target-species tasks. Each
task was trained with three fixed identity-aware split seeds (17, 29, 43). The
incumbent branch combines standardized class-balanced logistic regression with
class-balanced histogram gradient boosting. The independent public challenger
uses a frozen `facebook/esm2_t12_35M_UR50D` residue representation and a
class-balanced linear head. Both use calibration fitted only on tuning data.
Final utilities use a fixed 50/50 fusion after candidate-population percentile
normalization.

`models/public_activity/` contains the 18 incumbent artifacts and
`models/public_esm/` the 18 ESM2 heads. The disclosed fitting snapshot is
`training_data/public_activity/public_activity_training_table.parquet`.
`scripts/score_public_esm.py` is the readable heavy inference path; it requires
PyTorch, Transformers, pandas, joblib and scikit-learn. The distributed heads
were serialized with scikit-learn 1.6.1.

## Source-use matrix

| Source or artifact | Role in this release | Distributed here |
|---|---|---|
| OmegAMP public release | Generator, checkpoint, code and upstream training snapshot | Yes, with upstream MIT license |
| AMPScanner, dbAMP, DRAMP | Upstream provenance of OmegAMP AMP positives | Through the OmegAMP snapshot, not as separately rebuilt databases |
| Peptipedia | Upstream provenance of the broad OmegAMP peptide pool | Through the OmegAMP snapshot |
| Public activity table | Broad AMP and five species labels plus fitting/control roles for the released selection heads | Yes, as Parquet |
| UniProt-derived, random, shuffled and mutated negatives | Specificity controls and fitting negatives as marked in the table | Yes where used by the released heads |
| Signal and metabolic peptides | Locked negative controls only | Yes where present; never used for fitting |
| Official antibacterial reference | Exact-overlap and Top100 similarity validation only | Yes, copied from the official repository |
| HydrAMP starter | Frozen generator-family challenger; not promoted into G6 V5 | Not required by the final materialization path |
| DBAASP, GRAMPA and APD6 audit copies | External provenance, held-out testing, or novelty audits | Not copied wholesale into this repository |
| Hidden challenge labels or private data | Not used | No |

The HydrAMP template's database list describes that example system's
provenance; it is not treated as a requirement to concatenate every named
database. Bulk records with unresolved assay units, duplicate publications,
chemistry, or redistribution terms were not silently added to training.

The OmegAMP optional `secret_data` path was disabled. Signal and metabolic
peptides were locked controls and never fitting rows. Restricted research models
and hidden challenge labels were not used to select the Full Track release.

## Reproducibility boundary

`uv run generate` deterministically materializes the frozen release files. This
keeps the official entry point lightweight and byte-stable. It is not presented
as a fresh diffusion-training run. The code, weights, data snapshot and model
inference instructions needed to inspect the research lineage are separately
disclosed above.
