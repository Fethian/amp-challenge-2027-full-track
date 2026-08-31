# Robust public-data AMP design for the AMP Challenge 2027

This Full Track repository releases the frozen G6 V5 candidate: a deterministic
50,000-sequence peptide library and ranked Top100 selected with disclosed public
activity models, frozen ESM2 representations, identity-aware validation,
novelty controls, and robust portfolio optimization.

## Reproduce the official outputs

Install `uv` and Git LFS, then run:

```bash
git lfs pull
uv sync --frozen
uv run generate
```

Python is fixed to the 3.12 series in `.python-version` and `pyproject.toml`;
resolved dependencies are committed in `uv.lock`. The default seed is 42. The
command writes `generate/library.fasta` and `generate/top.fasta`. Repeated runs
produce byte-identical files containing 50,000 and 100 sequences respectively.
Identifiers are simple ranked labels (`seq00001`, `seq00002`, ...) and contain
no private database identifiers.

The official entry point deliberately materializes the frozen, audited release
files. Research-time generation and scoring required GPU models and a much
larger environment, so they are not silently rerun by the lightweight command.
The actual public OmegAMP source, configuration, training snapshot and checkpoint
used for candidate generation are included under `vendor/omegamp/` and
`training_data/omegamp_generative/`. The public activity and ESM2 selection heads
and their disclosed training table are under `models/` and
`training_data/public_activity/`.

For research-time inference, install the optional environment and score a FASTA:

```bash
uv sync --frozen --extra activity
uv run python scripts/score_public_activity.py input.fasta activity_scores.csv
uv sync --frozen --extra esm
uv run python scripts/score_public_esm.py input.fasta esm_scores.csv
```

## Documentation

- `KAGGLE_WRITEUP.md`: submission article and experiment summary.
- `MODEL_AND_DATA.md`: model, data, provenance, license, and claim boundaries.
- `TOP100_SELECTION.md`: frozen ranking, constraints, and robustness procedure.
- `config/selection_protocol.json`: public ranking formula, scenario weights,
  clustering parameters, and Random-25 aggregation order.
- `audit/v7_1_decision_summary.csv`: ARCADIAMP/OmegAMP capstone arms and five-gate decision.
- `scripts/verify_submission.py`: official challenge repository validator.

These files separate three reproducibility claims: `uv run generate` exports the
frozen release; the model/data/config directories disclose the research lineage;
and the audit/configuration files support the selection and closing decision.
Byte-identical export alone is not presented as a from-scratch rerun of every
GPU training and candidate-search step.

To verify a public clone exactly as the organizers do:

```bash
uv run python scripts/verify_submission.py <github-url> \
  --antibacterial-fasta data/antibacterial.fasta
```

The computational scores are public-data surrogates. They are not measured MIC,
HC50, hemolytic safety, clinical efficacy, or hidden competition labels.
