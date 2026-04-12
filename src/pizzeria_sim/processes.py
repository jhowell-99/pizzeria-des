from numpy import random as rn


def monitor_dough(pizzeria):
    """
    Watches dough stock and triggers an emergency batch if it
    drops below the low_dough_threshold mid-shift.
    """
    while True:
        yield pizzeria.env.timeout(5)
        if (
            pizzeria.dough.level < pizzeria.config.low_dough_threshold
            and not pizzeria.emergency_batch_in_progress
        ):
            print(f"[t={pizzeria.env.now:.1f}] Low dough! Triggering emergency batch.")
            pizzeria.emergency_batch_in_progress = True
            pizzeria.env.process(emergency_dough_batch(pizzeria))


def emergency_dough_batch(pizzeria):
    """
    A smaller mid-shift batch when stock runs low.
    Competes with chefs doing prep — realistic mid-service scramble.
    """
    with pizzeria.chef.request() as req:
        yield req
        batch_time = max(
            0.0,
            rn.normal(
                pizzeria.config.mean_dough_batch_time / 2,
                pizzeria.config.std_dough_batch_time,
            ),
        )
        yield pizzeria.env.timeout(batch_time)
        yield pizzeria.dough.put(pizzeria.config.emergency_batch_size)
        pizzeria.emergency_batch_in_progress = False  # clear flag when done
        print(
            f"[t={pizzeria.env.now:.1f}] Emergency batch done: "
            f"+{pizzeria.config.emergency_batch_size} dough balls"
        )


def customer_arrivals(pizzeria):
    """
    Generate customers according to a poisson arrival process
    """
    i = 0
    while True:
        iat = rn.exponential(
            pizzeria.config.mean_interarrival_time
        )  # interarrival time

        yield pizzeria.env.timeout(iat)
        i += 1
        pizzeria.env.process(customer(pizzeria, i))


def customer(pizzeria, customer_id):
    arrival_time = pizzeria.env.now

    # ORDER — Erlang-2 (two-phase exponential) for realistic order taking
    with pizzeria.waiter.request() as req:
        yield req
        order_time = sum(
            rn.exponential(pizzeria.config.mean_order_time / 2) for _ in range(2)
        )
        yield pizzeria.env.timeout(order_time)

    # CREATE PIZZA
    yield pizzeria.env.process(create_pizza(pizzeria))

    # COOK
    yield pizzeria.env.process(cook_pizza(pizzeria))

    # SERVE — exponential
    with pizzeria.waiter.request() as req:
        yield req
        serve_time = rn.exponential(pizzeria.config.mean_serve_time)
        yield pizzeria.env.timeout(serve_time)

    # METRICS
    total_time = pizzeria.env.now - arrival_time
    pizzeria.metrics.completed_orders += 1
    pizzeria.metrics.wait_times.append(total_time)


def create_pizza(pizzeria):
    # wait for dough
    yield pizzeria.dough.get(1)

    # chef prepares — triangular (min, mode, max)
    with pizzeria.chef.request() as req:
        yield req
        prep_time = rn.triangular(
            pizzeria.config.min_prep_time,
            pizzeria.config.mean_prep_time,
            pizzeria.config.max_prep_time,
        )
        yield pizzeria.env.timeout(prep_time)


def cook_pizza(pizzeria):
    with pizzeria.oven.request() as req:
        yield req
        # Uniform — oven time is tightly controlled
        bake_time = rn.uniform(
            pizzeria.config.min_bake_time,
            pizzeria.config.max_bake_time,
        )
        yield pizzeria.env.timeout(bake_time)


def make_dough(pizzeria):
    while True:
        with pizzeria.chef.request() as req:
            yield req
            # Normal — dough making is a practiced, consistent task
            dough_time = max(
                0.0,
                rn.normal(
                    pizzeria.config.mean_dough_time, pizzeria.config.std_dough_time
                ),
            )
            yield pizzeria.env.timeout(dough_time)
            yield pizzeria.dough.put(1)
