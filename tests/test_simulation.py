# tests/test_simulation.py
import numpy as np


def test_completed_orders_nonzero(pizzeria, env):
    np.random.seed(42)
    pizzeria.run()
    env.run(until=pizzeria.config.sim_time)
    assert pizzeria.metrics.completed_orders > 0


def test_dough_never_goes_negative(pizzeria, env):
    """Container level should never drop below zero."""
    levels = []

    def monitor():
        while True:
            levels.append(pizzeria.dough.level)
            yield env.timeout(1)

    pizzeria.run()
    env.process(monitor())
    env.run(until=pizzeria.config.sim_time)
    assert min(levels) >= 0
