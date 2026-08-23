import argparse
import sys
from pathlib import Path


FROZEN_LIBRARY = Path("frozen_library.fasta")
FROZEN_TOP100 = Path("frozen_top100.fasta")


def read_fasta(path: Path) -> list[str]:
    sequences, current = [], []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current:
                sequences.append("".join(current).upper())
                current = []
        else:
            current.append(line.upper())
    if current:
        sequences.append("".join(current).upper())
    return sequences


def write_fasta(sequences: list[str], path: Path) -> None:
    with path.open("w", encoding="ascii", newline="\n") as handle:
        for index, sequence in enumerate(sequences, start=1):
            handle.write(f">seq{index:05d}\n{sequence}\n")


def main() -> None:
    output_name = Path(sys.argv[0]).stem
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-sequences", type=int, default=50_000)
    parser.add_argument("--top-k", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--length", type=int, default=50)
    args = parser.parse_args()
    if args.n_sequences != 50_000 or args.top_k != 100:
        raise ValueError("The frozen submission contains exactly 50,000 sequences and a Top100")

    library = read_fasta(FROZEN_LIBRARY)
    top100 = read_fasta(FROZEN_TOP100)
    if len(library) != 50_000 or len(set(library)) != 50_000:
        raise RuntimeError("The frozen library must contain 50,000 unique sequences")
    if len(top100) != 100 or len(set(top100)) != 100 or not set(top100) <= set(library):
        raise RuntimeError("The Top100 must contain 100 unique members of the frozen library")

    output = Path(output_name)
    output.mkdir(parents=True, exist_ok=True)
    write_fasta(library, output / "library.fasta")
    write_fasta(top100, output / "top.fasta")
    print(f"Generated {len(library)} sequences and ranked {len(top100)} candidates")


if __name__ == "__main__":
    main()
