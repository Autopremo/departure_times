import tkinter as tk
from tkinter import ttk
import pandas as pd
from datetime import datetime, timedelta, time as dt_time
import os

# File names for weekdays and weekends
data_file_weekday = "departure_times_weekday.csv"
data_file_weekend = "departure_times_weekend.csv"

# Sample data for weekdays
default_data_weekday = {
    "CarNo": [101, 103, 105, 107, 109, 111, 113, 115, 117, 119, 121, 123, 201, 203, 205, 207, 209, 211, 213, 215, 219, 221, 223, 225, 227, 229, 231, 233, 500, 560, 580, 550, 530, 710, 510, 740, 551, 570, 581, "700/1", "700/2"],
    "Leave Time": ["20:15", "20:30", "20:30", "21:00", "20:30", "21:00", "21:00", "21:00", "22:00", "21:00", "22:00", "22:00", "22:20", "22:55", "23:00", "23:15", "23:25", "23:25", "23:45", "23:10",
                   "23:30", "00:10", "00:00", "00:10", "00:15", "00:35", "00:40", "00:45", "19:30", "20:00", "20:00", "20:15", "20:15", "20:15", "20:30", "21:30", "22:00", "22:30", "23:30", "23:35", "00:05"]
}

# Sample data for weekends
default_data_weekend = {
    "CarNo": [101, 103, 105, 107, 109, 111, 113, 115, 117, 119, 121, 123, 201, 203, 205, 207, 209, 211, 213, 215, 219, 221, 223, 225, 227, 229, 231, 233, 565, 515, 505, 575, 535, 555, 710, 740, "700/1", "700/2", 581],
    "Leave Time": ["20:15", "20:30", "20:30", "21:00", "20:30", "21:00", "21:00", "21:00", "22:00", "21:00", "22:00", "22:00", "22:20", "22:55", "23:00", "23:15", "23:25", "23:25", "23:45", "23:10",
                   "23:30", "00:10", "00:00", "00:10", "00:15", "00:35", "00:40", "00:45", "20:15", "20:30", "20:30", "21:00", "21:00", "21:00", "21:00", "21:45", "23:35", "00:05", "22:00"]
}

# Initialize reference_time
reference_time = datetime.now()
distribution_date = None

# Function to initialize the CSV files with default data if they don't exist
def initialize_csv():
    if not os.path.exists(data_file_weekday):
        df_weekday = pd.DataFrame(default_data_weekday)
        df_weekday.to_csv(data_file_weekday, index=False)
    if not os.path.exists(data_file_weekend):
        df_weekend = pd.DataFrame(default_data_weekend)
        df_weekend.to_csv(data_file_weekend, index=False)

# Initialize the CSV files if they don't exist
initialize_csv()

def save_data(df, file_name):
    df.to_csv(file_name, index=False)

def calculate_departure_time(df):
    today = reference_time.date()
    departure_times = []
    
    for lt in df["Leave Time"]:
        leave_time = datetime.strptime(lt, "%H:%M").time()
        if leave_time >= dt_time(0, 0) and leave_time < dt_time(12, 0):
            departure_time = datetime.combine(today + timedelta(days=1), leave_time)
        else:
            departure_time = datetime.combine(today, leave_time)
        
        # Adjust if the program is opened between 00:00 and 06:00
        if reference_time.time() >= dt_time(0, 0) and reference_time.time() < dt_time(6, 0):
            departure_time -= timedelta(days=1)
        
        departure_times.append(departure_time)
    
    df["Departure Time"] = departure_times
    save_data(df, get_data_file())  # Save the updated departure times to the appropriate CSV file

def format_time_left(td):
    total_seconds = int(td.total_seconds())
    if total_seconds <= 0:
        return "00:00"
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}"

def get_data_file():
    global distribution_date
    if datetime.strptime(distribution_date, '%Y-%m-%d').strftime('%A') == 'Sunday':
        return data_file_weekend
    else:
        return data_file_weekday

def update_time_left():
    global reference_time
    df = pd.read_csv(get_data_file())  # Reload the data from the correct CSV file
    calculate_departure_time(df)
    now = reference_time
    df["Time Left"] = df["Departure Time"] - now
    df["Time Left"] = df["Time Left"].apply(format_time_left)
    
    # Filter out rows where "Time Left" is "00:00" or less
    df_filtered = df[df["Time Left"] > "00:00"]
    
    df_sorted = df_filtered.sort_values(by="Departure Time")
    
    # Clear the table
    for item in table.get_children():
        table.delete(item)
    
    if df_sorted.empty:
        empty_message.grid(row=1, column=0, columnspan=3)
        table.grid_forget()
    else:
        # Get the top 3 rows to be bolded, red, and larger
        top_3 = df_sorted.head(3)

        # Reinsert sorted rows with correct tags
        for i, row in df_sorted.iterrows():
            tags = ('bold_red_large',) if row["CarNo"] in top_3["CarNo"].values else ()
            table.insert("", "end", values=(row["CarNo"], row["Leave Time"], row["Time Left"]), tags=tags)

        empty_message.grid_forget()
        table.grid(row=1, column=0, columnspan=3, sticky='nsew')

    update_cars_departed_label(df, df_sorted)
    root.after(60000, update_all)

def update_cars_departed_label(df, df_sorted):
    total_cars = len(df)
    departed_cars = total_cars - len(df_sorted)
    cars_departed_label.config(text=f"Cars Departed: {departed_cars}/{total_cars}")

def update_clock():
    global reference_time
    now_str = reference_time.strftime("%H:%M")
    current_date = reference_time.strftime("%Y-%m-%d")
    clock_label.config(text=now_str)
    current_date_label.config(text=current_date)

def update_all():
    global reference_time
    reference_time = datetime.now()
    update_clock()
    update_time_left()

def update_distribution_date():
    global reference_time, distribution_date
    now = reference_time
    if now.time() >= dt_time(13, 0, 0):
        distribution_date = (now + timedelta(days=1)).strftime('%Y-%m-%d')
    else:
        distribution_date = now.strftime('%Y-%m-%d')
    distribution_date_label.config(text=f"Distribution Date: {distribution_date}")

def check_and_update_distribution_date():
    global reference_time
    reference_time = datetime.now()
    if reference_time.time() >= dt_time(13, 0, 0):
        update_distribution_date()

def schedule_daily_update():
    global reference_time
    now = reference_time
    next_update = datetime.combine(now.date(), dt_time(13, 0, 0))
    if now.time() > dt_time(13, 0, 0):
        next_update += timedelta(days=1)
    
    delay = (next_update - now).total_seconds() * 1000
    root.after(int(delay), daily_update)

def daily_update():
    df = pd.read_csv(get_data_file())  # Reload the data from the correct CSV file
    calculate_departure_time(df)  # Recalculate departure times at 13:00
    update_all()
    update_distribution_date()  # Recalculate distribution date only once a day
    schedule_daily_update()

def reload_data():
    update_all()

# Create the root window
root = tk.Tk()
root.title("Car Departure Times")
root.configure(background='black')

# Allow the window to be resizable
root.resizable(True, True)

# Configure grid layout
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Create a style for the Treeview
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview",
                background="black",
                foreground="white",
                fieldbackground="black",
                font=("Helvetica", 72),  # Double the previous font size (36 * 2)
                rowheight=138)  # Double the previous row height (69 * 2)
style.configure("Treeview.Heading",
                background="black",
                foreground="white",
                font=("Helvetica", 40, 'bold'))  # Keep the heading font size as before

style.configure("Treeview.BoldRedLarge", font=("Helvetica", 92, 'bold'), foreground="red")  # Larger bold font and red color for top 3 rows

style.map('Treeview', background=[('selected', 'black')])

# Create a Treeview widget
columns = ("CarNo", "Departure Time", "Time Left")
table = ttk.Treeview(root, columns=columns, show='headings', style="Treeview")

for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor=tk.CENTER)

# Tag for bold, red, and larger rows
table.tag_configure('bold_red_large', font=("Helvetica", 110, 'bold'), foreground="red")  # Larger font size for top 3 rows

# Create a frame for the top labels
top_frame = tk.Frame(root, background="black")
top_frame.grid(row=0, column=0, columnspan=3, sticky='ew', pady=20)

# Distribution Date label
distribution_date_label = tk.Label(top_frame, font=("Helvetica", 40, 'bold'), background="black", foreground="white")
distribution_date_label.pack(side=tk.LEFT, padx=400)

# Spacer frame to push Cars Departed label to the right
spacer = tk.Frame(top_frame, background="black", width=100)
spacer.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Add a label to display cars departed at the top right
cars_departed_label = tk.Label(top_frame, font=("Helvetica", 30, 'bold'), background="black", foreground="white")
cars_departed_label.pack(side=tk.RIGHT, padx=20)

# Add a label to display the empty message
empty_message = tk.Label(root, text="Departure Times will be updated at 13:00", font=("Helvetica", 40, 'bold'), background="black", foreground="white")

# Place the table in the root window with proper packing options
table.grid(row=1, column=0, columnspan=3, sticky='nsew')

# Add a clock frame at the bottom
clock_frame = tk.Frame(root, background="black")
clock_frame.grid(row=2, column=0, columnspan=3, sticky='ew')

# Add a current date label to the clock frame
current_date_label = tk.Label(clock_frame, font=("Helvetica", 100, 'bold'), background="black", foreground="white")
current_date_label.pack(side=tk.LEFT, expand=True, padx=20)

# Add a clock label to the clock frame
clock_label = tk.Label(clock_frame, font=("Helvetica", 100, 'bold'), background="black", foreground="white")
clock_label.pack(side=tk.LEFT, expand=True)

# Add a Reload button to the clock frame
reload_button = tk.Button(clock_frame, text="Reload", command=reload_data, font=("Helvetica", 24), background="black", foreground="gray")
reload_button.pack(side=tk.RIGHT, padx=20)

# Initial update of the clock and time left
update_distribution_date()
update_all()

# Schedule daily update
schedule_daily_update()

# Start the GUI event loop
root.mainloop()