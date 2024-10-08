import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, StringVar, Frame, ttk
from tkinter import messagebox
from tkinter.ttk import Notebook
from tkcalendar import DateEntry
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

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

def load_data(start_date, end_date, file_path):
    # Load and prepare data
    data = pd.read_csv(file_path)
    data['Resolved'] = pd.to_datetime(data['Resolved'], format='%d/%b/%y %I:%M %p').dt.date
    data = data[(data['Resolved'] >= start_date) & (data['Resolved'] <= end_date)]
    date_range = pd.date_range(start=data['Resolved'].min(), end=data['Resolved'].max())
    full_date_range_df = pd.DataFrame(date_range, columns=['Date'])
    daily_task_counts = data['Resolved'].value_counts().reset_index()
    daily_task_counts.columns = ['Date', 'Task_Count']
    full_date_range_df['Date'] = full_date_range_df['Date'].dt.date
    daily_task_counts['Date'] = daily_task_counts['Date']
    daily_task_counts = pd.merge(full_date_range_df, daily_task_counts, on='Date', how='left').fillna(0)
    return daily_task_counts

def update_date_range(*args):
    start_date = start_date_var.get_date()
    end_date = end_date_var.get_date()
    num_days = (end_date - start_date).days
    date_range_text.set(f"Number of days between selected dates: {num_days}")

def update_date_range_from_file(*args):
    file_path = selected_file.get()
    if file_path:
        data = pd.read_csv(file_path)
        data['Resolved'] = pd.to_datetime(data['Resolved'], format='%d/%b/%y %I:%M %p').dt.date
        default_start_date = data['Resolved'].min()
        default_end_date = data['Resolved'].max()
        start_date_var.set_date(default_start_date)
        end_date_var.set_date(default_end_date)
        update_date_range()

def run_simulation():
    try:
        forecast_days = int(forecast_days_var.get())
        num_simulations = int(num_simulations_var.get())
        start_date = start_date_var.get_date()
        end_date = end_date_var.get_date()
        file_path = selected_file.get()

        if not file_path:
            messagebox.showerror("Input Error", "Please select a CSV file.")
            return

        daily_task_counts_df = load_data(start_date, end_date, file_path)
        daily_task_counts = daily_task_counts_df['Task_Count'].values
        forecast = MonteCarloForecast(daily_task_counts)
        simulations = forecast.run_simulation(forecast_days, num_simulations)
        stats = forecast.generate_statistics(simulations)
        plot = forecast.plot_results(simulations)
        plot.gcf().set_size_inches(20, 6)
        plt.xticks(np.arange(min(simulations), max(simulations) + 1, 1), rotation=45, ha='right', fontsize='small')

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

        # Display plot in the Monte Carlo tab
        for widget in monte_carlo_tab.winfo_children():
            widget.destroy()  # Clear previous plot
        canvas = FigureCanvasTkAgg(plot.gcf(), master=monte_carlo_tab)
        canvas.draw()
        canvas.get_tk_widget().pack()

        # Display throughput chart in the Throughput tab
        throughput_plot = plt.figure(figsize=(20, 6))
        plt.bar(daily_task_counts_df['Date'], daily_task_counts_df['Task_Count'])
        plt.xticks(daily_task_counts_df['Date'], daily_task_counts_df['Date'], rotation=45, ha='right', fontsize='small')
        for label in plt.gca().get_xticklabels():
            if label.get_text():
                date_obj = pd.to_datetime(label.get_text())
                if date_obj.weekday() in [5, 6]:
                    label.set_color('red')
        plt.title('Throughput Over Time')
        plt.xlabel('Date')
        plt.xticks(rotation=45, ha='right')
        plt.ylabel('Number of Tasks Resolved')
        plt.tight_layout()

        for widget in throughput_tab.winfo_children():
            widget.destroy()  # Clear previous plot
        throughput_canvas = FigureCanvasTkAgg(throughput_plot, master=throughput_tab)
        throughput_canvas.draw()
        throughput_canvas.get_tk_widget().pack()
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for the parameters.")

# Create the main window
root = Tk()
root.title("Monte Carlo Simulation")

# Initialize variables
date_range_text = StringVar()

# Input frame
input_frame = Frame(root)
input_frame.pack(pady=10)

# Select CSV file from dropdown
Label(input_frame, text="Select CSV file from 'history' folder:").grid(row=0, column=0, padx=10)
selected_file = StringVar()
csv_files = [f"history/{file}" for file in os.listdir('history') if file.endswith('.csv')]
file_dropdown = ttk.Combobox(input_frame, textvariable=selected_file, values=csv_files)
file_dropdown.grid(row=0, column=1, padx=10)
file_dropdown.bind("<<ComboboxSelected>>", update_date_range_from_file)

Label(input_frame, text="Enter the number of days for the forecast period:").grid(row=1, column=0, padx=10)
forecast_days_var = StringVar(value="21")
Entry(input_frame, textvariable=forecast_days_var).grid(row=1, column=1, padx=10)

Label(input_frame, text="Enter the number of simulations:").grid(row=2, column=0, padx=10)
num_simulations_var = StringVar(value="10000")
Entry(input_frame, textvariable=num_simulations_var).grid(row=2, column=1, padx=10)

Label(input_frame, text="Select the start date for the historical data:").grid(row=3, column=0, padx=10)
start_date_var = DateEntry(input_frame, date_pattern='yyyy-mm-dd')
start_date_var.grid(row=3, column=1, padx=10)

Label(input_frame, text="Select the end date for the historical data:").grid(row=4, column=0, padx=10)
end_date_var = DateEntry(input_frame, date_pattern='yyyy-mm-dd')
end_date_var.grid(row=4, column=1, padx=10)

Button(input_frame, text="Run Simulation", command=run_simulation).grid(row=5, columnspan=2, pady=10)

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

# Tab control for plots
tab_control = Notebook(root)
monte_carlo_tab = Frame(tab_control)
throughput_tab = Frame(tab_control)
tab_control.add(monte_carlo_tab, text='Monte Carlo Plot')
tab_control.add(throughput_tab, text='Throughput Chart')
tab_control.pack(expand=1, fill='both')

# Run the main loop
root.mainloop()