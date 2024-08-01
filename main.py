import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from tkinter import Tk, Label, Entry, Button, StringVar, Frame
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class MonteCarloForecast:
    def __init__(self, daily_tasks, num_simulations):
        self.daily_tasks = daily_tasks
        self.num_simulations = num_simulations

    def run_simulation(self, forecast_days):
        simulations = []
        for _ in range(self.num_simulations):
            total_tasks = 0
            for _ in range(forecast_days):
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
        plt.tight_layout()
        return plt


def load_data():
    # Load and prepare data
    file_path = 'history.csv'  # Ensure the CSV file is in the same directory
    data = pd.read_csv(file_path)
    data['Resolved'] = pd.to_datetime(data['Resolved'], format='%d.%m.%y %H:%M')
    date_range = pd.date_range(start=data['Resolved'].min(), end=data['Resolved'].max())
    full_date_range_df = pd.DataFrame(date_range, columns=['Date'])
    daily_task_counts = data['Resolved'].dt.floor('d').value_counts().reset_index()
    daily_task_counts.columns = ['Date', 'Task_Count']
    full_date_range_df['Date'] = full_date_range_df['Date'].dt.date
    daily_task_counts['Date'] = daily_task_counts['Date'].dt.date
    daily_task_counts = pd.merge(full_date_range_df, daily_task_counts, on='Date', how='left').fillna(0)
    daily_task_counts = daily_task_counts['Task_Count'].values
    return daily_task_counts


def run_simulation():
    try:
        forecast_days = int(forecast_days_var.get())
        forecast = MonteCarloForecast(daily_task_counts, num_simulations)
        simulations = forecast.run_simulation(forecast_days)
        stats = forecast.generate_statistics(simulations)
        plot = forecast.plot_results(simulations)

        # Display results
        results_text.set(f"Mean: {stats['mean']}\n"
                         f"Median: {stats['median']}\n"
                         f"90th Percentile: {stats['percentiles']['90th']}\n"
                         f"75th Percentile: {stats['percentiles']['75th']}\n"
                         f"25th Percentile: {stats['percentiles']['25th']}\n"
                         f"10th Percentile: {stats['percentiles']['10th']}")

        # Display plot
        canvas = FigureCanvasTkAgg(plot.gcf(), master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number of days.")


# Load the data
daily_task_counts = load_data()
num_simulations = 10000

# Create the main window
root = Tk()
root.title("Monte Carlo Simulation")

# Input frame
input_frame = Frame(root)
input_frame.pack(pady=10)

Label(input_frame, text="Enter the number of days for the forecast period:").grid(row=0, column=0, padx=10)
forecast_days_var = StringVar()
Entry(input_frame, textvariable=forecast_days_var).grid(row=0, column=1, padx=10)
Button(input_frame, text="Run Simulation", command=run_simulation).grid(row=0, column=2, padx=10)

# Results frame
results_frame = Frame(root)
results_frame.pack(pady=10)

results_text = StringVar()
Label(results_frame, textvariable=results_text, justify="left").pack()

# Plot frame
plot_frame = Frame(root)
plot_frame.pack(pady=10)

# Run the main loop
root.mainloop()
