import requests
import pandas as pd
from datetime import datetime, timedelta
from time import time 
import os
import logging
import argparse


logging.basicConfig(level=logging.INFO)

def main_donkey(api_address: str, name_file: str):

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
            # timestamp of the last update of donkey republic (will be close to the same of the request)
            last_update = data_json["last_updated"]

            # get the dictonary entry with the information of the sation 
            stations = data_json["data"]["stations"]

            # list to save the data and to use to create a dataframe with the list
            list_of_data = []

            for info in stations:
                # get infos of the entries of each dictonary
                station_id = info["station_id"]
                num_bikes_available = info["num_bikes_available"]
                num_docks_available = info["num_docks_available"]
                is_installed = info["is_installed"]
                is_renting = info["is_renting"]
                is_returning = info["is_returning"]
                last_reported = info["last_reported"]

                list_of_data.append([station_id, num_bikes_available, num_docks_available, is_installed, is_renting, 
                                    is_returning, last_reported, last_update])

            dataframe = pd.DataFrame(list_of_data, columns=["Station_ID", "Number_of_Bikes", "Number_of_Docks_Available", 
                                                            "is_installed", "is_renting", "is_returning", "last_reported", "last_update"])

            if os.path.isfile(path_csv_file):
                hdr = False
            else:
                hdr = True
            
            dataframe.to_csv(path_csv_file, mode='a', index=False, header=hdr)
            logging.info("Dataframe %s saved.", name_file)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("api_address", type=str)
    parser.add_argument("name_file", type=str)

    args = parser.parse_args()

    api_address = args.api_address
    name_file = args.name_file
    
    # api_sprottenflotte = "https://stables.donkey.bike/api/public/gbfs/donkey_kiel/en/station_status.json"
    # name_csv_file_kiel = "sprottenflotte_data"

    directory_path = "./results"
    try:
        os.mkdir(directory_path)
    except OSError:
        logging.info("Directory already exist.")
    else:
        logging.info("Directory created succesfully.")

    main_donkey(api_address, name_file)