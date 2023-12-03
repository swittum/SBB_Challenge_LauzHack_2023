from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import folium
from compare import compare_connections
from dateutil import parser


def format_time(timestamp):
    parsed_timestamp = parser.parse(timestamp)
    hours = parsed_timestamp.hour
    minutes = parsed_timestamp.minute
    formatted_time = f"{hours:02}:{minutes:02}"
    return formatted_time


app = Flask(__name__)


def process_data(start, dest):
    loc = Nominatim(user_agent="Geopy Library")
    getLocStart = loc.geocode(str(start))
    getLocDest = loc.geocode(str(dest))
    
    coordinates = {
        'start_long': getLocStart.longitude,
        'start_lat': getLocStart.latitude,
        'dest_long': getLocDest.longitude,
        'dest_lat': getLocDest.latitude
    }
    return coordinates


def make_map_html(route_sbb, route_car, route_combi1, route_combi2):
    # Create a base map centered at specific coordinates
    map_center = [46.9480, 7.447]
    mymap = folium.Map(location=map_center, zoom_start=8)

    # Sample route coordinates
    merged_list = [(route_sbb[i, 1], route_sbb[i, 0]) for i in range(0, len(route_sbb))]
    merged_list2 = [(route_car[i, 1], route_car[i, 0]) for i in range(0, len(route_car))]
    merged_list3 = [(route_combi1[i, 1], route_combi1[i, 0]) for i in range(0, len(route_combi1))]
    merged_list4 = [(route_combi2[i, 1], route_combi2[i, 0]) for i in range(0, len(route_combi2))]

    # Add a PolyLine to represent the route
    folium.PolyLine(locations=merged_list, color='blue', weight=5, opacity=0.7).add_to(mymap)
    folium.PolyLine(locations=merged_list2, color='red', weight=5, opacity=0.7).add_to(mymap)
    folium.PolyLine(locations=merged_list3, color='green', weight=5, opacity=0.7).add_to(mymap)
    folium.PolyLine(locations=merged_list4, color='green', weight=5, opacity=0.7).add_to(mymap)

    # Save the map to an HTML file
    mymap.save("static/map_with_markers_and_route.html")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        data_start = request.form['start']
        data_dest = request.form['dest']
        data_time = request.form['time']

        # Process or store the data as needed
        processed_data = process_data(data_start, data_dest)
        data_input_combined = str(data_start) + " - " + str(data_dest)
        origin = [processed_data['start_long'], processed_data['start_lat']]
        destination = [processed_data['dest_long'], processed_data['dest_lat']]
        sbb_data, car_data, combi_data = compare_connections(origin, destination, data_time)
        route_sbb = sbb_data['route']
        duration_sbb = sbb_data['duration']
        route_car = car_data[0]
        duration_car = car_data[1]
        route_combi_car = combi_data['route_car']
        route_combi_sbb = combi_data['route']
        duration_combi = combi_data['duration_total']
        duration_combi = combi_data['duration_total']
        changing_points_sbb = sbb_data['changing_points']
        changing_times_sbb = [format_time(el) for el in sbb_data['changing_times']]
        changing_points_combi = combi_data['changing_points']
        changing_times_combi = [format_time(el) for el in combi_data['changing_times']]
        print(changing_points_combi)

        make_map_html(route_sbb, route_car, route_combi_car, route_combi_sbb)
        return render_template('result.html',
                                data_input=data_input_combined,
                                datadict={
                                    f"SBB - {duration_sbb:.0f} min": {key: value for key, value in zip(changing_points_sbb, changing_times_sbb)},
                                    f"Car - {duration_car:.0f} min": '-',
                                    f"Combi - {duration_combi:.0f} min": {key: value for key, value in zip(changing_points_combi, changing_times_combi)}
                                    }
                                )


if __name__ == '__main__':
    app.run(debug=True)
    