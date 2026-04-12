import simpy

from pizzeria_sim.metrics import Metrics
from pizzeria_sim.processes import (
    customer_arrivals,
    monitor_dough,
)


class Pizzeria:
    def __init__(self, env, config):
        self.env = env
        self.config = config

        # Resources
        self.oven = simpy.Resource(env, capacity=config.num_ovens)
        self.chef = simpy.Resource(env, capacity=config.num_chefs)
        self.waiter = simpy.Resource(env, capacity=config.num_waiters)

        # Consumable — start empty, opening batch fills it at t=0
        self.dough = simpy.Container(
            env,
            capacity=config.dough_capacity,
            init=config.initial_dough_batch,
        )

        self.emergency_batch_in_progress = False

        self.metrics = Metrics()

    def run(self):
        self.env.process(monitor_dough(self))
        self.env.process(customer_arrivals(self))
