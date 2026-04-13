from dataclasses import dataclass


@dataclass
class PizzeriaConfig:
    num_ovens: int = 3
    num_chefs: int = 3
    num_waiters: int = 2

    dough_capacity: int = 100
    initial_dough_batch: int = 100  # dough balls made before shift starts
    low_dough_threshold: int = 30  # trigger an emergency batch if stock drops here
    emergency_batch_size: int = 30  # how many to make in emergency batch

    mean_interarrival_time: float = 5.0  # Poisson arrivals → Exponential IAT

    # Order taking — Erlang-2 (sum of 2 exponentials)
    mean_order_time: float = 2.0  # mean of the full order duration

    # Pizza prep — Triangular
    min_prep_time: float = 3.0
    mean_prep_time: float = 5.0  # mode of triangular
    max_prep_time: float = 9.0

    # Baking — Uniform
    min_bake_time: float = 10.0
    max_bake_time: float = 14.0

    # Serving — Exponential
    mean_serve_time: float = 2.0

    # Dough batch — Normal, made once before shift
    mean_dough_batch_time: float = 30.0  # 30 min to prep a full batch
    std_dough_batch_time: float = 5.0

    sim_time: int = 200
