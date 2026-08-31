"""Score FASTA sequences with the disclosed composition/physicochemical heads."""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from pathlib import Path

import joblib
import numpy as np


AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"
HYDROPHOBIC = set("AILMFWVY")
AROMATIC = set("FWY")
POSITIVE = set("KRH")
NEGATIVE = set("DE")


def read_fasta(path: Path) -> tuple[list[str], list[str]]:
    names: list[str] = []
    sequences: list[str] = []
    current: list[str] = []
    name: str | None = None
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
    if not sequences or any(not sequence or set(sequence) - set(AMINO_ACIDS) for sequence in sequences):
        raise ValueError("FASTA must contain non-empty standard-amino-acid sequences")
    return names, sequences


def numerical_features(sequences: list[str]) -> np.ndarray:
    matrix = np.zeros((len(sequences), 72), dtype=np.float32)
    aa_index = {amino_acid: index for index, amino_acid in enumerate(AMINO_ACIDS)}
    for row, sequence in enumerate(sequences):
        length, counts = len(sequence), Counter(sequence)
        matrix[row, 0] = math.log1p(length)
        matrix[row, 1] = (
            counts["K"] + counts["R"] + 0.1 * counts["H"] - counts["D"] - counts["E"]
        ) / length
        matrix[row, 2] = sum(counts[value] for value in HYDROPHOBIC) / length
        matrix[row, 3] = sum(counts[value] for value in AROMATIC) / length
        matrix[row, 4] = sum(counts[value] for value in POSITIVE) / length
        matrix[row, 5] = sum(counts[value] for value in NEGATIVE) / length
        matrix[row, 6] = counts["C"] / length
        matrix[row, 7] = counts["G"] / length
        matrix[row, 8] = counts["P"] / length
        matrix[row, 9] = len(set(sequence)) / 20.0
        matrix[row, 10] = max(counts.values()) / length
        matrix[row, 11] = sum(
            sequence[index] == sequence[index - 1] for index in range(1, length)
        ) / max(1, length - 1)
        for amino_acid, index in aa_index.items():
            matrix[row, 12 + index] = counts[amino_acid] / length
        for segment in range(2):
            part = sequence[segment * length // 2 : (segment + 1) * length // 2]
            local_counts = Counter(part)
            denominator = max(1, len(part))
            for amino_acid, index in aa_index.items():
                matrix[row, 32 + segment * 20 + index] = local_counts[amino_acid] / denominator
    return matrix


def predict(artifact: dict, feature_matrix: np.ndarray) -> np.ndarray:
    base = 0.5 * artifact["linear"].predict_proba(feature_matrix)[:, 1]
    base += 0.5 * artifact["tree"].predict_proba(feature_matrix)[:, 1]
    clipped = np.clip(base, 1e-6, 1 - 1e-6)
    logit = np.log(clipped / (1 - clipped)).reshape(-1, 1)
    return artifact["calibrator"].predict_proba(logit)[:, 1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("fasta", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--models", type=Path, default=Path("models/public_activity"))
    args = parser.parse_args()

    names, sequences = read_fasta(args.fasta)
    feature_matrix = numerical_features(sequences)
    model_paths = sorted(args.models.glob("*__seed*.joblib"))
    if len(model_paths) != 18:
        raise FileNotFoundError(f"Expected 18 public-activity artifacts; found {len(model_paths)}")

    score_columns: dict[str, np.ndarray] = {}
    for model_path in model_paths:
        score_columns[model_path.stem] = predict(joblib.load(model_path), feature_matrix)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["identifier", "sequence", *score_columns]
    with args.output_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for index, (name, sequence) in enumerate(zip(names, sequences)):
            row: dict[str, str | float] = {"identifier": name, "sequence": sequence}
            row.update({column: float(values[index]) for column, values in score_columns.items()})
            writer.writerow(row)


if __name__ == "__main__":
    main()
