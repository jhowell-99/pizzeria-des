import simpy

from pizzeria_sim.metrics import Metrics
from pizzeria_sim.processes import (
    customer_arrivals,
    make_dough,
)


class Pizzeria:
    def __init__(self, env, config):
        self.env = env
        self.config = config

        # Resources
        self.oven = simpy.Resource(env, capacity=config.num_ovens)
        self.chef = simpy.Resource(env, capacity=config.num_chefs)
        self.waiter = simpy.Resource(env, capacity=config.num_waiters)

        # Consumable
        self.dough = simpy.Container(
            env,
            capacity=config.dough_capacity,
            init=config.initial_dough,
        )

        self.metrics = Metrics()

    def run(self):
        # Start processes
        self.env.process(customer_arrivals(self))
        self.env.process(make_dough(self))
