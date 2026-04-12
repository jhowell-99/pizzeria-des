from numpy import random as rn


def customer(pizzeria, customer_id):
    arrival_time = pizzeria.env.now

    # ORDER
    queue_start = pizzeria.env.now
    with pizzeria.waiter.request() as req:
        yield req
        queue_time = pizzeria.env.now - queue_start
        service_start = pizzeria.env.now
        order_time = sum(
            rn.exponential(pizzeria.config.mean_order_time / 2) for _ in range(2)
        )
        yield pizzeria.env.timeout(order_time)
        pizzeria.metrics.order.record(queue_time, pizzeria.env.now - service_start)

    # PREP + DOUGH
    yield pizzeria.env.process(create_pizza(pizzeria))

    # BAKE
    yield pizzeria.env.process(cook_pizza(pizzeria))

    # SERVE
    queue_start = pizzeria.env.now
    with pizzeria.waiter.request() as req:
        yield req
        queue_time = pizzeria.env.now - queue_start
        service_start = pizzeria.env.now
        serve_time = max(0.5, rn.exponential(pizzeria.config.mean_serve_time))
        yield pizzeria.env.timeout(serve_time)
        pizzeria.metrics.serve.record(queue_time, pizzeria.env.now - service_start)

    pizzeria.metrics.record_total(pizzeria.env.now - arrival_time)


def create_pizza(pizzeria):
    yield pizzeria.dough.get(1)

    queue_start = pizzeria.env.now
    with pizzeria.chef.request() as req:
        yield req
        queue_time = pizzeria.env.now - queue_start
        service_start = pizzeria.env.now
        prep_time = rn.triangular(
            pizzeria.config.min_prep_time,
            pizzeria.config.mean_prep_time,
            pizzeria.config.max_prep_time,
        )
        yield pizzeria.env.timeout(prep_time)
        pizzeria.metrics.prep.record(queue_time, pizzeria.env.now - service_start)


def cook_pizza(pizzeria):
    queue_start = pizzeria.env.now
    with pizzeria.oven.request() as req:
        yield req
        queue_time = pizzeria.env.now - queue_start
        service_start = pizzeria.env.now
        bake_time = rn.uniform(
            pizzeria.config.min_bake_time, pizzeria.config.max_bake_time
        )
        yield pizzeria.env.timeout(bake_time)
        pizzeria.metrics.bake.record(queue_time, pizzeria.env.now - service_start)


def customer_arrivals(pizzeria):
    i = 0
    while True:
        iat = rn.exponential(pizzeria.config.mean_interarrival_time)
        yield pizzeria.env.timeout(iat)
        i += 1
        pizzeria.env.process(customer(pizzeria, i))


def monitor_dough(pizzeria):
    while True:
        yield pizzeria.env.timeout(5)
        if (
            pizzeria.dough.level < pizzeria.config.low_dough_threshold
            and not pizzeria.emergency_batch_in_progress
        ):
            pizzeria.emergency_batch_in_progress = True
            pizzeria.env.process(emergency_dough_batch(pizzeria))


def emergency_dough_batch(pizzeria):
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
        pizzeria.emergency_batch_in_progress = False
