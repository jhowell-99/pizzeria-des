# tests/test_config.py
import numpy as np

from pizzeria_sim.config import PizzeriaConfig
from pizzeria_sim.model import Pizzeria


def test_single_chef_single_oven(env):
    """Simulation should still complete with minimal resources."""
    np.random.seed(42)
    config = PizzeriaConfig(num_chefs=1, num_ovens=1, num_waiters=1)
    p = Pizzeria(env, config)
    p.run()
    env.run(until=config.sim_time)
    assert p.metrics.completed_orders > 0


def test_high_dough_supply_no_emergency_batch(env):
    """With abundant dough, emergency batch should never trigger."""
    np.random.seed(42)
    config = PizzeriaConfig(initial_dough_batch=9999, dough_capacity=9999)
    p = Pizzeria(env, config)
    p.run()
    env.run(until=config.sim_time)
    assert not p.emergency_batch_in_progress
