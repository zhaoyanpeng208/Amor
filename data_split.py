#!/usr/bin/env python3
"""
Randomly split a dataset into train/val/test with an 8:1:1 ratio, repeated 5 times
using fixed random seeds 29, 37, 42, 49 and 51.

Supports:
  * CSV/TSV: parsed with the csv module, so records containing embedded commas,
    quotes or newlines are never broken apart. The header row is preserved by default
    and copied into every subset.
  * Plain text / JSONL: split line by line.
  * Optional stratified sampling by column (--stratify), keeping class proportions
    consistent across subsets.

Examples:
    python split_811.py data.csv                      # -> data_splits/seed_29/{train,val,test}.csv ...
    python split_811.py data.csv -o runs              # custom output directory
    python split_811.py data.csv --flat               # flat output: train_29.csv / val_29.csv / test_29.csv
    python split_811.py data.csv --stratify label     # stratified by the "label" column
    python split_811.py data.csv --no-header          # input has no header row
    python split_811.py data.csv --delimiter ';'      # custom delimiter
    python split_811.py data.txt                      # plain text, split by line
"""

import argparse
import csv
import random
import sys
from collections import Counter
from pathlib import Path

DEFAULT_SEEDS = [29, 37, 42, 49, 51]
TRAIN_RATIO, VAL_RATIO = 0.8, 0.1
CSV_SUFFIXES = {".csv", ".tsv"}

# Raise the field size limit so very long fields (possibly containing newlines) are written intact.
csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def split_by_ratio(idx, rng):
    """Shuffle indices and cut them into 8:1:1; the three parts always sum to the total."""
    idx = list(idx)
    rng.shuffle(idx)
    n = len(idx)
    n_train = min(int(round(n * TRAIN_RATIO)), n)
    n_val = min(int(round(n * VAL_RATIO)), n - n_train)
    return idx[:n_train], idx[n_train:n_train + n_val], idx[n_train + n_val:]


def allocate_quota(sizes, total):
    """Largest-remainder method: distribute `total` slots proportional to `sizes`, summing exactly to `total`."""
    raw = [s * total / sum(sizes) for s in sizes]
    base = [int(x) for x in raw]
    rest = total - sum(base)
    order = sorted(range(len(sizes)), key=lambda i: (raw[i] - base[i], -sizes[i]), reverse=True)
    for k in range(rest):
        base[order[k % len(order)]] += 1
    return base


def stratified_split(values, rng):
    """Stratified split: each class keeps the same proportion in all three parts, with exact 8:1:1 totals."""
    groups = {}
    for i, v in enumerate(values):
        groups.setdefault(v, []).append(i)
    keys = sorted(groups, key=str)
    gidx = [groups[k] for k in keys]
    for g in gidx:
        rng.shuffle(g)

    n = sum(len(g) for g in gidx)
    n_train = min(int(round(n * TRAIN_RATIO)), n)
    n_val = min(int(round(n * VAL_RATIO)), n - n_train)

    q_train = allocate_quota([len(g) for g in gidx], n_train)
    remain = [len(g) - t for g, t in zip(gidx, q_train)]
    q_val = allocate_quota(remain, n_val) if n - n_train > 0 else [0] * len(gidx)

    tr, va, te = [], [], []
    for g, t, v in zip(gidx, q_train, q_val):
        tr += g[:t]
        va += g[t:t + v]
        te += g[t + v:]
    return tr, va, te


def read_csv_rows(path, delimiter):
    """Read a file into a list of records; auto-detect the delimiter when not given."""
    with path.open("r", encoding="utf-8", errors="surrogateescape", newline="") as f:
        if delimiter is None:
            sample = f.read(64 * 1024)
            f.seek(0)
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
            except csv.Error:
                delimiter = ","
        return list(csv.reader(f, delimiter=delimiter)), delimiter


def write_csv_rows(path, rows):
    """Write records back as CSV, preserving quoting of special characters."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", errors="surrogateescape", newline="") as f:
        csv.writer(f, lineterminator="\n").writerows(rows)


def write_text_lines(path, lines):
    """Write plain-text lines, one per record."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", errors="surrogateescape", newline="") as f:
        for ln in lines:
            f.write(ln + "\n")


def main():
    ap = argparse.ArgumentParser(
        description="Split data 8:1:1 (train:val:test), 5 times, with fixed seeds 29/37/42/49/51")
    ap.add_argument("input", help="input file (.csv/.tsv, or plain text / JSONL)", default='data/AlphaLISA.csv/AlphaLISA.csv')
    ap.add_argument("-o", "--outdir", default=None, help="output directory (default: <input stem>_splits)")
    ap.add_argument("--seeds", type=int, nargs="+", default=DEFAULT_SEEDS, help="random seed list")
    ap.add_argument("--flat", action="store_true", help="flat output train_29.csv instead of seed_29/ subdirectories")
    ap.add_argument("--delimiter", default=None, help="CSV delimiter (default: auto-detect)")
    ap.add_argument("--no-header", action="store_true", help="input CSV has no header row (default: first row is header)")
    ap.add_argument("--stratify", default=None, help="stratify by column: header name, or 0-based column index")
    ap.add_argument("--csv", action="store_true", help="force CSV parsing even if the suffix differs")
    ap.add_argument("--text", action="store_true", help="force plain-text (line) parsing")
    ap.add_argument("--keep-blank", action="store_true", help="text mode: keep blank lines (default: drop them)")
    args = ap.parse_args()

    src = Path(args.input).expanduser()
    if not src.is_file():
        raise SystemExit(f"Input file not found: {src}")

    is_csv = args.csv or (not args.text and src.suffix.lower() in CSV_SUFFIXES)

    if is_csv:
        table, delimiter = read_csv_rows(src, args.delimiter)
        if not table:
            raise SystemExit("Input file is empty: nothing to split")
        header = [] if args.no_header else table[0]
        body = table if args.no_header else table[1:]
        ncols = len(table[0])
    else:
        text = src.read_text(encoding="utf-8", errors="surrogateescape").splitlines()
        if not args.keep_blank:
            text = [ln for ln in text if ln.strip()]
        if not text:
            raise SystemExit("Input file is empty: nothing to split")
        header, body, ncols = [], text, None

    n = len(body)
    if n < 3:
        raise SystemExit(f"Too few records ({n}) for an 8:1:1 split (at least 3 required)")

    # Resolve the stratification column, either by header name or by 0-based index.
    strat_values = None
    if args.stratify:
        if not is_csv:
            raise SystemExit("--stratify only supports CSV/TSV input")
        col = args.stratify
        if header and col in header:
            ci = header.index(col)
        else:
            try:
                ci = int(col)
            except ValueError:
                raise SystemExit(f"Stratify column {col!r} not found; use a header name or a 0-based column index")
            if not (0 <= ci < ncols):
                raise SystemExit(f"Column index {ci} out of range (file has {ncols} columns)")
        strat_values = [row[ci] if ci < len(row) else "" for row in body]

    outdir = Path(args.outdir).expanduser() if args.outdir else src.parent / f"{src.stem}_splits"
    ext = src.suffix.lstrip(".") or "txt"
    writer = write_csv_rows if is_csv else write_text_lines

    mode = "CSV" if is_csv else "text"
    print(f"Input: {src}  [{mode}" + (f", delimiter={delimiter!r}" if is_csv else "") + "]")
    print(f"Records: {n}" + (" (1 header row stripped and copied into every subset)" if header else ""))
    if strat_values is not None:
        dist = Counter(strat_values)
        print(f"Stratify by: {args.stratify}  classes={len(dist)}  " +
              "  ".join(f"{k}={v}" for k, v in dist.most_common(8)) +
              (" ..." if len(dist) > 8 else ""))
    print(f"Output directory: {outdir}\n")

    parts_name = ("train", "val", "test")
    for seed in args.seeds:
        rng = random.Random(seed)
        if strat_values is None:
            tr, va, te = split_by_ratio(range(n), rng)
        else:
            tr, va, te = stratified_split(strat_values, rng)

        # Sanity check: the three parts are disjoint and together cover every record.
        assert len(set(tr) | set(va) | set(te)) == n, f"seed {seed}: split does not cover all records"
        assert not (set(tr) & set(va)) and not (set(tr) & set(te)) and not (set(va) & set(te)), \
            f"seed {seed}: split parts overlap"

        buckets = [tr, va, te]
        stats = []
        for name, bidx in zip(parts_name, buckets):
            rows = [body[i] for i in bidx]
            if args.flat:
                out_path = outdir / f"{name}_{seed}.{ext}"
            else:
                out_path = outdir / f"seed_{seed}" / f"{name}.{ext}"
            data = ([header] + rows) if header else rows
            writer(out_path, data)
            stats.append(len(rows))

        print(f"seed {seed:>3}: train={stats[0]:<6} val={stats[1]:<6} test={stats[2]:<6} total={sum(stats)}")

    print("\nCheck passed: for every seed, train+val+test are disjoint and cover the full dataset.")


if __name__ == "__main__":
    main()
