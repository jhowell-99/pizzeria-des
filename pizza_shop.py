from numpy.random import default_rng
import simpy

def simplified_pizza_process(env, name, mean_prepizza_time, mean_pizza_time,
                            mean_postpizza_time, pizzamaker, rg=default_rng(0)):
    """Process function modeling how a patient flows through system."""

    print(f"{name} entering pizzaria at {env.now:.4f}")
    
    # Yield for the pre-vac time
    yield env.timeout(rg.exponential(mean_prepizza_time))
    
    # Request vaccination staff to get vaccinated
    with pizzamaker.request() as request:
        print(f"{name} requested pizza at {env.now:.4f}")
        yield request
        print(f"{name} got pizza at {env.now:.4f}")
        yield env.timeout(rg.normal(mean_pizza_time, 0.5))

    # Yield for the post-vac time
    yield env.timeout(mean_postpizza_time)
    
    # The process is over, we would exit the clinic
    print(f"{name} exiting pizzaria clinic at {env.now:.4f}")

def customer_arrivals(env,
                        mean_interarrival_time,
                        mean_prepizza_time,
                        mean_pizza_time,
                        mean_postpizza_time,
                        pizzamaker,
                        rg=default_rng(0)):
    """Generate customer arrivals and processing"""

    # Create a counter to keep track of number of customers generated and 
    # to serve as unique customer id
    customer = 0

    # Infinite loop for generating customers
    while True:

        # Generate next interarrival time
        iat = rg.exponential(mean_interarrival_time)
        
        # This process will now yield to a 'timeout' event. This process will 
        # resume after iat time units.
        yield env.timeout(iat)

        # New customer generated = update counter of patients
        customer += 1
        
        print(f"Customer {customer} created at time {env.now}")

        customer_visit = simplified_pizza_process(
            env, 'Cusomter{}'.format(customer), mean_prepizza_time, 
            mean_pizza_time, mean_postpizza_time, pizzamaker
        )

        env.process(customer_visit)

# Initialize a simulation environment
env = simpy.Environment()

# set input values
mean_interarrival_time = 10.0
mean_prepizza_time = 5.0
mean_pizza_time = 10.0
mean_postpizza_time = 2.0
num_pizzamakers = 2

pizzamaker = simpy.Resource(env, num_pizzamakers)

# Create a process generator and start it and add it to the env
# env.process() starts the patient_arrivals process and adds it to the environment

env.process(customer_arrivals(env, mean_interarrival_time, mean_prepizza_time,
                            mean_pizza_time, mean_postpizza_time, pizzamaker))

runtime = 60
# Run the simulation
env.run(until=runtime)