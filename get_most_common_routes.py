import pandas as pd 
from get_information_sprottenflotte import get_station_of_kiel


def rented_timestamp(number_of_bikes: list, timestamp: list):
    '''Return a dict with the timestamp as key and value as how many bikes were rented at that time.'''

    index = 0
    renting = []
    while index < len(number_of_bikes) - 1:
        if number_of_bikes[index] > number_of_bikes[index + 1]:
            renting.append((timestamp[index + 1], number_of_bikes[index] - number_of_bikes[index + 1]))
        index += 1
    return renting


def return_timestamp(number_of_bikes: list, timestamp: list):
    '''Return a dict with the timestamp as key and value of how many bikes were returned.'''

    index = 0
    returning = []
    while index < len(number_of_bikes) - 1:
        if number_of_bikes[index] < number_of_bikes[index + 1]:
            returning.append((timestamp[index + 1] - 100, timestamp[index + 1],timestamp[index + 1] + 100 , number_of_bikes[index + 1] - number_of_bikes[index]))
        index += 1
    return returning

def map_timestamps_list_to_dict(timestamp_list: list):
    return {k: v for v, k in enumerate(timestamp_list)}

def binary_search(time, returning, left, right):
    '''Binary search to search for the station where a bike was returned to a certain time.'''

    mid = (right + left) // 2
    if right < left:
        return -1
    elif (time == returning[mid][1]) or (time >= returning[mid][0] and time <= returning[mid][2]):
        return mid
    elif time < returning[mid][1]:
        return binary_search(time, returning, left, mid - 1)
    elif time > returning[mid][1]:
        return binary_search(time, returning, mid + 1, right)
    
def function(dict_with_info: dict, station: int, key_time: float) -> dict:
    '''Function to get the weight of a route.'''

    time_count_dict = {}
    five_minute = 300
    list_of_timestamps = [key_time + five_minute, key_time + 2 * five_minute, key_time + 3 * five_minute, key_time + 4 * five_minute,
                        key_time + 5 * five_minute, key_time + 6 * five_minute]
    for station_id in dict_with_info:
        time_count_list = []
        if station_id != station:
            _,returning = dict_with_info[station_id]
            for time in list_of_timestamps:
                index = binary_search(time, returning, 0, len(returning) - 1)
                if index != -1:
                    time_count_list.append((returning[index][1], returning[index][3]))
            time_count_dict[station_id] = time_count_list
    return time_count_dict
    

def get_routes(sprottenflotte_routing_df) -> dict:
    '''Get the routes in a dictanory.'''

    station_id_list = sprottenflotte_routing_df["Station_ID"].unique()
    timestamps = sprottenflotte_routing_df.loc[sprottenflotte_routing_df["Station_ID"] == 24397]["last_update"].to_list()
    dict_with_info = {}
    # for every station get the number of bikes. With that use function rented_timestamp and returning_timestamp to
    # get two dict to get the timestamps were a bike was returned and rented.
    # Save in dict where key is station and value is a tuple with renting, returning info.
    for station in station_id_list:
        result_df = sprottenflotte_routing_df.loc[sprottenflotte_routing_df["Station_ID"] == station]
        number_of_bikes = result_df["Number_of_Bikes"].to_list()
        renting = rented_timestamp(number_of_bikes, timestamps)
        returning = returning = return_timestamp(number_of_bikes, timestamps)
        dict_with_info[station] = (renting, returning)

    routing_dict = {}
    for station in dict_with_info:
        renting,_ = dict_with_info[station]
        # for every time there was a renting, check the other station if a bike was returned in a time period of 30min
        time_dict_list = []
        for key_time in renting:
            anzahl_rented = key_time[1]
            dict = function(dict_with_info, station, key_time[0])
            time_dict_list.append((key_time[0], anzahl_rented, dict))
        routing_dict[station] = time_dict_list
    return routing_dict

def get_most_common_routes_from_routes(routes: dict):
    '''Get the most common routes from the routing dictonary from the function get_routes.'''

    # read csv file to get info of station
    df_station_info = pd.read_csv("./general_data/sprottenflotte_station_information.csv")
    df_station_info = df_station_info[["Station_ID", "name", "lat", "lon"]]

    # create routing table of routes taken from a dictanory that was created by get_routes function
    routing = []
    for station in routes:
        #print(station)
        endpoints_station = routes[station]
        #print(endpoints_station)
        for time in endpoints_station:
            dict_endpoints = time[2]
            #print(dict_endpoints)   
            for key in dict_endpoints:
                #print(key)
                if dict_endpoints[key] != []:
                    # append liste mit station startpunkt, station endpunkt, startpunkt lat, lon und endpunkt lat, lon, name der 
                    # station startpunkt, name der station endpunkt
                    start_info_df = df_station_info.loc[df_station_info["Station_ID"] == station]
                    #print(start_info_df)
                    end_info_df = df_station_info.loc[df_station_info["Station_ID"] == key]
                    start_name = start_info_df.iloc[0]["name"]
                    start_lat = start_info_df.iloc[0]["lat"]
                    start_lon = start_info_df.iloc[0]["lon"]
                    end_name = end_info_df.iloc[0]["name"]
                    end_lat = end_info_df.iloc[0]["lat"]
                    end_lon = end_info_df.iloc[0]["lon"]
                    #print(station, key, start_name, start_lat, start_lon, end_name, end_lat, end_lon)
                    routing.append([station, key, start_name, start_lat, start_lon, end_name, end_lat, end_lon])
        
        routing_table_df = pd.DataFrame(routing, columns=["start_station", "end_station", "start_name", "start_lat", "start_lon", 
                                                        "end_name", "end_lat", "end_lon"])
        
    # now get the most common routes from the routing table by looking how often a route was taken
    most_common_routes = []
    start_station_list = routing_table_df["start_station"].unique()
    for station in start_station_list:
        start_station_df = routing_table_df.loc[routing_table_df["start_station"] == station]
        for end_station in start_station_list:
            end_station_df = start_station_df.loc[start_station_df["end_station"] == end_station]
            if not (end_station_df.empty):
                weight = end_station_df["end_name"].to_list()
                weight = len(weight)
                start_name = end_station_df.iloc[0]["start_name"]
                start_lat = end_station_df.iloc[0]["start_lat"]
                start_lon = end_station_df.iloc[0]["start_lon"]
                end_name = end_station_df.iloc[0]["end_name"]
                end_lat = end_station_df.iloc[0]["end_lat"]
                end_lon = end_station_df.iloc[0]["end_lon"]
                most_common_routes.append([station, end_station, weight, start_name, start_lat, start_lon, end_name, end_lat, end_lon])

    most_common_routes_df = pd.DataFrame(most_common_routes, columns=["start_station", "end_station", "weight", "start_name", "start_lat", "start_lon", 
                                                        "end_name", "end_lat", "end_lon"])
    
    most_common_routes_df.to_csv("./general_data/most_common_routes.csv")

    return most_common_routes_df

def add_route(most_common_routes_df, station_id: int):
    '''Used to add a route to the Plotly plot for visualization of the most common routes. '''

    attributes_for_lines_df = most_common_routes_df.loc[most_common_routes_df["start_station"] == station_id]

    start_lat_list = attributes_for_lines_df["start_lat"].to_list()
    end_lat_list = attributes_for_lines_df["end_lat"].to_list()
    start_lon_list = attributes_for_lines_df["start_lon"].to_list()
    end_lon_list = attributes_for_lines_df["end_lon"].to_list()
    weight = attributes_for_lines_df["weight"].to_list()
    station_name = attributes_for_lines_df["start_name"].to_list()
    return start_lat_list, end_lat_list, start_lon_list, end_lon_list, weight, station_name


def get_only_the_most_taken_route(most_common_routes_df, station_id: int):
    '''Get only the two most taken routes from a station from the dataframe with the routes.'''

    most_common_routes_df = most_common_routes_df.loc[most_common_routes_df["start_station"] == station_id]
    most_common_routes_df = most_common_routes_df.sort_values(by=["weight"], ascending=False)
    first_row_df = most_common_routes_df.head(2)
    
    start_lat_list = first_row_df["start_lat"].to_list()
    end_lat_list = first_row_df["end_lat"].to_list()
    start_lon_list = first_row_df["start_lon"].to_list()
    end_lon_list = first_row_df["end_lon"].to_list()
    weight = first_row_df["weight"].to_list()
    station_name = first_row_df["start_name"].to_list()
    return start_lat_list, end_lat_list, start_lon_list, end_lon_list, station_name


        

if __name__ == '__main__':
    clusters_df = pd.read_csv(r"./general_data/sf_attributes_clustered_kiel_per_day.csv")
    clusters_df = clusters_df.drop(columns=["Unnamed: 0", "Frequency_of_Usage", "Avg_Number_of_Bikes", "Avg_Usage_of_Station",
                                            "Avg_Returning_Bike_of_Station", "Avg_Renting_Bike_of_Station", "name"])

    sprottenflotte_data_df = pd.read_csv(r"./data/sprottenflotte_data.csv")
    sprottenflotte_data_df = sprottenflotte_data_df.drop(columns=["is_installed", "is_renting", "is_returning"])
    sprottenflotte_data_clusters_df = pd.merge(sprottenflotte_data_df, clusters_df, on="Station_ID")

    # # get only the stations in Kiel
    sprottenflotte_data_clusters_kiel_df = get_station_of_kiel(sprottenflotte_data_clusters_df)
    sprottenflotte_data_clusters_kiel_df = sprottenflotte_data_clusters_kiel_df.drop(columns=["lat", "lon"])
    sprottenflotte_data_clusters_kiel_df

    sprottenflotte_cluster_2_1_kiel_df = sprottenflotte_data_clusters_kiel_df.loc[(sprottenflotte_data_clusters_kiel_df["Cluster"] == 2) |
                                                                                    (sprottenflotte_data_clusters_kiel_df["Cluster"] == 1) ]
    sprottenflotte_routing_df = sprottenflotte_cluster_2_1_kiel_df[["Station_ID", "Number_of_Bikes", "last_update"]]

    routes = get_routes(sprottenflotte_routing_df)
    print(routes)


        