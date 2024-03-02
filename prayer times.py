import requests
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta


def fetch_prayer_times(city, country):
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=5"

    try:
        response = requests.get(url)
        info = response.json()
        if "data" in info:
            timings = info["data"]["timings"]
            # Convert times to 12-hour format
            for name, time in timings.items():
                formatted_time = datetime.strptime(time, '%H:%M').strftime('%I:%M %p')
                timings[name] = formatted_time
            return timings
        else:
            return None
    except Exception as e:
        return f"Unexpected error occurred {e}"


def update_timer():
    global prayer_timings
    now = datetime.now().strftime('%I:%M %p')
    time_until_next_prayer, next_prayer = calculate_time_until_next_prayer(prayer_timings)

    if time_until_next_prayer is not None:
        time_label.config(text=f"Time until {next_prayer}: {str(time_until_next_prayer).split(',')[0]}")
        remaining_time_seconds = time_until_next_prayer.total_seconds()

        # Function to update the countdown every second
        def countdown():
            nonlocal remaining_time_seconds
            if remaining_time_seconds > 0:
                remaining_time = timedelta(seconds=remaining_time_seconds)
                time_label.config(text=f"Time until {next_prayer}: {str(remaining_time).split(',')[0]}")
                remaining_time_seconds -= 1
                app.after(1000, countdown)  # Use app.after for scheduling the update
            else:
                update_timer()  # Move to the next prayer time

        countdown()  # Start the countdown
    else:
        time_label.config(text="No prayer remaining for the day")


def calculate_time_until_next_prayer(prayer_timings):
    now = datetime.now().strftime('%I:%M %p')
    prayers = list(prayer_timings.values())
    prayer_times = [datetime.strptime(time, '%I:%M %p') for time in prayers]
    next_prayer_index = next((i for i, time in enumerate(prayer_times) if time > datetime.strptime(now, '%I:%M %p')),
                             None)

    if next_prayer_index is not None:
        time_until_next_prayer = prayer_times[next_prayer_index] - datetime.strptime(now, '%I:%M %p')

        # Adjusting the prayer times list to start from the next prayer
        prayers = prayers[next_prayer_index:] + prayers[:next_prayer_index]
        prayer_timings = dict(
            zip(list(prayer_timings.keys())[next_prayer_index:] + list(prayer_timings.keys())[:next_prayer_index],
                prayers))

        return time_until_next_prayer, list(prayer_timings.keys())[0]
    else:
        return None, None


def gui_fetch_prayer_times():
    global prayer_timings
    city = city_entry.get()
    country = country_entry.get()
    if city and country:
        prayer_timings = fetch_prayer_times(city, country)
        if prayer_timings:
            result.delete(0, tk.END)  # Clear previous results

            # Sort prayer times in ascending order
            sorted_prayers = sorted(prayer_timings.items(), key=lambda x: datetime.strptime(x[1], '%I:%M %p'))

            for name, time in sorted_prayers:
                result.insert(tk.END, f"{name}: {time}")

            prayer_timings = dict(sorted_prayers)  # Update prayer timings to sorted order
            update_timer()
        else:
            messagebox.showerror("Error", "Unable to fetch prayer times. Please enter correct city and country names")
    else:
        messagebox.showerror("Error", "Please enter city and country names")


app = tk.Tk()
app.title("Prayer Times")
frame = ttk.Frame(app, padding="20")
frame.grid(row=0, column=0)

city_label = ttk.Label(frame, text="City : ")
city_label.grid(row=0, column=0, pady=5)
city_entry = ttk.Entry(frame, width=30)
city_entry.grid(row=0, column=1, pady=5)

country_label = ttk.Label(frame, text="Country : ")
country_label.grid(row=1, column=0, pady=5)
country_entry = ttk.Entry(frame, width=30)
country_entry.grid(row=1, column=1, pady=5)

fetch_button = ttk.Button(frame, text="Get Prayer Times", command=gui_fetch_prayer_times)
fetch_button.grid(row=2, column=0, columnspan=2, pady=10)

result = tk.Listbox(frame, height=11, width=40)
result.grid(row=3, column=0, columnspan=2, pady=5)

time_label = ttk.Label(frame, text="")
time_label.grid(row=4, column=0, columnspan=2, pady=5)

prayer_timings = {}  # Holds the fetched prayer timings

app.mainloop()