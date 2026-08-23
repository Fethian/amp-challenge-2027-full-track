# Robust public-data antimicrobial peptide design with identity-aware model ensembles

## Abstract

We present a deterministic 50,000-member antimicrobial peptide design library
and a robustly ranked Top100 for the AMP Challenge 2027. Our aim was not to
maximize a single surrogate score, but to construct a portfolio that remains
competitive when model seed, target species, sequence novelty, and
out-of-distribution behavior are varied. We rebuilt broad and species-specific
activity models from disclosed public data with the optional secret-data path
disabled, separated related sequences with 30% identity clustering, and scored
a frozen population of 117,957 exact-unique candidates. A preregistered frozen
ESM2 challenge improved locked AUROC on all 18 task-seed evaluations and was
therefore fused with the composition models at a fixed 50/50 weight. We also conducted a
preregistered generator-family challenge between OmegAMP and HydrAMP. The
mixed-family branch satisfied every sequence, diversity, and novelty constraint
but underperformed OmegAMP-only on both the mean and lower tail of the random25
robustness test. We therefore retained the OmegAMP branch. The released library
contains 50,000 exact-unique sequences from 50,000 identity clusters. Its Top100
contains 100 identity clusters, has no identity30 overlap with classifier
training sequences, has maximum reference similarity 0.778, and passes the
official sequence validator. These results establish public-data surrogate
quality and reproducibility, not measured antimicrobial efficacy or safety.

![Public-model and portfolio results](figures/public_model_and_portfolio_results.png)

## 1. Motivation

Antimicrobial peptide generation is a multi-objective problem. A candidate must
be plausible under imperfect activity models, remain sufficiently novel, avoid
obvious sequence pathologies, and contribute to a portfolio that survives the
challenge's random sampling of 25 peptides from the submitted Top100. Optimizing
one model or one mean score can instead concentrate the library around a narrow
sequence family and amplify surrogate-model error. We therefore treated final
selection as robust portfolio construction under several deliberately different
public evidence surfaces.

Our development process also separated scientific negative results from
engineering and disclosure constraints. Earlier experiments showed that ESM2
LoRA variants for quantitative MIC did not improve their frozen baseline, a simple ANKH–ESM2 rank
consensus did not generalize across source-held-out folds, a quantitative HC50
head was not reliable enough to rank safety, and trust-region generation failed
its preregistered elite-regret gate. Those branches were stopped rather than
repeated until a favorable result appeared. Those failures did not test the
later public-label ESM2 classifier, which used different labels, an independently
frozen protocol, and no backbone updates.

## 2. Public data and candidate population

The public activity table was reconstructed from the disclosed OmegAMP activity
materials. After sequence validation, canonicalization, and exact-label conflict
removal, it contained 322,267 unique sequences in the challenge domain. Broad
AMP positives came from the curated public AMP set. Curated non-AMP peptides,
UniProt-derived non-AMP sequences, and fixed random, shuffled, and mutated
decoys supplied fitting negatives. Signal and metabolic peptides were reserved
as locked controls and never entered model fitting. Species-specific positives
were available for *Acinetobacter baumannii*, *Escherichia coli*, *Klebsiella
pneumoniae*, *Pseudomonas aeruginosa*, and *Staphylococcus aureus*.

The frozen candidate population contained 117,957 exact-unique sequences:
67,957 public OmegAMP diffusion candidates and the 50,000 sequences distributed
with the official HydrAMP starter. The two families had no exact cross-family
overlap. Twenty candidates that exactly matched public classifier training
sequences were excluded from final-library eligibility. The official
antibacterial reference was used only for novelty checks and was not treated as
a source of candidate labels.

The database names in the HydrAMP example submission are descriptions of that
starter's training provenance rather than a mandatory checklist. Our public
branch therefore used each source according to a defined role. DBAASP, DRAMP,
dbAMP, APD/APD6, GRAMPA, AMP Scanner, Peptipedia, and UniProt appear in upstream
training snapshots or novelty audits, but we did not concatenate every database
into a single positive table. In particular, bulk DBAASP records were not added
without assay and unit harmonization, duplicate-publication handling, chemistry
review, and redistribution review. Likewise, DRAMP/Hemolytik hemolysis records
were not converted into unsupported safety labels.

## 3. Identity-aware public activity models

We trained six binary activity tasks with three fixed seeds, producing 18
models. Each model averaged two low-capacity learners over sequence composition
and physicochemical features: standardized class-balanced logistic regression
and class-balanced histogram gradient boosting. A logistic calibrator was fit
only on the tuning partition. The features described length, net charge density,
hydrophobic and aromatic fractions, residue composition, local half-sequence
composition, entropy, and repeat behavior.

To reduce sequence-family leakage, MMseqs2 clustered the union of training and
candidate sequences at 30% identity and 80% coverage. Each seed assigned whole
clusters, rather than individual rows, to 70% fitting, 15% tuning, and 15%
locked evaluation partitions. Candidate sequences sharing an identity cluster
with public training data were explicitly marked and later forbidden from the
Top100.

Across the 18 locked evaluations, incumbent AUROC ranged from 0.815 to 0.887. The
signal/metabolic controls had mean predicted activity between 0.004 and 0.028,
with essentially no predictions above 0.5. The models therefore supplied a
useful public ranking surface without suggesting that their probabilities were
MIC values, safety measurements, or official hidden-label probabilities.

We then challenged this surface with the public frozen
`facebook/esm2_t12_35M_UR50D` backbone. Mean-pooled residue representations were
concatenated with the same 72 public sequence features and fitted with a
class-balanced linear head; only the head and tune-only calibrator were trained.
The fusion weight and promotion thresholds were fixed before representation
extraction. The 50/50 fusion improved AUROC in all 18 locked evaluations: the
median gain was 0.0607, the smallest individual gain was 0.0405, and the six
task-average gains ranged from 0.0475 to 0.0673. Locked-control behavior remained
inside the preregistered tolerance, so the ESM branch was promoted.

The strong 35M result motivated one additional preregistered capacity challenge:
we replaced it with frozen ESM2-150M while holding the rows, split, head,
calibration, fusion weight, controls, and candidate population fixed. The larger
backbone did not pass its replacement gate. Median fused AUROC improvement over
35M was only 0.0018; the worst individual change was −0.0110, and mean changes
for *A. baumannii* and *K. pneumoniae* were −0.0044 and −0.0043. We therefore
retained ESM2-35M rather than assuming that greater model capacity implied a
more robust public ranking surface.

We also tested whether the fixed fusion should place more weight on ESM2-35M.
Because the original locked results could not legitimately tune that choice, we
used three entirely new identity-cluster split seeds and divided each tuning
partition into separate calibration and weight-selection halves. Unconstrained
tuning selected ESM weights of 0.75 or 1.0 in 17 of 18 evaluations and improved
new locked AUROC by a median 0.0040, but maximum locked-control FPR increased
from 0.0032 to 0.0207. A final experiment on a third set of fresh split seeds
allowed non-default weights only when ordinary tuning negatives preserved FPR
and mean-probability tolerances. It selected the default 0.5 in 13 of 18 cases,
produced zero median locked gain, and still increased maximum locked-control FPR
from 0.0036 to 0.0080. Neither weighting challenge passed its preregistered
gate, providing independent support for retaining the fixed 50/50 fusion.

## 4. Robust library and Top100 selection

For every task and split seed, incumbent and ESM scores were separately
converted to empirical candidate-population percentiles and then averaged 50/50.
All remaining continuous candidate signals were converted to empirical percentiles over
the complete frozen population, preventing a low-base-rate species model from
dominating merely because its calibrated probabilities had a smaller numerical
range. Four fixed scenarios stressed different failure modes. The balanced
scenario combined broad activity, worst-species activity, across-species mean,
seed stability, descriptor transport, and training-cluster novelty. The
species-adversarial and broad-adversarial scenarios increased the weight of the
corresponding weakest activity evidence. The transport scenario emphasized
distance from the public AMP descriptor distribution, sequence complexity, and
novelty from training clusters. Descriptor distance was measured with a
Ledoit–Wolf shrinkage Mahalanobis model fit only on disclosed curated AMP
positives.

Candidates were ordered lexicographically by their worst scenario, the average
of their two worst scenarios, and their mean utility. The 50,000-member library
required valid challenge sequences, exact uniqueness, no exact match to public
training or official reference sequences, and at most one member per identity30
cluster. The Top100 added stricter complexity and public-AMP descriptor
envelopes, zero identity30 overlap with classifier training, at most 15
OmegAMP sequences from one generation seed, maximum Levenshtein similarity
0.78 to the official reference, and maximum internal pairwise similarity 0.80.

## 5. Generator-family challenge

We compared an OmegAMP-only incumbent with a mixed OmegAMP–HydrAMP challenger on
the same frozen model surface and constraints. The mixed 50,000 library
contained 22,293 OmegAMP and 27,707 HydrAMP sequences. Its Top100 contained 65
OmegAMP and 35 HydrAMP candidates. Both branches had 50,000 identity clusters in
their full libraries and 100 identity clusters in their Top100 lists, and both
passed all reference, internal-similarity, complexity, family, and generation-
seed constraints.

The promotion decision used 10,000 fixed-seed draws of 25 peptides from each
Top100. For OmegAMP-only, the weakest-scenario mean was 0.8209, with P10 0.8182
and P01 0.8162. For the mixed branch, the corresponding values were 0.8096,
0.8037, and 0.7990. Thus the mixed branch was lower by 0.0114 in mean and 0.0145
at P10. Because promotion required a non-negative P10 difference and at least a
0.005 mean improvement, HydrAMP was not promoted.

This is a useful negative result rather than evidence that HydrAMP sequences
are inactive. HydrAMP contributed genuinely different sequence geometry and
passed every structural constraint, but that additional diversity did not
improve the frozen public robustness objective. The result also did not alter
the earlier research-only ANKH/ESM2 findings because those models were not read
by this selection pipeline.

## 6. Final library and validation

The final public-data candidate is therefore the OmegAMP-only branch. Its full
library contains 50,000 exact-unique sequences and 50,000 identity30 clusters.
The Top100 contains 100 exact-unique sequences and 100 identity30 clusters. No
Top100 sequence shares an identity30 cluster with the public classifier
training table. Maximum similarity to the official antibacterial reference is
0.778, and maximum internal Top100 similarity is 0.698. Relative to the
composition-only selection, ESM fusion replaced 501 members of the 50,000 library
and 55 members of the Top100. Ninety-five of the new Top100 were already present
in the earlier 50,000 library, showing that the main effect was reranking rather
than a wholesale shift of the generated population.

The repository entry point, `uv run generate`, deterministically materializes
`generate/library.fasta` and `generate/top.fasta` with simple ranked identifiers.
Two consecutive local runs produced byte-identical files. The official
validator confirmed 50,000 unique sequences, the standard amino-acid alphabet,
length 8–50, Top100 containment, zero exact overlap between the library and the
official reference, and compliance with the official Top100 similarity limit.

### V7.1 closing audit

Before release we conducted a final fixed-scope challenger audit without adding
new candidate pools or changing the five promotion gates. Six additional
generator-ratio portfolios were compared with G6 V5. The original generator
challenge retained its preregistered 10,000-draw decision; the closing audit
used 100,000 Random-25 draws to estimate mean, median, P01/P10/P90/P99, one-draw
failure probability, and pairing sensitivity. It also evaluated selection-aware
external APEX and HemoPI2 deltas, family leave-one-out stability, and public
endpoint diagnostics.

Frozen ESM2 and ANKH HC50/selectivity heads were applied to the complete
344-sequence union and to every Random-25 scheme. HemoPI2 was treated as a
separate hemolysis diagnostic rather than a substitute for the official
HC50/MIC endpoint. These endpoint models are imperfect public surrogates, so
they were not used post hoc to redefine the selection rule or certify safety.
Every challenger failed at least the frozen external-evidence and safety gates;
the closing decision therefore retained G6 V5 unchanged.

## 7. Limitations and claim boundary

The central limitation is that official candidate labels and wet-lab
measurements were unavailable. Identity-aware public holdouts reduce but do not
eliminate dataset shift, source bias, or surrogate exploitation. The public
models predict sequence labels rather than strain-resolved MIC under controlled
assay conditions. We also lack a quantitatively reliable HC50 or hemolysis model;
consequently, no candidate is described as safe. The proposed Top100 should be
interpreted as an experimentally prioritized, diverse portfolio rather than a
set of validated therapeutics.

Future improvements should focus on standardized strain-level MIC records,
assay-context modeling, reliable negatives, and experimentally measured
hemolysis or cytotoxicity. These additions are more likely to change decision
quality than repeatedly adding overlapping AMP-positive databases. Wet-lab
testing remains the decisive next stage.

## 8. Reproducibility and files

Public project repository:
https://github.com/Fethian/amp-challenge-2027-full-track

The repository includes the deterministic generation entry point, the frozen
50,000 library and Top100, the 18 incumbent public activity models, the 18 public
ESM2 linear heads, the public activity training table, the OmegAMP generative
training snapshot, dependency lock file, and upstream license information. The
Kaggle submission links this public repository and attaches the generated
`library.fasta` and `top.fasta` as project files. The entry point materializes
the frozen audited sequences; research-time generation and model scoring are
disclosed separately and are not misrepresented as part of the lightweight
official command.

The submission makes no claim of hidden-label performance, antimicrobial
activity, low hemolysis, clinical safety, or therapeutic efficacy. Its supported
claims are format compliance, public-data surrogate performance, diversity,
novelty, deterministic reproduction, and transparent negative model selection.
