from sprottenflotte_data import main_donkey
from weather_data import main_weather
import os
import logging
import time

directory_path = "./results"

api_sprottenflotte = "https://stables.donkey.bike/api/public/gbfs/donkey_kiel/en/station_status.json"
name_csv_file_kiel = "sprottenflotte_data"

api_aarhus = "https://stables.donkey.bike/api/public/gbfs/donkey_aarhus/en/station_status.json"
name_csv_file_aarhus = "aarhus_data"

api_genf = "https://stables.donkey.bike/api/public/gbfs/donkey_ge/de/station_status.json"
name_csv_file_genf = "genf_data"

api_weather_kiel = "https://api.brightsky.dev/current_weather?lat=54.3776&lon=10.1424"
name_csv_file_weather = "weather_data"

try:
    os.mkdir(directory_path)

except OSError:
    logging.info("Directory already exist.")

else:
    logging.info("Directory created succesfully.")

hour = 0

while (True):

    # data of Kiel
    main_donkey(api_sprottenflotte, name_csv_file_kiel)
    # data of Aarhus
    main_donkey(api_aarhus, name_csv_file_aarhus)
    # data of Genf
    main_donkey(api_genf, name_csv_file_genf)

    # get weather data only every half an hour
    if (hour % 2100 == 0):
        main_weather(api_weather_kiel, name_csv_file_weather)

    logging.info("Iteration done, sleeping for 5 minutes until next one.")
    time.sleep(300)
    hour += 300

