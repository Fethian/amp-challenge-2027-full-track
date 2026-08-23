# Frozen library and Top100 selection

The released files are the retained G6 V5 result. No candidate sequence was
changed during repository clean-room preparation.

## Candidate population and scoring

The frozen population contained 117,957 exact-unique sequences: 67,957 public
OmegAMP diffusion candidates and 50,000 official HydrAMP-starter candidates.
Each candidate was scored on six public activity tasks (broad AMP plus five
species), using three identity-aware split seeds. For every task and seed, the
composition model and frozen ESM2-35M head were separately converted to
candidate-population percentiles and fused 50/50.

Four fixed utility scenarios stressed balanced activity, the weakest species,
broad-activity failure, and descriptor transport/novelty. Ranking was
lexicographic by the worst scenario, mean of the two worst scenarios, and mean
utility. Continuous signals were percentile-normalized over the full frozen
population; no hidden labels were used.

## Hard constraints

The 50,000 library required:

- standard amino acids only and challenge length 8-50 aa;
- exact uniqueness and no exact official-reference match;
- no exact public-training match; and
- at most one sequence per MMseqs2 identity30 cluster (80% coverage).

The Top100 additionally required:

- membership in the submitted 50,000 library;
- zero identity30 cluster overlap with classifier training sequences;
- fixed complexity and public-AMP descriptor envelopes;
- at most 15 OmegAMP sequences from one generation seed;
- maximum Levenshtein ratio 0.78 to the official reference; and
- maximum internal pairwise Levenshtein ratio 0.80.

The final Top100 has 100 exact-unique members and 100 identity30 clusters. Its
observed maximum official-reference similarity is 0.778 and maximum internal
similarity is 0.698.

## Robustness and challenger decisions

The original frozen generator-family gate used 10,000 fixed-seed Random-25
draws. OmegAMP-only achieved weakest-scenario mean/P10/P01 of
0.8209/0.8182/0.8162, versus 0.8096/0.8037/0.7990 for the mixed
OmegAMP-HydrAMP branch. The mixed branch therefore failed the preregistered
promotion rule (non-negative P10 delta and at least +0.005 mean delta).

The V7.1 closing audit expanded diagnostic Random-25 sampling to 100,000 draws,
compared six additional generator-ratio challengers, tested pairing sensitivity,
and evaluated external activity and safety endpoints. Every challenger failed
at least the frozen external-evidence and safety gates; G6 V5 was retained.
HemoPI2 and frozen ESM2/ANKH HC50/selectivity heads were diagnostics only: they
did not redefine HC50/MIC, prove safety, or alter the five frozen gates after
candidate predictions were observed.

The official evaluator samples 25 members from the Top100. The Top100 is thus a
diversified experimental portfolio, not a claim that every member is safe or
active in vitro.
