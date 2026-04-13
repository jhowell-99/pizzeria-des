# Pizzeria Discrete Event Simulation (SimPy)

A discrete event simulation (DES) of a pizzeria built using **SimPy**. This project models the flow of customers and pizza production, capturing resource constraints such as chefs, ovens, waiters, and dough supply. Stochastic analysis is supported via multiple replications with confidence interval reporting.

---

## Overview

The simulation models a typical pizzeria workflow:

1. Customer arrives (Poisson process)
2. Order is taken (waiter — Erlang-2)
3. Pizza is prepared (chef + dough — Triangular)
4. Pizza is cooked (oven — Uniform)
5. Pizza is served (waiter — Exponential)
6. Customer leaves

Dough is prepared in a batch before the shift begins. If stock drops below a configurable threshold mid-shift, an emergency batch is triggered automatically.

---

## Project Structure

```
pizzeria-des/
├── src/
│   └── pizzeria_sim/
│       ├── config.py        # simulation parameters
│       ├── model.py         # Pizzeria class and resource setup
│       ├── processes.py     # SimPy processes
│       └── metrics.py       # per-stage metrics and reporting
├── experiments/
│   ├── baseline.py          # entry point
│   └── replications.py      # stochastic replication runner
├── outputs/                 # timestamped results folders (git-ignored)
└── README.md
```

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/jhowell-99/pizzeria-des
cd pizzeria-des
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -e .
pip install -r requirements.txt
```

---

## Running the Simulation

Run the baseline experiment:

```bash
python experiments/baseline.py
```

This runs 200 replications by default and writes results to a timestamped folder under `outputs/`:

Example output:

```
Running replications: 100%|██████████| 200/200 [00:12<00:00,  2.41run/s]
Results written to outputs/20240413_142301/
```

---

## Configuring the Simulation

All parameters are defined in `src/pizzeria_sim/config.py`:

```python
@dataclass
class PizzeriaConfig:
    num_ovens: int = 2
    num_chefs: int = 2
    num_waiters: int = 1

    dough_capacity: int = 100
    initial_dough_batch: int = 80
    low_dough_threshold: int = 20
    emergency_batch_size: int = 20

    mean_interarrival_time: float = 5.0   # minutes between arrivals, poisson

    mean_order_time: float = 2.0          # Erlang-2
    min_prep_time: float = 3.0            # Triangular
    mean_prep_time: float = 5.0
    max_prep_time: float = 9.0
    min_bake_time: float = 10.0           # Uniform
    max_bake_time: float = 14.0
    mean_serve_time: float = 2.0          # Exponential

    mean_dough_batch_time: float = 15.0
    std_dough_batch_time: float = 3.0

    sim_time: int = 360                   # 6 hours (1 tick = 1 minute)
```

To run a different scenario, create a new experiment file under `experiments/` and pass a modified config:

```python
config = PizzeriaConfig(num_ovens=3, num_chefs=3)
results = run_replications(config, n=30)
export_results(results, config)
```

---

## Outputs

Each run produces four files in a timestamped folder:

| File | Contents |
|---|---|
| `config.json` | Full config used for the run |
| `results.json` | Complete nested results including all CIs |
| `summary.csv` | Completed orders and total time statistics |
| `stages.csv` | Per-stage queue and service time with 95% CIs |

---

## Future Improvements

- Resource utilisation tracking
- Queue length monitoring over time
- Multiple pizza types with different prep/bake times
- Batch oven cooking
- Scenario comparison and plotting
- Customer abandonment (reneging) after a maximum wait threshold

---

## Author

Jamie Howell