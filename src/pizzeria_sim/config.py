from dataclasses import dataclass


@dataclass
class PizzeriaConfig:
    num_ovens: int = 2
    num_chefs: int = 2
    num_waiters: int = 1

    dough_capacity: int = 50
    initial_dough: int = 10

    arrival_rate: float = 1 / 5  # customers every ~5 mins

    order_time: float = 2
    prep_time: float = 5
    bake_time: float = 10
    serve_time: float = 2
    dough_time: float = 4

    sim_time: int = 1000
