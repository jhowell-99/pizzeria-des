import csv
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import simpy
from scipy import stats
from tqdm import tqdm

from pizzeria_sim.config import PizzeriaConfig
from pizzeria_sim.model import Pizzeria


def run_replication(config: PizzeriaConfig, seed: int) -> dict:
    """Run a single replication with a given seed and return its summary."""
    np.random.seed(seed)
    env = simpy.Environment()
    model = Pizzeria(env, config)
    model.run()
    env.run(until=config.sim_time)
    return model.metrics.summary()


def run_replications(config: PizzeriaConfig, n: int = 30, base_seed: int = 42) -> dict:
    """Run n replications and aggregate metrics across all runs."""
    results = [
        run_replication(config, seed=base_seed + i)
        for i in tqdm(range(n), desc="Running replications", unit="run")
    ]
    return aggregate(results, n)


def aggregate(results: list[dict], n: int) -> dict:
    """Aggregate summaries across replications into mean ± CI per metric."""

    def ci(data: list[float]) -> dict:
        a = np.array(data)
        mean = np.mean(a)
        std = np.std(a, ddof=1)
        se = std / np.sqrt(len(a))
        t_crit = stats.t.ppf(0.975, df=len(a) - 1)
        return {
            "mean": round(float(mean), 3),
            "std": round(float(std), 3),
            "ci_low": round(float(mean - t_crit * se), 3),
            "ci_high": round(float(mean + t_crit * se), 3),
        }

    def aggregate_stage(stage_name: str, metric: str) -> dict:
        values = [
            r["stages"][i][metric]["mean"]
            for r in results
            for i, s in enumerate(r["stages"])
            if s["stage"] == stage_name and r["stages"][i][metric]
        ]
        return ci(values) if values else {}

    completed = [r["completed_orders"] for r in results]
    total_means = [r["total_time"]["mean"] for r in results if r["total_time"]]
    total_p95s = [r["total_time"]["p95"] for r in results if r["total_time"]]

    stages = ["order", "prep", "bake", "serve"]

    abandoned = [r["abandoned_orders"] for r in results]
    rates = [r["abandonment_rate"] for r in results]
    abandoned_queue_means = [
        r["abandoned_queue_time"]["mean"]
        for r in results
        if r["abandoned_queue_time"]
    ]

    return {
        "n_replications": n,
        "completed_orders":   ci(completed),
        "abandoned_orders":   ci(abandoned),
        "abandonment_rate":   ci(rates),
        "abandoned_queue_time": ci(abandoned_queue_means) if abandoned_queue_means else {},
        "total_time": {
            "mean": ci(total_means),
            "p95":  ci(total_p95s),
        },
        "stages": {
            stage: {
                "queue_time":   aggregate_stage(stage, "queue_time"),
                "service_time": aggregate_stage(stage, "service_time"),
            }
            for stage in stages
        }
    }

def report_replications(results: dict):
    width = 80
    n = results["n_replications"]

    print("=" * width)
    print(f"{'STOCHASTIC ANALYSIS REPORT':^{width}}")
    print(f"{'(' + str(n) + ' replications, 95% confidence intervals)':^{width}}")
    print("=" * width)

    # Throughput
    co = results["completed_orders"]
    print(f"  Completed orders  :  "
          f"mean={co['mean']}  std={co['std']}  "
          f"95% CI=[{co['ci_low']}, {co['ci_high']}]")

    ab = results["abandoned_orders"]
    print(f"  Abandoned orders  :  "
          f"mean={ab['mean']}  std={ab['std']}  "
          f"95% CI=[{ab['ci_low']}, {ab['ci_high']}]")

    rate = results["abandonment_rate"]
    print(f"  Abandonment rate  :  "
          f"mean={rate['mean']}%  std={rate['std']}  "
          f"95% CI=[{rate['ci_low']}%, {rate['ci_high']}%]")

    aq = results.get("abandoned_queue_time", {})
    if aq:
        print(f"  Abandoned queue   :  "
              f"mean={aq['mean']}  std={aq['std']}  "
              f"95% CI=[{aq['ci_low']}, {aq['ci_high']}]")
    print()

    # Total time in system
    def fmt_ci(d):
        if not d:
            return "  no data"
        return (f"mean={d['mean']:>7}  std={d['std']:>7}  "
                f"95% CI=[{d['ci_low']:>7}, {d['ci_high']:>7}]")

    t = results["total_time"]
    print(f"  Total time in system (min):")
    print(f"    mean  :  {fmt_ci(t['mean'])}")
    print(f"    p95   :  {fmt_ci(t['p95'])}")
    print()

    # Per-stage breakdown
    header = (f"  {'Stage':<10} {'Metric':<14} {'mean':>7} "
              f"{'std':>7} {'CI low':>8} {'CI high':>8}")
    print(header)
    print("  " + "-" * (width - 2))

    for stage, metrics in results["stages"].items():
        for metric_name, vals in [("queue", metrics["queue_time"]),
                                   ("service", metrics["service_time"])]:
            if not vals:
                continue
            print(
                f"  {stage:<10} {metric_name:<14} "
                f"{vals['mean']:>7} {vals['std']:>7} "
                f"{vals['ci_low']:>8} {vals['ci_high']:>8}"
            )

    print("=" * width)


def export_results(results: dict, config: PizzeriaConfig, output_dir: str = "outputs"):
    """Export replication results to a timestamped folder."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(output_dir) / timestamp
    path.mkdir(parents=True, exist_ok=True)

    _export_json(results, path)
    _export_summary_csv(results, path)
    _export_stages_csv(results, path)
    _export_config(config, path)

    print(f"Results written to {path}/")


def _export_json(results: dict, path: Path):
    with open(path / "results.json", "w") as f:
        json.dump(results, f, indent=2)


def _export_summary_csv(results: dict, path: Path):
    rows = [
        {"metric": "completed_orders", "stat": stat, "value": val}
        for stat, val in results["completed_orders"].items()
    ] + [
        {"metric": f"total_time_{sub}", "stat": stat, "value": val}
        for sub, stats in results["total_time"].items()
        for stat, val in stats.items()
    ]
    with open(path / "summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "stat", "value"])
        writer.writeheader()
        writer.writerows(rows)


def _export_stages_csv(results: dict, path: Path):
    rows = [
        {"stage": stage, "metric": metric_name, "stat": stat, "value": val}
        for stage, metrics in results["stages"].items()
        for metric_name, stats in metrics.items()
        for stat, val in (stats or {}).items()
    ]
    with open(path / "stages.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["stage", "metric", "stat", "value"])
        writer.writeheader()
        writer.writerows(rows)


def _export_config(config: PizzeriaConfig, path: Path):
    import dataclasses

    with open(path / "config.json", "w") as f:
        json.dump(dataclasses.asdict(config), f, indent=2)
