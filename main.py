from flask import Flask, render_template, request, redirect, url_for
from geopy.geocoders import Nominatim
import folium
from dateutil import parser
from compare import compare_connections


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
    polyline1 = folium.PolyLine(locations=merged_list, color='blue', weight=5, opacity=0.7, label='SBB').add_to(mymap)
    polyline2 = folium.PolyLine(locations=merged_list2, color='red', weight=5, opacity=0.7, label='Car').add_to(mymap)
    polyline3 = folium.PolyLine(locations=merged_list3, color='green', weight=5, opacity=0.7, label='Combi').add_to(mymap)
    polyline4 = folium.PolyLine(locations=merged_list4, color='green', weight=5, opacity=0.7).add_to(mymap)
    
    # Add legend
    polyline1.add_to(mymap)
    polyline2.add_to(mymap)
    polyline3.add_to(mymap)
    polyline4.add_to(mymap)

    # Create a custom legend
    legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 120px; height: 130px; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    background-color: white;
                    ">
        &nbsp; <b>Legend</b> <br>
        &nbsp; SBB &nbsp; <i class="fa fa-map-marker fa-2x" style="color:blue"></i><br>
        &nbsp; Car &nbsp; <i class="fa fa-map-marker fa-2x" style="color:red"></i><br>
        &nbsp; Combi &nbsp; <i class="fa fa-map-marker fa-2x" style="color:green"></i>
        </div>
        '''

    mymap.get_root().html.add_child(folium.Element(legend_html))

    # Save the map to an HTML file
    mymap.save("static/map_with_markers_and_route.html")


@app.route('/')
def index():
    error = request.args.get('error', False)
    return render_template('index.html', error=error)


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
        try:
            sbb_data, car_data, combi_data = compare_connections(origin, destination, data_time)
        except Exception as e:
            print(e)
            return redirect(url_for('index', error=True))
        route_sbb = sbb_data['route']
        duration_sbb = sbb_data['duration']
        route_car = car_data[0]
        duration_car = car_data[1]
        route_combi_car = combi_data['route_car']
        route_combi_sbb = combi_data['route']
        duration_combi = combi_data['duration_total']
        changing_points_sbb = sbb_data['changing_points']
        changing_times_sbb = [format_time(el) for el in sbb_data['changing_times']]
        changing_points_combi = combi_data['changing_points']
        changing_times_combi = [format_time(el) for el in combi_data['changing_times']]

        if duration_car < duration_combi and duration_car < duration_sbb:
            meme_file = "meme1.jpg"
        if duration_combi < duration_car and duration_combi < duration_sbb:
            meme_file = "meme2.jpg"
        else:
            meme_file = "meme3.jpg"
        
        make_map_html(route_sbb, route_car, route_combi_car, route_combi_sbb)
        return render_template('result.html',
                                data_input=data_input_combined,
                                datadict={
                                    f"SBB - {duration_sbb:.0f} min": {key: value for key, value in zip(changing_points_sbb, changing_times_sbb)},
                                    f"Car - {duration_car:.0f} min": '-',
                                    f"Combi - {duration_combi:.0f} min": {key: value for key, value in zip(changing_points_combi, changing_times_combi)}
                                    },
                                meme_file=meme_file
                                )


if __name__ == '__main__':
    app.run(debug=True)
    