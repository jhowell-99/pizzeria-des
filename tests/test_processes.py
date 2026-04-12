# tests/test_processes.py
import numpy as np

from pizzeria_sim.config import PizzeriaConfig
from pizzeria_sim.model import Pizzeria
from pizzeria_sim.processes import cook_pizza, create_pizza


def test_cook_pizza_uses_oven(pizzeria, env):
    """Oven should be occupied during cooking then released."""
    env.process(cook_pizza(pizzeria))

    env.step()  # advance to just after request
    assert pizzeria.oven.count == 1

    env.run()
    assert pizzeria.oven.count == 0


def test_create_pizza_consumes_dough(pizzeria, env):
    """Each pizza should consume exactly 1 dough ball."""
    initial = pizzeria.dough.level
    env.process(create_pizza(pizzeria))
    env.run()
    assert pizzeria.dough.level == initial - 1


def test_create_pizza_blocks_when_no_dough(env, default_config):
    """Process should block indefinitely if dough container is empty."""
    np.random.seed(42)
    empty_config = PizzeriaConfig(initial_dough_batch=0)
    p = Pizzeria(env, empty_config)

    env.process(create_pizza(p))
    env.run(until=100)

    # No dough consumed, process never completed
    assert p.dough.level == 0
    assert p.metrics.completed_orders == 0
