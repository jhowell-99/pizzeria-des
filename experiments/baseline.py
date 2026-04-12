import simpy

from pizzeria_sim.config import PizzeriaConfig
from pizzeria_sim.model import Pizzeria


def main():
    env = simpy.Environment()
    config = PizzeriaConfig()

    model = Pizzeria(env, config)
    model.run()

    env.run(until=config.sim_time)

    model.metrics.report()


if __name__ == "__main__":
    main()
