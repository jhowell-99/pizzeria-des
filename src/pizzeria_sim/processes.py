import random


def customer_arrivals(pizzeria):
    i = 0
    while True:
        yield pizzeria.env.timeout(random.expovariate(pizzeria.config.arrival_rate))
        i += 1
        pizzeria.env.process(customer(pizzeria, i))


def customer(pizzeria, customer_id):
    arrival_time = pizzeria.env.now

    # ORDER
    with pizzeria.waiter.request() as req:
        yield req
        yield pizzeria.env.timeout(pizzeria.config.order_time)

    # CREATE PIZZA
    yield pizzeria.env.process(create_pizza(pizzeria))

    # COOK
    yield pizzeria.env.process(cook_pizza(pizzeria))

    # SERVE
    with pizzeria.waiter.request() as req:
        yield req
        yield pizzeria.env.timeout(pizzeria.config.serve_time)

    # METRICS
    total_time = pizzeria.env.now - arrival_time
    pizzeria.metrics.completed_orders += 1
    pizzeria.metrics.wait_times.append(total_time)


def create_pizza(pizzeria):
    # wait for dough
    yield pizzeria.dough.get(1)

    # chef prepares
    with pizzeria.chef.request() as req:
        yield req
        yield pizzeria.env.timeout(pizzeria.config.prep_time)


def cook_pizza(pizzeria):
    with pizzeria.oven.request() as req:
        yield req
        yield pizzeria.env.timeout(pizzeria.config.bake_time)


def make_dough(pizzeria):
    while True:
        with pizzeria.chef.request() as req:
            yield req
            yield pizzeria.env.timeout(pizzeria.config.dough_time)
            yield pizzeria.dough.put(1)
