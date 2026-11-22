"""Compare two Windows Vulkan llama.cpp builds with the same local GGUF."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile


ORDER = ("baseline", "candidate", "candidate", "baseline")
LABELS = {(512, 0): "prefill_512", (0, 128): "decode_128"}
FLAGS = ["-ngl", "99", "-p", "512", "-n", "128", "-b", "256", "-ub", "128", "-r", "3", "-o", "json"]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def trial(binary, weights, device):
    proc = subprocess.run([str(binary), "-m", str(weights), "-dev", device, *FLAGS],
                          cwd=binary.parent, capture_output=True, encoding="utf-8",
                          errors="replace", timeout=600)
    if proc.returncode:
        raise RuntimeError(f"{binary.parent.name} exited with {proc.returncode}.\n{proc.stderr[-1200:]}")
    tests = {}
    details = None
    for row in json.loads(proc.stdout):
        if row["devices"] != device or "vulkan" not in row["backends"].lower():
            raise ValueError("The benchmark did not report the requested Vulkan device.")
        label = LABELS[(row["n_prompt"], row["n_gen"])]
        samples = row["samples_ts"]
        if label in tests or len(samples) != 3 or not all(math.isfinite(s) and s > 0 for s in samples):
            raise ValueError("Missing or invalid timing samples.")
        tests[label] = {"tokens_per_second": samples, "nanoseconds": row["samples_ns"],
                        "utc": row["test_time"]}
        details = {k: row[k] for k in ("build_number", "build_commit", "gpu_info", "cpu_info",
                                       "devices", "backends", "model_type", "n_threads")}
        details["cpu_info"] = details["cpu_info"].strip()
    if set(tests) != set(LABELS.values()):
        raise ValueError("Expected separate prompt and output measurements.")
    return details, tests


def compare(baseline, candidate, weights, device):
    binaries = {k: p.resolve(strict=True) for k, p in (("baseline", baseline), ("candidate", candidate))}
    if binaries["baseline"].samefile(binaries["candidate"]):
        raise ValueError("Choose two different builds.")
    weights = weights.resolve(strict=True)
    result = {"date_utc": datetime.now(timezone.utc).isoformat(), "model_file": weights.name,
              "model_sha256": sha256(weights), "device": device, "bench_flags": FLAGS,
              "builds": {}, "trials": []}
    for number, role in enumerate(ORDER, 1):
        print(f"Trial {number}/4: {role}", flush=True)
        details, tests = trial(binaries[role], weights, device)
        if result["builds"].setdefault(role, details) != details:
            raise ValueError("Hardware or build changed between trials.")
        result["trials"].append({"build": role, "tests": tests})
    old, new = (result["builds"][role] for role in ("baseline", "candidate"))
    if old["build_commit"] == new["build_commit"]:
        raise ValueError("The binaries report the same llama.cpp commit.")
    for field in ("gpu_info", "cpu_info", "n_threads", "model_type"):
        if old[field] != new[field]:
            raise ValueError(f"Runs disagree on {field}; repeat under matching conditions.")
    result["summary"] = {}
    for label in LABELS.values():
        medians = {}
        for role in binaries:
            samples = [s for run in result["trials"] if run["build"] == role
                       for s in run["tests"][label]["tokens_per_second"]]
            medians[role] = statistics.median(samples)
        medians["ratio"] = medians["candidate"] / medians["baseline"]
        result["summary"][label] = medians
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("baseline", "candidate", "model", "out"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--device", default="Vulkan0")
    args = p.parse_args()
    if args.out.exists():
        p.error("The output already exists. Choose a fresh filename.")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result = compare(args.baseline, args.candidate, args.model, args.device)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.out.parent,
                                     suffix=".partial", delete=False) as file:
        temp = Path(file.name)
        try:
            json.dump(result, file, indent=2, allow_nan=False)
            file.write("\n")
        except BaseException:
            file.close()
            temp.unlink(missing_ok=True)
            raise
    try:
        # Windows rename fails if another run has already claimed this result name.
        os.rename(temp, args.out)
    finally:
        temp.unlink(missing_ok=True)
    print(json.dumps(result["summary"], indent=2))
    print(f"Saved {args.out}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.TimeoutExpired) as error:
        sys.exit(f"Benchmark stopped: {error}")
