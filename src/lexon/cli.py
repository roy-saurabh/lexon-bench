"""
LEXON CLI — main entry point.

Commands:
  generate-benchmark  Generate synthetic benchmark data
  run                 Run LEXON reasoning on benchmark instances
  run-baseline        Run a named baseline system
  evaluate            Compute metrics against gold labels
  reproduce           One-command full reproduction
  export-supplement   Package supplementary ZIP
  check-integrity     Validate benchmark and outputs
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from lexon.constants import RANDOM_SEED

app = typer.Typer(
    name="lexon",
    help="LEXON: Executable AI Regulatory Obligation Reasoning companion toolkit.",
    add_completion=False,
)
console = Console()


# ---------------------------------------------------------------------------
# generate-benchmark
# ---------------------------------------------------------------------------


@app.command("generate-benchmark")
def cmd_generate_benchmark(
    config: Optional[Path] = typer.Option(
        Path("configs/experiment_synthetic.yaml"), help="Config file"
    ),
    seed: int = typer.Option(RANDOM_SEED, help="Random seed"),
    output_dir: Path = typer.Option(Path("data/processed"), help="Output directory"),
) -> None:
    """Generate the LEXON-Bench synthetic benchmark."""
    from lexon.benchmark.generate_synthetic import generate
    from lexon.benchmark.gold import generate_all_gold_labels
    from lexon.benchmark.split import get_split_ids
    from lexon.benchmark.validators import validate_benchmark
    from lexon.io import write_jsonl, write_text

    console.print("[bold blue]Generating LEXON-Bench synthetic benchmark...[/]")

    clauses, profiles, instances = generate(seed=seed)
    clause_index = {c.clause_id: c for c in clauses}
    profile_index = {p.system_id: p for p in profiles}
    gold_labels = generate_all_gold_labels(instances, clause_index, profile_index)

    errors = validate_benchmark(clauses, profiles, instances, gold_labels)
    if errors:
        console.print("[bold red]Benchmark validation failed:[/]")
        for e in errors:
            console.print(f"  ✗ {e}")
        raise typer.Exit(1)

    output_dir = Path(output_dir)
    write_jsonl(clauses, output_dir / "clauses.jsonl")
    write_jsonl(profiles, output_dir / "system_profiles.jsonl")
    write_jsonl(instances, output_dir / "benchmark_instances.jsonl")
    write_jsonl(gold_labels, output_dir / "gold_labels.jsonl")

    splits_dir = Path("data/splits")
    for split in ("train", "dev", "test"):
        ids = get_split_ids(instances, split)
        write_text("\n".join(ids) + "\n", splits_dir / f"{split}_ids.txt")

    console.print(f"[green]✓[/] {len(clauses)} clauses")
    console.print(f"[green]✓[/] {len(profiles)} profiles")
    console.print(f"[green]✓[/] {len(instances)} instances")
    console.print(f"[green]✓[/] {len(gold_labels)} gold labels")
    console.print(f"[green]✓[/] Written to {output_dir}")


# ---------------------------------------------------------------------------
# run (LEXON full system)
# ---------------------------------------------------------------------------


@app.command("run")
def cmd_run(
    input: Path = typer.Option(
        Path("data/processed/benchmark_instances.jsonl"), help="Instances JSONL"
    ),
    output: Path = typer.Option(
        Path("outputs/results/lexon_predictions.jsonl"), help="Predictions JSONL"
    ),
    split: Optional[str] = typer.Option(None, help="Filter by split (train/dev/test)"),
) -> None:
    """Run LEXON full reasoning engine on benchmark instances."""
    from lexon.benchmark.generate_synthetic import generate
    from lexon.io import read_jsonl, write_jsonl
    from lexon.reasoning.engine import LexonEngine
    from lexon.schemas import BenchmarkInstance, ReasoningResult

    console.print("[bold blue]Running LEXON reasoning engine...[/]")

    clauses, profiles, _ = generate()
    clause_index = {c.clause_id: c for c in clauses}
    profile_index = {p.system_id: p for p in profiles}

    instances = read_jsonl(input, BenchmarkInstance)
    if split:
        instances = [i for i in instances if i.split == split]

    engine = LexonEngine()
    results: list[ReasoningResult] = []
    for inst in instances:
        clause = clause_index[inst.clause_id]
        profile = profile_index[inst.system_id]
        result = engine.reason(clause, profile, inst.instance_id)
        results.append(result)

    write_jsonl(results, output)
    console.print(f"[green]✓[/] {len(results)} predictions written to {output}")


# ---------------------------------------------------------------------------
# run-baseline
# ---------------------------------------------------------------------------


@app.command("run-baseline")
def cmd_run_baseline(
    baseline: str = typer.Argument(
        ..., help="Baseline name: checklist | ontology-only | flat-rules"
    ),
    input: Path = typer.Option(
        Path("data/processed/benchmark_instances.jsonl"), help="Instances JSONL"
    ),
    output_dir: Path = typer.Option(Path("outputs/results"), help="Output directory"),
    split: Optional[str] = typer.Option(None, help="Filter by split"),
    run_llm_baseline: bool = typer.Option(
        False, "--run-llm-baseline",
        help="Run optional LLM baseline (requires LEXON_LLM_API_KEY env var)",
    ),
) -> None:
    """Run a named baseline system."""
    from lexon.baselines.checklist import ChecklistBaseline
    from lexon.baselines.ontology_only import OntologyOnlyBaseline
    from lexon.baselines.flat_rules import FlatRulesBaseline
    from lexon.baselines.llm_optional import run_llm_baseline_if_enabled, write_audit_status
    from lexon.benchmark.generate_synthetic import generate
    from lexon.io import read_jsonl, write_jsonl
    from lexon.schemas import BenchmarkInstance, ReasoningResult

    baseline_map = {
        "checklist": ChecklistBaseline,
        "ontology-only": OntologyOnlyBaseline,
        "flat-rules": FlatRulesBaseline,
    }

    if baseline == "llm":
        if not run_llm_baseline:
            console.print(
                "[yellow]LLM baseline is disabled. "
                "Use --run-llm-baseline and set LEXON_LLM_API_KEY to enable.[/]"
            )
            write_audit_status(executed=False)
            raise typer.Exit(0)
        result = run_llm_baseline_if_enabled()
        console.print(f"LLM baseline status: {result}")
        return

    if baseline not in baseline_map:
        console.print(f"[red]Unknown baseline: {baseline}. "
                      f"Choose from: {list(baseline_map.keys())}[/]")
        raise typer.Exit(1)

    console.print(f"[bold blue]Running baseline: {baseline}[/]")

    clauses, profiles, _ = generate()
    clause_index = {c.clause_id: c for c in clauses}
    profile_index = {p.system_id: p for p in profiles}

    instances = read_jsonl(input, BenchmarkInstance)
    if split:
        instances = [i for i in instances if i.split == split]

    engine = baseline_map[baseline]()
    results: list[ReasoningResult] = []
    for inst in instances:
        clause = clause_index[inst.clause_id]
        profile = profile_index[inst.system_id]
        result = engine.reason(clause, profile, inst.instance_id)
        results.append(result)

    safe_name = baseline.replace("-", "_")
    out_path = Path(output_dir) / f"{safe_name}_predictions.jsonl"
    write_jsonl(results, out_path)
    console.print(f"[green]✓[/] {len(results)} predictions written to {out_path}")


# ---------------------------------------------------------------------------
# evaluate
# ---------------------------------------------------------------------------


@app.command("evaluate")
def cmd_evaluate(
    gold: Path = typer.Option(
        Path("data/processed/gold_labels.jsonl"), help="Gold labels JSONL"
    ),
    pred: Path = typer.Option(
        Path("outputs/results/lexon_predictions.jsonl"), help="Predictions JSONL"
    ),
    system_name: str = typer.Option("LEXON (full)", help="System name for tables"),
    split: str = typer.Option("test", help="Split being evaluated"),
    output_dir: Path = typer.Option(Path("outputs/results"), help="Output directory"),
) -> None:
    """Compute evaluation metrics against gold labels."""
    from lexon.benchmark.generate_synthetic import generate
    from lexon.evaluation.bootstrap import fill_bootstrap_cis
    from lexon.evaluation.metrics import (
        aggregate_metrics,
        compute_instance_metrics,
    )
    from lexon.evaluation.tables import write_metrics_csv
    from lexon.io import read_jsonl
    from lexon.schemas import BenchmarkInstance, GoldLabels, ReasoningResult

    console.print(f"[bold blue]Evaluating {system_name} on {split} split...[/]")

    gold_list = read_jsonl(gold, GoldLabels)
    pred_list = read_jsonl(pred, ReasoningResult)

    clauses, profiles, instances = generate()
    instance_index = {i.instance_id: i for i in instances if i.split == split}
    gold_index = {g.instance_id: g for g in gold_list}
    pred_index = {p.instance_id: p for p in pred_list}

    instance_metrics = []
    for iid, inst in sorted(instance_index.items()):
        if iid not in gold_index or iid not in pred_index:
            continue
        g = gold_index[iid]
        p = pred_index[iid]
        im = compute_instance_metrics(p, g, ambiguous=inst.ambiguous, difficulty=inst.difficulty)
        instance_metrics.append(im)

    agg = aggregate_metrics(instance_metrics, system_name, split)
    agg = fill_bootstrap_cis(agg, instance_metrics)

    out = Path(output_dir)
    safe_name = system_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    write_metrics_csv([agg], out / f"metrics_{safe_name}.csv")

    # Pretty-print summary
    table = Table(title=f"Results — {system_name} ({split} split)")
    table.add_column("Task")
    table.add_column("Precision", justify="right")
    table.add_column("Recall", justify="right")
    table.add_column("F1", justify="right")
    table.add_column("95% CI", justify="right")
    table.add_row(
        "T1 Activation",
        f"{agg.t1_precision:.3f}", f"{agg.t1_recall:.3f}", f"{agg.t1_f1:.3f}",
        f"[{agg.t1_f1_ci_lo:.3f}, {agg.t1_f1_ci_hi:.3f}]",
    )
    table.add_row(
        "T2 Evidence Gaps",
        f"{agg.t2_precision:.3f}", f"{agg.t2_recall:.3f}", f"{agg.t2_f1:.3f}",
        f"[{agg.t2_f1_ci_lo:.3f}, {agg.t2_f1_ci_hi:.3f}]",
    )
    table.add_row(
        "T3 Conflicts",
        f"{agg.t3_precision:.3f}", f"{agg.t3_recall:.3f}", f"{agg.t3_f1:.3f}",
        "—",
    )
    console.print(table)
    console.print(f"[green]✓[/] Written to {out}")


# ---------------------------------------------------------------------------
# reproduce
# ---------------------------------------------------------------------------


@app.command("reproduce")
def cmd_reproduce(
    all: bool = typer.Option(False, "--all", help="Run full reproduction pipeline"),
    smoke: bool = typer.Option(False, "--smoke", help="Quick smoke test (subset)"),
) -> None:
    """Run full reproduction pipeline (generate → run → evaluate → tables → figures)."""
    from scripts.reproduce_paper_results import reproduce_all

    console.print("[bold blue]Running full LEXON-Bench reproduction pipeline...[/]")
    reproduce_all(smoke=smoke)
    console.print("[bold green]Reproduction complete.[/]")


# ---------------------------------------------------------------------------
# export-supplement
# ---------------------------------------------------------------------------


@app.command("export-supplement")
def cmd_export_supplement(
    output: Path = typer.Option(
        Path("outputs/lexon_supplementary.zip"), help="Output ZIP path"
    ),
) -> None:
    """Package supplementary materials as a ZIP archive."""
    import zipfile

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    include_patterns = [
        "data/processed/*.jsonl",
        "data/splits/*.txt",
        "outputs/results/*.csv",
        "outputs/tables/*.md",
        "outputs/figures/*.png",
        "outputs/reports/*.md",
        "rules/*.dl",
        "rules/*.md",
        "rules/*.yaml",
        "docs/*.md",
        "src/lexon/**/*.py",
    ]

    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for pattern in include_patterns:
            for file_path in sorted(Path(".").glob(pattern)):
                if file_path.is_file():
                    zf.write(file_path)

    console.print(f"[green]✓[/] Supplementary ZIP written to {output}")


# ---------------------------------------------------------------------------
# check-integrity
# ---------------------------------------------------------------------------


@app.command("check-integrity")
def cmd_check_integrity() -> None:
    """Validate benchmark integrity and check for placeholder text in outputs."""
    from lexon.benchmark.validators import validate_benchmark
    from lexon.benchmark.generate_synthetic import generate
    from lexon.benchmark.gold import generate_all_gold_labels
    from lexon.evaluation.tables import check_no_placeholders

    console.print("[bold blue]Running integrity checks...[/]")
    errors: list[str] = []

    clauses, profiles, instances = generate()
    clause_index = {c.clause_id: c for c in clauses}
    profile_index = {p.system_id: p for p in profiles}
    gold_labels = generate_all_gold_labels(instances, clause_index, profile_index)
    errors.extend(validate_benchmark(clauses, profiles, instances, gold_labels))

    table_paths = [
        Path("outputs/tables/table_activation_gap.md"),
        Path("outputs/tables/table_conflicts.md"),
        Path("outputs/tables/table_ablation.md"),
    ]
    for tp in table_paths:
        if tp.exists():
            errors.extend(check_no_placeholders(tp))

    if errors:
        console.print("[bold red]Integrity check FAILED:[/]")
        for e in errors:
            console.print(f"  ✗ {e}")
        raise typer.Exit(1)
    else:
        console.print("[bold green]✓ All integrity checks passed.[/]")


if __name__ == "__main__":
    app()
