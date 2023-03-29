import pandas as pd

# Function to convert a station ID to a station name.
def convert_station_id(id):
    # Data frame containing station ID and corresponding station name.
    stationID_to_stationName = pd.read_csv('sprottenflotte_map_stationID_to_stationName.csv').set_index('Station_ID')

    # Dictionary that maps the station ID to the corresponding station name.
    station_id_dict = stationID_to_stationName.to_dict()

    return station_id_dict['name'][id]
