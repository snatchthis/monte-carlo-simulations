import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class MonteCarloForecast:
    def __init__(self, daily_tasks, forecast_days, num_simulations):
        self.daily_tasks = daily_tasks
        self.forecast_days = forecast_days
        self.num_simulations = num_simulations

    def run_simulation(self):
        simulations = []
        for _ in range(self.num_simulations):
            total_tasks = 0
            for _ in range(self.forecast_days):
                # Randomly select a number of tasks completed in a day from historical data
                tasks = np.random.choice(self.daily_tasks)
                total_tasks += tasks
            simulations.append(total_tasks)
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

# Load the data
file_path = 'history.csv'
data = pd.read_csv(file_path)

# Convert the 'Resolved' column to datetime format
data['Resolved'] = pd.to_datetime(data['Resolved'], format='%d.%m.%y %H:%M')

# Generate the full range of dates
date_range = pd.date_range(start=data['Resolved'].min(), end=data['Resolved'].max())

# Create a DataFrame for the full date range
full_date_range_df = pd.DataFrame(date_range, columns=['Date'])

# Count the number of tasks completed each day
daily_task_counts = data['Resolved'].dt.floor('d').value_counts().reset_index()
daily_task_counts.columns = ['Date', 'Task_Count']

# Ensure the Date columns are of the same type
full_date_range_df['Date'] = full_date_range_df['Date'].dt.date
daily_task_counts['Date'] = daily_task_counts['Date'].dt.date

# Merge with the full date range DataFrame and fill missing values with 0
daily_task_counts = pd.merge(full_date_range_df, daily_task_counts, on='Date', how='left').fillna(0)
daily_task_counts = daily_task_counts['Task_Count'].values

# Monte Carlo simulation parameters
forecast_days = 21  # Example: Forecast for 45 days
num_simulations = 10000

# Create forecast object
forecast = MonteCarloForecast(daily_task_counts, forecast_days, num_simulations)
simulations = forecast.run_simulation()
stats = forecast.generate_statistics(simulations)
forecast.plot_results(simulations)

stats
