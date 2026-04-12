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

A parallel process continuously produces pizza dough, competing for chef time.

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
{
  'completed_orders': 90,
  'avg_wait_time': 34.79,
  'max_wait_time': 52.39
}
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
