from replications import export_results, run_replications


def main():
    from pizzeria_sim.config import PizzeriaConfig

    config = PizzeriaConfig()
    results = run_replications(config, n=200)
    export_results(results, config, output_dir="outputs")


if __name__ == "__main__":
    main()
