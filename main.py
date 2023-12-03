from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import folium
import matplotlib.pyplot as plt
from compare import compare_connections
from coordinates import COORDINATES_SG, COORDINATES_BIEL, COORDINATES_GENEVA


app = Flask(__name__)


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
        sbb, car, mix = compare_connections(origin, destination)
        route_sbb, duration_sbb = sbb[0], sbb[1]
        route_car, duration_car = car[0], car[1]
        route_mix1, route_mix2, duration_mix = mix[0], mix[1], mix[2]
        make_map_html(route_sbb, route_car, route_mix1, route_mix2)
        return render_template('result.html', data_input=data_input_combined, datadict={f"SBB only - {duration_sbb:.0f} min": {"a":5,"b":3,"c":"v"}, f"Car - {duration_car:.0f} min": {"a":5,"b":3,"c":"v"}, f"Combi - {duration_mix:.0f} min": {"a":5,"b":3,"c":"v"}})
    

def process_data(start, dest):
    # This is a placeholder function for processing the submitted data
    
    # calling the Nominatim tool and create Nominatim class
    loc = Nominatim(user_agent="Geopy Library")
    # entering the location name
    getLocStart = loc.geocode(str(start))
    getLocDest = loc.geocode(str(dest))
    
    # printing address
    print(getLocStart.address)
    print(getLocDest.address)
    coordinates = {
        'start_long': getLocStart.longitude,
        'start_lat': getLocStart.latitude,
        'dest_long': getLocDest.longitude,
        'dest_lat': getLocDest.latitude
    }
    
    return coordinates


def make_map_html(route_sbb, route_car, route_mix1, route_mix2):

    # Create a base map centered at specific coordinates
    map_center = [46.9480, 7.447]
    mymap = folium.Map(location=map_center, zoom_start=8)

    # Sample route coordinates
    merged_list = [(route_sbb[i, 1], route_sbb[i, 0]) for i in range(0, len(route_sbb))]
    merged_list2 = [(route_car[i, 1], route_car[i, 0]) for i in range(0, len(route_car))]
    merged_list3 = [(route_mix1[i, 1], route_mix1[i, 0]) for i in range(0, len(route_mix1))]
    merged_list4 = [(route_mix2[i, 1], route_mix2[i, 0]) for i in range(0, len(route_mix2))]

    # Add a PolyLine to represent the route
    folium.PolyLine(locations=merged_list, color='blue', weight=5, opacity=0.7).add_to(mymap)
    folium.PolyLine(locations=merged_list2, color='red', weight=5, opacity=0.7).add_to(mymap)
    folium.PolyLine(locations=merged_list3, color='green', weight=5, opacity=0.7).add_to(mymap)
    folium.PolyLine(locations=merged_list4, color='green', weight=5, opacity=0.7).add_to(mymap)

    # Save the map to an HTML file
    mymap.save("static/map_with_markers_and_route.html")


if __name__ == '__main__':
    app.run(debug=True)
    