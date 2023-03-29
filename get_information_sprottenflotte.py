import pandas as pd


# Some functions to extract some data from Sprottenflotte. It will most often return a dictonary with the 
# station_ids as the key.



def get_total_number_of_bikes(sprottenflotte_df):
    '''Get the total number of bikes available for Sprottenflotte.'''

    last_update_list = sprottenflotte_df["last_update"].to_list()
    dict_timestamp = {}
    max_number_of_bikes = []
    for timestamp in last_update_list:
        if timestamp not in dict_timestamp:
            dict_timestamp[timestamp] = True
            result_df = sprottenflotte_df.loc[sprottenflotte_df['last_update'] == timestamp]
            # print(result_df["Number_of_Bikes"].sum())
            max_number_of_bikes.append(result_df["Number_of_Bikes"].sum())
            # print(max_number_of_bikes)
    return max(max_number_of_bikes)


def frequency_of_station_rentals_total(sprottenflotte_df):
    '''Returns the frequency of usage of a station over the total amount of time as a dictonary.'''

    last_update_list = sprottenflotte_df["last_update"].unique()
    station_id_list = sprottenflotte_df["Station_ID"].unique()
    length_of_time = len(last_update_list)
    frequencies_stations = {}
    for station in station_id_list:
        station_id_df = sprottenflotte_df.loc[sprottenflotte_df["Station_ID"] == station]
        last_reported_list = station_id_df["last_reported"].unique()
        frequencies_stations[station] = len(last_reported_list) / length_of_time
    return frequencies_stations


def avg_number_of_bike_per_day(sprottenflotte_df):
    '''Returns the average number of bikes available at the stationper day as dictonary.'''
    
    avg_number_of_bikes = {}
    first_update = sprottenflotte_df["last_update"].values[0]
    one_day = first_update + 86400
    station_id_list = sprottenflotte_df["Station_ID"].unique()
    last_update = sprottenflotte_df["last_update"].values[-1]
        
    for station in station_id_list:
        number_bikes_per_day = []
        if station == 26355:
            one_day_copy = 1678212530 + 21070 + 86400
            first_update_copy = 1678212530
        else:
            one_day_copy = one_day
            first_update_copy = first_update
        while one_day_copy < last_update:
            result_df = sprottenflotte_df.loc[ (sprottenflotte_df["Station_ID"] == station) & 
                                                (sprottenflotte_df["last_update"] >= first_update_copy) & 
                                                (sprottenflotte_df["last_update"] < one_day_copy) ]
            entry = result_df["Number_of_Bikes"].to_list()
            number_bikes_per_day.append(sum(entry) / len(entry))
            first_update_copy = one_day_copy
            one_day_copy += 86400
        avg_number_of_bikes[station] = sum(number_bikes_per_day) / len(number_bikes_per_day)
    
    return avg_number_of_bikes


def avg_usage_of_station_per_day(sprottenflotte_df):
    '''Returns the average usage of a station per day as a dictanory.'''

    avg_usage_of_station = {}
    first_update = sprottenflotte_df["last_update"].values[0]
    one_day = first_update + 86400
    station_id_list = sprottenflotte_df["Station_ID"].unique()
    last_update = sprottenflotte_df["last_update"].values[-1]

    for station in station_id_list:
        usage_of_station_per_day = []
        if station == 26355:
            one_day_copy = 1678212530 + 21070 + 86400
            first_update_copy = 1678212530  
        else:
            one_day_copy = one_day
            first_update_copy = first_update
        while one_day_copy < last_update:
            result_df = sprottenflotte_df.loc[ (sprottenflotte_df["Station_ID"] == station) & 
                                                (sprottenflotte_df["last_update"] >= first_update_copy) & 
                                                (sprottenflotte_df["last_update"] < one_day_copy) ]
            reported = result_df["last_reported"].unique()
            usage_of_station_per_day.append(len(reported))
            first_update_copy = one_day_copy
            one_day_copy += 86400
        avg_usage_of_station[station] = sum(usage_of_station_per_day) / len(usage_of_station_per_day)
    
    return avg_usage_of_station


def get_returning(number_of_bikes: list):
    '''
    Given a list of values, it returns a number, which is calculated by comparing two values next to each other.
    
    The number is the returned number of bikes to that station.
    '''

    index = 0
    returned = 0
    while index < len(number_of_bikes) - 1:
        if number_of_bikes[index] < number_of_bikes[index + 1]:
            returned += number_of_bikes[index + 1] - number_of_bikes[index]
        index += 1
    return returned

# same as get_returning, just the other way around
def get_renting(number_of_bikes: list):
    '''
    Given a list of values, it returns a number, which is calculated by comparing two values next to each other.
    
    The number is the retented number of bikes to that station.
    '''

    index = 0
    renting = 0
    while index < len(number_of_bikes) - 1:
        if number_of_bikes[index] > number_of_bikes[index + 1]:
            renting += number_of_bikes[index] - number_of_bikes[index + 1]
        index += 1
    return renting


def avg_returning_bike_of_station_per_day(sprottenflotte_df):
    '''Returns the average of the returning bikes to a station per day as a dictonary.'''

    avg_returning_bike_of_station = {}
    first_update = sprottenflotte_df["last_update"].values[0]
    one_day = first_update + 86400
    station_id_list = sprottenflotte_df["Station_ID"].unique()
    last_update = sprottenflotte_df["last_update"].values[-1]

    for station in station_id_list:
        number_of_bikes_returning= []
        if station == 26355:
            one_day_copy = 1678212530 + 21070 + 86400
            first_update_copy = 1678212530
        else:
            one_day_copy = one_day
            first_update_copy = first_update
        while one_day_copy < last_update:
            result_df = sprottenflotte_df.loc[ (sprottenflotte_df["Station_ID"] == station) & 
                                                (sprottenflotte_df["last_update"] >= first_update_copy) & 
                                                (sprottenflotte_df["last_update"] < one_day_copy) ]
            number_of_bikes = result_df["Number_of_Bikes"].to_list()
            number_of_bikes_returning.append(get_returning(number_of_bikes))
            first_update_copy = one_day_copy
            one_day_copy += 86400
        avg_returning_bike_of_station[station] = sum(number_of_bikes_returning) / len(number_of_bikes_returning)

    return avg_returning_bike_of_station


def avg_renting_bike_of_station_per_day(sprottenflotte_df):
    '''Return the average of how often a bike is rented from a station per day as a dictonary.'''

    avg_renting_bike_of_station = {}
    first_update = sprottenflotte_df["last_update"].values[0]
    one_day = first_update + 86400
    station_id_list = sprottenflotte_df["Station_ID"].unique()
    last_update = sprottenflotte_df["last_update"].values[-1]

    for station in station_id_list:
        number_of_bikes_renting= []
        if station == 26355:
            one_day_copy = 1678212530 + 21070 + 86400
            first_update_copy = 1678212530
        else:
            one_day_copy = one_day
            first_update_copy = first_update
        while one_day_copy < last_update:
            result_df = sprottenflotte_df.loc[ (sprottenflotte_df["Station_ID"] == station) & 
                                                (sprottenflotte_df["last_update"] >= first_update_copy) & 
                                                (sprottenflotte_df["last_update"] < one_day_copy) ]
            number_of_bikes = result_df["Number_of_Bikes"].to_list()
            number_of_bikes_renting.append(get_renting(number_of_bikes))
            first_update_copy = one_day_copy
            one_day_copy += 86400   
        avg_renting_bike_of_station[station] = sum(number_of_bikes_renting) / len(number_of_bikes_renting)

    return avg_renting_bike_of_station



def avg_number_of_bike_per_half_hour(sprottenflotte_df):
    '''Returns the average numer of bike available at a station per half an hour as dictonary.'''

    avg_number_of_bikes = {}
    first_update = sprottenflotte_df["last_update"].values[0]
    half_hour = first_update + 1800
    station_id_list = sprottenflotte_df["Station_ID"].unique()
    last_update = sprottenflotte_df["last_update"].values[-1]
        
    for station in station_id_list:
        number_bikes_per_half_hour = []
        if station == 26355:
            half_hour_copy = 1678212530 + 1800
            first_update_copy = 1678212530
        else:
            half_hour_copy = half_hour
            first_update_copy = first_update
        while half_hour_copy < last_update:
            if station == 26355:
                    if not (first_update_copy < 1678374768 and first_update_copy > 1678212837):
                        result_df = sprottenflotte_df.loc[ (sprottenflotte_df["Station_ID"] == station) & 
                                                    (sprottenflotte_df["last_update"] >= first_update_copy) & 
                                                    (sprottenflotte_df["last_update"] < half_hour_copy) ]
                        entry = result_df["Number_of_Bikes"].to_list()
                        number_bikes_per_half_hour.append(sum(entry) / len(entry))
            
            elif not ((first_update_copy < 1678180903 and first_update_copy > 1678168785) or (first_update_copy > 1678249874 and first_update_copy < 1678264138)):                                                                                                                           
                result_df = sprottenflotte_df.loc[ (sprottenflotte_df["Station_ID"] == station) & 
                                                    (sprottenflotte_df["last_update"] >= first_update_copy) & 
                                                    (sprottenflotte_df["last_update"] < half_hour_copy) ]
                entry = result_df["Number_of_Bikes"].to_list()
                number_bikes_per_half_hour.append(sum(entry) / len(entry))
            first_update_copy = half_hour_copy
            half_hour_copy += 1800
        avg_number_of_bikes[station] = sum(number_bikes_per_half_hour) / len(number_bikes_per_half_hour)
    
    return avg_number_of_bikes


def avg_usage_of_station_per_half_hour(sprottenflotte_df):
    '''Returns the average usage of a station per half hour as a dictonary.'''

    avg_usage_of_station = {}
    first_update = sprottenflotte_df["last_update"].values[0]
    half_hour = first_update + 1800
    station_id_list = sprottenflotte_df["Station_ID"].unique()
    last_update = sprottenflotte_df["last_update"].values[-1]

    for station in station_id_list:
        usage_of_station_per_half_hour = []
        if station == 26355:
            half_hour_copy = 1678212530 + 1800
            first_update_copy = 1678212530
        else:
            half_hour_copy = half_hour
            first_update_copy = first_update

        while half_hour_copy < last_update:
            if station == 26355:
                if not (first_update_copy < 1678374768 and first_update_copy > 1678212837):
                    result_df = sprottenflotte_df.loc[ (sprottenflotte_df["Station_ID"] == station) & 
                                                    (sprottenflotte_df["last_update"] >= first_update_copy) & 
                                                    (sprottenflotte_df["last_update"] < half_hour_copy) ]
                reported = result_df["last_reported"].unique()
                usage_of_station_per_half_hour.append(len(reported))
            elif not ((first_update_copy < 1678180903 and first_update_copy > 1678168785) or (first_update_copy > 1678249874 and first_update_copy < 1678264138)):
                result_df = sprottenflotte_df.loc[ (sprottenflotte_df["Station_ID"] == station) & 
                                                    (sprottenflotte_df["last_update"] >= first_update_copy) & 
                                                    (sprottenflotte_df["last_update"] < half_hour_copy) ]
                reported = result_df["last_reported"].unique()
                usage_of_station_per_half_hour.append(len(reported))
            first_update_copy = half_hour_copy
            half_hour_copy += 1800
        avg_usage_of_station[station] = sum(usage_of_station_per_half_hour) / len(usage_of_station_per_half_hour)
    
    return avg_usage_of_station


def avg_returning_bike_of_station_per_half_hour(sprottenflotte_df):
    '''Returns the average of how often a bike is returned to a station per half hour as a dictonary.'''

    avg_returning_bike_of_station = {}
    first_update = sprottenflotte_df["last_update"].values[0]
    half_hour = first_update + 1800
    station_id_list = sprottenflotte_df["Station_ID"].unique()
    last_update = sprottenflotte_df["last_update"].values[-1]

    for station in station_id_list:
        number_of_bikes_returning = []
        if station == 26355:
            half_hour_copy = 1678212530 + 1800
            first_update_copy = 1678212530
        else:
            half_hour_copy = half_hour
            first_update_copy = first_update
        while half_hour_copy < last_update:
            if station == 26355:
                if not (first_update_copy < 1678374768 and first_update_copy > 1678212837):
                    result_df = sprottenflotte_df.loc[ (sprottenflotte_df["Station_ID"] == station) & 
                                                    (sprottenflotte_df["last_update"] >= first_update_copy) & 
                                                    (sprottenflotte_df["last_update"] < half_hour_copy) ]
                number_of_bikes = result_df["Number_of_Bikes"].to_list()
                number_of_bikes_returning.append(get_returning(number_of_bikes))
            
            elif not ((first_update_copy < 1678180903 and first_update_copy > 1678168785) or (first_update_copy > 1678249874 and first_update_copy < 1678264138)):
                result_df = sprottenflotte_df.loc[ (sprottenflotte_df["Station_ID"] == station) & 
                                                    (sprottenflotte_df["last_update"] >= first_update_copy) & 
                                                    (sprottenflotte_df["last_update"] < half_hour_copy) ]
                number_of_bikes = result_df["Number_of_Bikes"].to_list()
                number_of_bikes_returning.append(get_returning(number_of_bikes))
            first_update_copy = half_hour_copy
            half_hour_copy += 1800
        avg_returning_bike_of_station[station] = sum(number_of_bikes_returning) / len(number_of_bikes_returning)

    return avg_returning_bike_of_station


def avg_renting_bike_of_station_per_half_hour(sprottenflotte_df):
    '''Returns the average of how often a bike is renting at a station per half hour as a dictonary.'''

    avg_renting_bike_of_station = {}
    first_update = sprottenflotte_df["last_update"].values[0]
    half_hour = first_update + 1800
    station_id_list = sprottenflotte_df["Station_ID"].unique()
    last_update = sprottenflotte_df["last_update"].values[-1]

    for station in station_id_list:
        number_of_bikes_renting = []
        if station == 26355:
            half_hour_copy = 1678212530 + 1800
            first_update_copy = 1678212530
        else:
            half_hour_copy = half_hour
            first_update_copy = first_update
        while half_hour_copy < last_update:
            if station == 26355:
                if not (first_update_copy < 1678374768 and first_update_copy > 1678212837):
                    result_df = sprottenflotte_df.loc[ (sprottenflotte_df["Station_ID"] == station) & 
                                                    (sprottenflotte_df["last_update"] >= first_update_copy) & 
                                                    (sprottenflotte_df["last_update"] < half_hour_copy) ]
                number_of_bikes = result_df["Number_of_Bikes"].to_list()
                number_of_bikes_renting.append(get_renting(number_of_bikes))

            if not ((first_update_copy < 1678180903 and first_update_copy > 1678168785) or (first_update_copy > 1678249874 and first_update_copy < 1678264138)):
                result_df = sprottenflotte_df.loc[ (sprottenflotte_df["Station_ID"] == station) & 
                                                    (sprottenflotte_df["last_update"] >= first_update_copy) & 
                                                    (sprottenflotte_df["last_update"] < half_hour_copy) ]
                number_of_bikes = result_df["Number_of_Bikes"].to_list()
                number_of_bikes_renting.append(get_renting(number_of_bikes))
            first_update_copy = half_hour_copy
            half_hour_copy += 1800
        avg_renting_bike_of_station[station] = sum(number_of_bikes_renting) / len(number_of_bikes_renting)

    return avg_renting_bike_of_station


def get_station_of_kiel(sprottenflotte_with_lat_lon_df):
    '''Get only the station in Kiel, not the station in Eckernförde etc.'''

    result = sprottenflotte_with_lat_lon_df.loc[ (sprottenflotte_with_lat_lon_df["lon"] > 10.0) &
                                                ((sprottenflotte_with_lat_lon_df["lon"] < 10.26))
                                                ]
    return result



if __name__ == '__main__':
    sprottenflotte_df = pd.read_csv(r"./data/sprottenflotte_data.csv")
    sprottenflotte_names_df = pd.read_csv(r"./general_data/sprottenflotte_map_stationID_to_stationName.csv")

    number_of_bikes_total = get_total_number_of_bikes(sprottenflotte_df)

    total_frequency_of_station_rentals = frequency_of_station_rentals_total(sprottenflotte_df)

    avg_number_of_bike_day = avg_number_of_bike_per_day(sprottenflotte_df)

    avg_usage_of_station_day = avg_usage_of_station_per_day(sprottenflotte_df)

    avg_returning_bike_of_station_day = avg_returning_bike_of_station_per_day(sprottenflotte_df)

    avg_renting_bike_of_station_day = avg_renting_bike_of_station_per_day(sprottenflotte_df)

    station_id = sprottenflotte_df["Station_ID"].unique()

    # prepare total frequencies for dataframe
    total_frequency_of_station_rentals_list = []
    for key in total_frequency_of_station_rentals:
        total_frequency_of_station_rentals_list.append(total_frequency_of_station_rentals[key])

    # prepare  average number of bikes per day for dataframe
    avg_number_of_bike_day_list = []
    for key in avg_number_of_bike_day:
        avg_number_of_bike_day_list.append(avg_number_of_bike_day[key])

    # prepare average usage of station per day for dataframe
    avg_usage_of_station_day_list = []
    for key in avg_usage_of_station_day:
        avg_usage_of_station_day_list.append(avg_usage_of_station_day[key])

    avg_returning_bike_of_station_day_list = []
    for key in avg_returning_bike_of_station_day:
        avg_returning_bike_of_station_day_list.append(avg_returning_bike_of_station_day[key])

    avg_renting_bike_of_station_day_list = []
    for key in avg_renting_bike_of_station_day:
        avg_renting_bike_of_station_day_list.append(avg_renting_bike_of_station_day[key])

    sprottenflotte_attributes_df = pd.DataFrame(station_id ,columns=["Station_ID"])

    # append all the attribute with values to the dataframes
    sprottenflotte_attributes_df["Frequency_of_Usage"] = total_frequency_of_station_rentals_list
    sprottenflotte_attributes_df["Avg_Number_of_Bikes"] = avg_number_of_bike_day_list
    sprottenflotte_attributes_df["Avg_Usage_of_Station"] = avg_usage_of_station_day_list
    sprottenflotte_attributes_df["Avg_Returning_Bike_of_Station"] = avg_returning_bike_of_station_day_list
    sprottenflotte_attributes_df["Avg_Renting_Bike_of_Station"] = avg_renting_bike_of_station_day_list
    sprottenflotte_attributes_df["Total_numbers_of_Bikes"] = number_of_bikes_total
    
    # merge dataframes with names togehter on key "Station_ID"
    result_day = pd.merge(sprottenflotte_attributes_df, sprottenflotte_names_df, on="Station_ID")
    # save Dataframe as csv
    result_day.to_csv("./general_data/sprottenflotte_attributes_day.csv")

    print("First Dataframe saved.")

    avg_number_of_bike_per_half = avg_number_of_bike_per_half_hour(sprottenflotte_df)

    avg_usage_of_station_per_half = avg_usage_of_station_per_half_hour(sprottenflotte_df)

    avg_returning_bike_of_station_per_half = avg_returning_bike_of_station_per_half_hour(sprottenflotte_df)

    avg_renting_bike_of_station_per_half = avg_renting_bike_of_station_per_half_hour(sprottenflotte_df)


    # prepare  average number of bikes per day for dataframe
    avg_number_of_bike_half_hour_list = []
    for key in avg_number_of_bike_per_half:
        avg_number_of_bike_half_hour_list.append(avg_number_of_bike_per_half[key])

    # prepare average usage of station per day for dataframe
    avg_usage_of_station_per_half_list = []
    for key in avg_usage_of_station_per_half:
        avg_usage_of_station_per_half_list.append(avg_usage_of_station_per_half[key])

    avg_returning_bike_of_station_per_half_list = []
    for key in avg_returning_bike_of_station_per_half:
        avg_returning_bike_of_station_per_half_list.append(avg_returning_bike_of_station_per_half[key])

    avg_renting_bike_of_station_per_half_list = []
    for key in avg_renting_bike_of_station_per_half:
        avg_renting_bike_of_station_per_half_list.append(avg_renting_bike_of_station_per_half[key])

    sprottenflotte_attributes_half_hour_df = pd.DataFrame(station_id ,columns=["Station_ID"])
    
    # append all the attribute with values to the dataframes
    sprottenflotte_attributes_half_hour_df["Frequency_of_Usage"] = total_frequency_of_station_rentals_list
    sprottenflotte_attributes_half_hour_df["Avg_Number_of_Bikes"] = avg_number_of_bike_half_hour_list
    sprottenflotte_attributes_half_hour_df["Avg_Usage_of_Station"] = avg_usage_of_station_per_half_list
    sprottenflotte_attributes_half_hour_df["Avg_Returning_Bike_of_Station"] = avg_returning_bike_of_station_per_half_list
    sprottenflotte_attributes_half_hour_df["Avg Renting_Bike_of_Station"] = avg_renting_bike_of_station_per_half_list
    sprottenflotte_attributes_half_hour_df["Total_numbers_of_Bikes"] = number_of_bikes_total

    # merge dataframes with names togehter on key "Station_ID"
    result_half_hour = pd.merge(sprottenflotte_attributes_half_hour_df, sprottenflotte_names_df, on="Station_ID")

    # save Dataframe as csv
    result_half_hour.to_csv("./general_data/sprottenflotte_attributes_half_hour.csv")
    print("Done.")




