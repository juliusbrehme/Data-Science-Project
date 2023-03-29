import pandas as pd
import requests 
import logging 
import os
import argparse


logging.basicConfig(level=logging.INFO)


def main_weather(api_address: str, name_file: str):

    name_csv_file = name_file

    path_csv_file = "./results/" + name_csv_file + ".csv"
    
    try:
        # get json object of the api
        response = requests.get(api_address)

    except (requests.RequestException, requests.ConnectionError, requests.HTTPError, requests.URLRequired, 
            requests.TooManyRedirects, requests.ConnectTimeout, requests.ReadTimeout, requests.Timeout) as err:
        logging.warning("Connection error, will continue with next query.")
        logging.warning("Exception raised: %s", err)
        with open('./results/time_log.txt', 'a') as file:
            file.write("\n"f"{err}")
    
    else:

        try: 
            # save response as dict
            data_json = response.json()
        
        except (requests.JSONDecodeError) as err:
            logging.warning("Could not decode the text into json. Continue with the next query.")
            logging.warning("Exception raised: %s", err)
            with open('./results/time_log.txt', 'a') as file:
                file.write("\n"f"{err}")

        else: 
            
            list_of_data = []
            
            # get the data from the returned dictonary
            timestamp = data_json["weather"]["timestamp"]
            cloud_cover = data_json["weather"]["cloud_cover"]
            condition = data_json["weather"]["condition"]
            precipitation_10 = data_json["weather"]["precipitation_10"]
            relative_humidity = data_json["weather"]["relative_humidity"]
            visibility = data_json["weather"]["visibility"]
            wind_direction_10 = data_json["weather"]["wind_direction_10"]
            wind_speed_10 = data_json["weather"]["wind_speed_10"]
            wind_gust_speed_10 = data_json["weather"]["wind_gust_speed_10"]
            sunshine_30 = data_json["weather"]["sunshine_30"]
            temperature = data_json["weather"]["temperature"]
            station = data_json["sources"][0]["station_name"]

            list_of_data.append([cloud_cover, condition, precipitation_10, relative_humidity, visibility, wind_direction_10,
                                 wind_speed_10, wind_gust_speed_10, sunshine_30, temperature, station, timestamp])
            

            dataframe = pd.DataFrame(list_of_data, columns=["cloud_cover", "Condition", "Precipitation", "relative_humidity",
                                                            "Visibility", "wind_direction", "wind_speed", "wind_gust_speed",
                                                            "Sunshine", "Temperature", "Station", "timestamp"])

            if os.path.isfile(path_csv_file):
                hdr = False
            else:
                hdr = True
            
            dataframe.to_csv(path_csv_file, mode='a', index=False, header=hdr)
            logging.info("Dataframe %s saved.", name_file)



if __name__ == '__main__':

    # api_address = "https://api.brightsky.dev/current_weather?lat=54.3776&lon=10.1424"
    # name_csv_file = "weather_data"

    parser = argparse.ArgumentParser()
    parser.add_argument("api_address", type=str)
    parser.add_argument("name_file", type=str)

    args = parser.parse_args()

    api_address = args.api_address
    name_file = args.name_file

    directory_path = "./results"
    try:
        os.mkdir(directory_path)
    except OSError:
        logging.info("Directory already exist.")
    else:
        logging.info("Directory created succesfully.")

    main_weather(api_address, name_file)