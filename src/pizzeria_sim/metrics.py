class Metrics:
    def __init__(self):
        self.wait_times = []
        self.completed_orders = 0

    def summary(self):
        if not self.wait_times:
            return {}

        return {
            "completed_orders": self.completed_orders,
            "avg_wait_time": sum(self.wait_times) / len(self.wait_times),
            "max_wait_time": max(self.wait_times),
        }
