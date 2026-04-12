# Pizzeria Discrete Event Simulation (SimPy)

A discrete event simulation (DES) of a pizzeria built using **SimPy**. This project models the flow of customers and pizza production, capturing resource constraints such as chefs, ovens, waiters, and dough supply.

---

## Overview

The simulation models a typical pizzeria workflow:

1. Customer arrives
2. Order is taken (waiter)
3. Pizza is prepared (chef + dough)
4. Pizza is cooked (oven)
5. Pizza is served (waiter)
6. Customer leaves

A sim starts with an amount of dough. Extra dough will be made if values drop too low.

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd pizzeria-des
```

---

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install requirements.txt
```

---

## Running the Simulation

Run the baseline simulation:

```bash
python experiments/baseline.py
```

Example output:

```
================================================================================
                           PIZZERIA SIMULATION REPORT                           
================================================================================
  Completed orders : 71

  Total time in system (min):
    mean=28.485  std=7.318  p50=28.799  p95=38.706  max=46.221

  Stage      Metric             n    mean     std     min     p50     p95     max
  ------------------------------------------------------------------------------
  order      queue             77   0.487   0.924     0.0     0.0   2.345   3.703
  order      service           77   1.928   1.265   0.078   1.673    4.05   6.198
  prep       queue             77   0.376    0.89     0.0     0.0   2.292   4.068
  prep       service           77    5.56   1.224   3.385    5.39   7.692   8.418
  bake       queue             71   6.005   5.937     0.0   4.942  17.819  20.796
  bake       service           71  11.708   1.147  10.001  11.412  13.602  13.921
  serve      queue             71   0.278   0.782     0.0     0.0   2.151    4.03
  serve      service           71    2.17   2.227     0.5   1.011   6.857   9.858
================================================================================
```

---

## Configuring the Simulation

All parameters are defined in:

```
src/pizzeria_sim/config.py
```

Example:

```python
PizzeriaConfig(
    num_chefs=2,
    num_ovens=2,
    num_waiters=1,
    arrival_rate=1/5
)
```

Modify these values to explore different scenarios.

---

## Future Improvements

* Resource utilisation tracking
* Queue length monitoring
* Multiple pizza types
* Batch oven cooking
* Scenario comparison & plotting
* Stochastic analysis (multiple runs, averaging)

---

## Author

Jamie Howell
