from dataclasses import dataclass, field
from typing import List

import numpy as np


@dataclass
class StageMetrics:
    """Tracks wait (queue) time and service time for a single stage."""

    name: str
    queue_times: List[float] = field(default_factory=list)
    service_times: List[float] = field(default_factory=list)

    def record(self, queue_time: float, service_time: float):
        self.queue_times.append(queue_time)
        self.service_times.append(service_time)

    def summary(self) -> dict:
        def stats(data):
            if not data:
                return {}
            a = np.array(data)
            return {
                "n": len(a),
                "mean": round(float(np.mean(a)), 3),
                "std": round(float(np.std(a)), 3),
                "min": round(float(np.min(a)), 3),
                "p50": round(float(np.percentile(a, 50)), 3),
                "p95": round(float(np.percentile(a, 95)), 3),
                "max": round(float(np.max(a)), 3),
            }

        return {
            "stage": self.name,
            "queue_time": stats(self.queue_times),
            "service_time": stats(self.service_times),
        }


@dataclass
class Metrics:
    completed_orders: int = 0
    abandoned_orders: int = 0  # future use — customers who wait too long

    order: StageMetrics = field(default_factory=lambda: StageMetrics("order"))
    prep: StageMetrics = field(default_factory=lambda: StageMetrics("prep"))
    bake: StageMetrics = field(default_factory=lambda: StageMetrics("bake"))
    serve: StageMetrics = field(default_factory=lambda: StageMetrics("serve"))

    total_wait_times: List[float] = field(default_factory=list)

    def record_total(self, total: float):
        self.total_wait_times.append(total)
        self.completed_orders += 1

    def summary(self) -> dict:
        total = np.array(self.total_wait_times)

        if len(total) == 0:
            total_stats = {}
        else:
            total_stats = {
                "mean": round(float(np.mean(total)), 3),
                "std": round(float(np.std(total)), 3),
                "min": round(float(np.min(total)), 3),
                "p50": round(float(np.percentile(total, 50)), 3),
                "p95": round(float(np.percentile(total, 95)), 3),
                "max": round(float(np.max(total)), 3),
            }

        return {
            "completed_orders": self.completed_orders,
            "total_time": total_stats,
            "stages": [
                self.order.summary(),
                self.prep.summary(),
                self.bake.summary(),
                self.serve.summary(),
            ],
        }

    def report(self):
        s = self.summary()
        width = 80

        print("=" * width)
        print(f"{'PIZZERIA SIMULATION REPORT':^{width}}")
        print("=" * width)
        print(f"  Completed orders : {s['completed_orders']}")
        print()

        if not s["total_time"]:
            print("  No completed orders to report.")
        else:
            t = s["total_time"]
            print("  Total time in system (min):")
            print(
                f"    mean={t['mean']}  std={t['std']}  "
                f"p50={t['p50']}  p95={t['p95']}  max={t['max']}"
            )
        print()
        header = f"  {'Stage':<10} {'Metric':<14} {'n':>5} {'mean':>7} {'std':>7} {'min':>7} {'p50':>7} {'p95':>7} {'max':>7}"
        print(header)
        print("  " + "-" * (width - 2))

        for stage in s["stages"]:
            for metric_name, vals in [
                ("queue", stage["queue_time"]),
                ("service", stage["service_time"]),
            ]:
                if not vals:
                    continue
                print(
                    f"  {stage['stage']:<10} {metric_name:<14} "
                    f"{vals['n']:>5} {vals['mean']:>7} {vals['std']:>7} "
                    f"{vals['min']:>7} {vals['p50']:>7} {vals['p95']:>7} {vals['max']:>7}"
                )

        print("=" * width)
