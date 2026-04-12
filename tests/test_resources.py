# tests/test_resources.py
from pizzeria_sim.processes import cook_pizza, create_pizza, customer


def test_chef_released_after_prep(pizzeria, env):
    """Chef resource should always be released even if process completes."""
    env.process(create_pizza(pizzeria))
    env.run()
    assert pizzeria.chef.count == 0  # no chef left hanging


def test_oven_capacity_respected(pizzeria, env):
    """Oven count should never exceed capacity at any point."""
    for _ in range(10):
        env.process(cook_pizza(pizzeria))

    while env.peek() < float("inf"):
        env.step()
        assert pizzeria.oven.count <= pizzeria.config.num_ovens


def test_waiter_contention(pizzeria, env):
    """Queue should build when waiter is busy."""

    for i in range(5):  # 5 customers, 1 waiter
        env.process(customer(pizzeria, i))
    env.step()
    assert pizzeria.waiter.queue or pizzeria.waiter.count == 1
