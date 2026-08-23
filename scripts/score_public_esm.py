"""Score a FASTA file with the disclosed frozen-ESM2 public activity heads."""

from __future__ import annotations

import argparse
import math
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
from transformers import AutoModel, AutoTokenizer


BACKBONE = "facebook/esm2_t12_35M_UR50D"
AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
HYDROPHOBIC = set("AILMFWVY")
AROMATIC = set("FWY")


def read_fasta(path: Path) -> tuple[list[str], list[str]]:
    names, sequences, current = [], [], []
    name = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            if name is not None:
                names.append(name)
                sequences.append("".join(current).upper())
            name, current = line[1:], []
        else:
            current.append(line)
    if name is not None:
        names.append(name)
        sequences.append("".join(current).upper())
    if not sequences or any(set(sequence) - set(AMINO_ACIDS) for sequence in sequences):
        raise ValueError("FASTA must contain non-empty standard-amino-acid sequences")
    return names, sequences


def numerical_features(sequences: list[str]) -> np.ndarray:
    matrix = np.zeros((len(sequences), 72), dtype=np.float32)
    aa_index = {amino_acid: index for index, amino_acid in enumerate(AMINO_ACIDS)}
    for row, sequence in enumerate(sequences):
        length, counts = len(sequence), Counter(sequence)
        matrix[row, 0] = math.log1p(length)
        matrix[row, 1] = (counts["K"] + counts["R"] + .1 * counts["H"] - counts["D"] - counts["E"]) / length
        matrix[row, 2] = sum(counts[value] for value in HYDROPHOBIC) / length
        matrix[row, 3] = sum(counts[value] for value in AROMATIC) / length
        matrix[row, 4] = sum(counts[value] for value in "KRH") / length
        matrix[row, 5] = sum(counts[value] for value in "DE") / length
        matrix[row, 6] = counts["C"] / length
        matrix[row, 7] = counts["G"] / length
        matrix[row, 8] = counts["P"] / length
        matrix[row, 9] = len(set(sequence)) / 20
        matrix[row, 10] = max(counts.values()) / length
        matrix[row, 11] = sum(sequence[i] == sequence[i - 1] for i in range(1, length)) / max(1, length - 1)
        for amino_acid, index in aa_index.items():
            matrix[row, 12 + index] = counts[amino_acid] / length
        for segment in range(2):
            part = sequence[segment * length // 2:(segment + 1) * length // 2]
            local, denominator = Counter(part), max(1, len(part))
            for amino_acid, index in aa_index.items():
                matrix[row, 32 + segment * 20 + index] = local[amino_acid] / denominator
    return matrix


def esm_embeddings(sequences: list[str], batch_size: int) -> np.ndarray:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(BACKBONE)
    model = AutoModel.from_pretrained(BACKBONE).eval().to(device)
    rows = []
    with torch.inference_mode():
        for start in range(0, len(sequences), batch_size):
            tokens = tokenizer(
                sequences[start:start + batch_size],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=52,
                return_special_tokens_mask=True,
            )
            special = tokens.pop("special_tokens_mask").to(device)
            tokens = {key: value.to(device) for key, value in tokens.items()}
            hidden = model(**tokens).last_hidden_state
            mask = (tokens["attention_mask"].bool() & ~special.bool()).unsqueeze(-1)
            pooled = (hidden * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
            rows.append(pooled.cpu().numpy().astype(np.float32))
    return np.concatenate(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("fasta", type=Path)
    parser.add_argument("--models", type=Path, default=Path("models/public_esm"))
    parser.add_argument("--output", type=Path, default=Path("public_esm_scores.csv"))
    parser.add_argument("--batch-size", type=int, default=128)
    args = parser.parse_args()

    names, sequences = read_fasta(args.fasta)
    features = np.concatenate([esm_embeddings(sequences, args.batch_size), numerical_features(sequences)], axis=1)
    output = pd.DataFrame({"name": names, "sequence": sequences})
    model_paths = sorted(args.models.glob("*.joblib"))
    if len(model_paths) != 18:
        raise RuntimeError(f"Expected 18 public ESM heads, found {len(model_paths)}")
    for path in model_paths:
        fitted = joblib.load(path)
        probability = fitted["head"].predict_proba(features)[:, 1]
        logit = np.log(np.clip(probability, 1e-6, 1 - 1e-6) / np.clip(1 - probability, 1e-6, 1))
        output[path.stem] = fitted["calibrator"].predict_proba(logit.reshape(-1, 1))[:, 1]
    output.to_csv(args.output, index=False)
    print(f"Wrote {len(output)} sequences × {len(model_paths)} public ESM scores to {args.output}")


if __name__ == "__main__":
    main()
