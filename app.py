from flask import Flask, render_template
from datetime import datetime
import csv
import io

app = Flask(__name__)

def load_bus_schedule_data():
#Load bus schedule data from CSV file
    with open('full_service_schedule.csv', 'r') as file:
        csv_data = file.read()

    reader = csv.DictReader(io.StringIO(csv_data))
    schedule = []

    for row in reader:
        # Clean up the data and convert to proper time objects
        cleaned_row = {}
        for key, value in row.items():
            if value.strip():  # Check if the value is not empty
                try:
                    # Convert time string to datetime object
                    time_obj = datetime.strptime(value, "%H:%M")
                    cleaned_row[key] = time_obj
                except ValueError:
                    # Keep original value if not a valid time
                    cleaned_row[key] = value
            else:
                cleaned_row[key] = None
        schedule.append(cleaned_row)

    return schedule

def get_next_bus(schedule, current_time, from_location, to_location):
    """Find the next bus from from_location to to_location after current_time."""
    next_buses = []
    
    for bus in schedule:
        # Check if this bus serves both the from and to locations
        if from_location in bus and to_location in bus and bus[from_location] is not None and bus[to_location] is not None:
            # Check if departure time is after current time
            if bus[from_location].time() > current_time.time():
                next_buses.append({
                    'depart': bus[from_location].strftime('%H:%M'),
                    'arrive': bus[to_location].strftime('%H:%M'),
                    'stops': get_intermediate_stops(bus, from_location, to_location)
                })
    
    return sorted(next_buses, key=lambda x: datetime.strptime(x['depart'], '%H:%M'))

def get_intermediate_stops(bus, from_location, to_location):
    """Get all intermediate stops between from_location and to_location."""
    all_stops = ["Departs Station", "Kids Uni", "Sciences", "Creative Arts", "Early Start", "Hope Theatre", "Northfields Ave", "Arrives Station"]
    
    start_idx = all_stops.index(from_location)
    end_idx = all_stops.index(to_location)
    
    # Determine direction
    if start_idx < end_idx:  # Station to Northfields direction
        stops = all_stops[start_idx+1:end_idx+1]
    else:  # Northfields to Station direction
        stops = all_stops[end_idx:start_idx]
        stops.reverse()  # Reverse to get correct order
    
    result = []
    for stop in stops:
        if bus[stop] is not None:
            result.append({
                'name': stop,
                'time': bus[stop].strftime('%H:%M')
            })
    
    return result

@app.route('/')
def index():
    # Get current time
    current_time = datetime.now()
    
    # Load bus schedule
    schedule = load_bus_schedule_data()
    
    # Get next buses from Northfields Ave to Station
    next_from_northfields = get_next_bus(
        schedule, 
        current_time, 
        "Northfields Ave", 
        "Arrives Station"
    )
    
    # Get next buses from Station to Northfields Ave
    next_from_station = get_next_bus(
        schedule, 
        current_time, 
        "Departs Station", 
        "Northfields Ave"
    )
    
    return render_template(
        'index.html', 
        current_time=current_time.strftime('%H:%M'),
        next_from_northfields=next_from_northfields[:5],  # Limit to 5 buses
        next_from_station=next_from_station[:5],  # Limit to 5 buses

    )


if __name__ == '__main__':
    app.run(debug=True)