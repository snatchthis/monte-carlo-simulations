import numpy as np
import matplotlib.pyplot as plt

class MonteCarloForecast:
    def __init__(self, data, sprint_length, num_simulations):
        self.data = data
        self.sprint_length = sprint_length
        self.num_simulations = num_simulations

    def run_simulation(self):
        simulations = []
        for _ in range(self.num_simulations):
            simulations.append(np.sum(np.random.choice(self.data, self.sprint_length)))
        return simulations

    def generate_statistics(self, simulations):
        return {
            'mean': np.mean(simulations),
            'median': np.median(simulations),
            'percentiles': {
                '90th': np.percentile(simulations, 90),
                '75th': np.percentile(simulations, 75),
                '25th': np.percentile(simulations, 25),
                '10th': np.percentile(simulations, 10)
            }
        }

    def plot_results(self, simulations):
        plt.hist(simulations, bins=50)
        plt.title('Monte Carlo Simulation Results')
        plt.xlabel('Number of Tasks')
        plt.ylabel('Frequency')
        plt.show()

# Sample data for testing purposes
data = [10, 12, 9, 11, 15, 14, 13, 12, 10, 11]
sprint_length = 3  # 3 weeks
num_simulations = 10000

forecast = MonteCarloForecast(data, sprint_length, num_simulations)
simulations = forecast.run_simulation()
stats = forecast.generate_statistics(simulations)
forecast.plot_results(simulations)

print("Forecast Statistics:", stats)
