import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, StringVar, Frame
from tkinter import messagebox
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MonteCarloForecast:
    def __init__(self, daily_tasks):
        self.daily_tasks = daily_tasks

    def run_simulation(self, forecast_days, num_simulations):
        simulations = []
        for _ in range(num_simulations):
            total_tasks = 0
            for _ in range(forecast_days):
                tasks = np.random.choice(self.daily_tasks)
                total_tasks += tasks
            simulations.append(total_tasks)
        return simulations

    def generate_statistics(self, simulations):
        stats = {
            'mean': np.mean(simulations),
            'median': np.median(simulations),
            'std_dev': np.std(simulations),
            'percentiles': {
                '90th': np.percentile(simulations, 90),
                '75th': np.percentile(simulations, 75),
                '25th': np.percentile(simulations, 25),
                '10th': np.percentile(simulations, 10)
            }
        }
        return stats

    def plot_results(self, simulations):
        plt.hist(simulations, bins=50)
        plt.title('Monte Carlo Simulation Results')
        plt.xlabel('Number of Tasks')
        plt.ylabel('Frequency')
        plt.tight_layout()
        return plt

def load_data(start_date, end_date):
    # Load and prepare data
    file_path = 'history.csv'  # Ensure the CSV file is in the same directory
    data = pd.read_csv(file_path)
    data['Resolved'] = pd.to_datetime(data['Resolved'], format='%d.%m.%y %H:%M').dt.date
    data = data[(data['Resolved'] >= start_date) & (data['Resolved'] <= end_date)]
    date_range = pd.date_range(start=data['Resolved'].min(), end=data['Resolved'].max())
    full_date_range_df = pd.DataFrame(date_range, columns=['Date'])
    daily_task_counts = data['Resolved'].value_counts().reset_index()
    daily_task_counts.columns = ['Date', 'Task_Count']
    full_date_range_df['Date'] = full_date_range_df['Date'].dt.date
    daily_task_counts['Date'] = daily_task_counts['Date']
    daily_task_counts = pd.merge(full_date_range_df, daily_task_counts, on='Date', how='left').fillna(0)
    daily_task_counts = daily_task_counts['Task_Count'].values
    return daily_task_counts

def update_date_range(*args):
    start_date = start_date_var.get_date()
    end_date = end_date_var.get_date()
    num_days = (end_date - start_date).days
    date_range_text.set(f"Number of days between selected dates: {num_days}")

def run_simulation():
    try:
        forecast_days = int(forecast_days_var.get())
        num_simulations = int(num_simulations_var.get())
        start_date = start_date_var.get_date()
        end_date = end_date_var.get_date()
        daily_task_counts = load_data(start_date, end_date)
        forecast = MonteCarloForecast(daily_task_counts)
        simulations = forecast.run_simulation(forecast_days, num_simulations)
        stats = forecast.generate_statistics(simulations)
        plot = forecast.plot_results(simulations)

        # Display results
        results_text.set(f"Mean: {stats['mean']}\n"
                         f"Median: {stats['median']}\n"
                         f"Standard Deviation: {stats['std_dev']}\n"
                         f"90th Percentile: {stats['percentiles']['90th']}\n"
                         f"75th Percentile: {stats['percentiles']['75th']}\n"
                         f"25th Percentile: {stats['percentiles']['25th']}\n"
                         f"10th Percentile: {stats['percentiles']['10th']}")

        guidance_text.set(f"Guidance:\n"
                          f"The mean number of tasks expected to be completed is {stats['mean']:.2f}.\n"
                          f"Half of the simulations resulted in fewer than {stats['median']} tasks and half in more.\n"
                          f"The standard deviation is {stats['std_dev']:.2f}, indicating the variability in task completion.\n"
                          f"90% of the simulations resulted in fewer than {stats['percentiles']['90th']} tasks.\n"
                          f"75% of the simulations resulted in fewer than {stats['percentiles']['75th']} tasks.\n"
                          f"25% of the simulations resulted in fewer than {stats['percentiles']['25th']} tasks.\n"
                          f"10% of the simulations resulted in fewer than {stats['percentiles']['10th']} tasks.")

        # Display plot
        for widget in plot_frame.winfo_children():
            widget.destroy()  # Clear previous plot
        canvas = FigureCanvasTkAgg(plot.gcf(), master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for the parameters.")

# Load the data to get the date range for default values
file_path = 'history.csv'
data = pd.read_csv(file_path)
data['Resolved'] = pd.to_datetime(data['Resolved'], format='%d.%m.%y %H:%M').dt.date
default_start_date = data['Resolved'].min()
default_end_date = data['Resolved'].max()

# Create the main window
root = Tk()
root.title("Monte Carlo Simulation")

# Input frame
input_frame = Frame(root)
input_frame.pack(pady=10)

Label(input_frame, text="Enter the number of days for the forecast period:").grid(row=0, column=0, padx=10)
forecast_days_var = StringVar(value="21")
Entry(input_frame, textvariable=forecast_days_var).grid(row=0, column=1, padx=10)

Label(input_frame, text="Enter the number of simulations:").grid(row=1, column=0, padx=10)
num_simulations_var = StringVar(value="10000")
Entry(input_frame, textvariable=num_simulations_var).grid(row=1, column=1, padx=10)

Label(input_frame, text="Select the start date for the historical data:").grid(row=2, column=0, padx=10)
start_date_var = DateEntry(input_frame, date_pattern='yyyy-mm-dd', year=default_start_date.year, month=default_start_date.month, day=default_start_date.day)
start_date_var.grid(row=2, column=1, padx=10)

Label(input_frame, text="Select the end date for the historical data:").grid(row=3, column=0, padx=10)
end_date_var = DateEntry(input_frame, date_pattern='yyyy-mm-dd', year=default_end_date.year, month=default_end_date.month, day=default_end_date.day)
end_date_var.grid(row=3, column=1, padx=10)

date_range_text = StringVar()
num_days = (default_end_date - default_start_date).days
date_range_text.set(f"Number of days between selected dates: {num_days}")
Label(input_frame, textvariable=date_range_text).grid(row=4, columnspan=2, pady=10)

Button(input_frame, text="Run Simulation", command=run_simulation).grid(row=5, columnspan=2, pady=10)

# Bind date changes to update_date_range function
start_date_var.bind("<<DateEntrySelected>>", update_date_range)
end_date_var.bind("<<DateEntrySelected>>", update_date_range)

# Results frame
results_frame = Frame(root)
results_frame.pack(pady=10)

results_text = StringVar()
Label(results_frame, textvariable=results_text, justify="left").pack()

# Guidance frame
guidance_frame = Frame(root)
guidance_frame.pack(pady=10)

guidance_text = StringVar()
Label(guidance_frame, textvariable=guidance_text, justify="left").pack()

# Plot frame
plot_frame = Frame(root)
plot_frame.pack(pady=10)

# Run the main loop
root.mainloop()
