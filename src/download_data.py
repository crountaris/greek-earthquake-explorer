import time
from pathlib import Path

import pandas as pd
import requests
import io 


URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

def get_year(year):
    """Download all M2.5+ earthquakes around Greece for one year."""
    #Parameters 
    params = {
        "format": "csv",
        "starttime": f"{year}-01-01",
        "endtime":f"{year}-12-31T23:59:59",
        "minmagnitude":2.5,
        "minlatitude":34,
        "maxlatitude":42,
        "minlongitude":19,
        "maxlongitude":30,
    }
    #Building the Address and Download
    query = "&".join(f"{k}={v}" for k, v in params.items())
    full_url = URL + "?" + query
    response = requests.get(full_url, timeout=60)    
    if response.status_code !=200:
         print("Problem with year", year, "- Status", response.status_code)                 #sends the request to the server and waits for a response, timeout=60 means wait 60 seconds before giving up
         print(response.text [:500 ])
         raise SystemExit(1)           
    df = pd.read_csv(io.StringIO(response.text))                          #if the response is not 200 (OK) then print an error message
    #Report, Pause and Return
    print(year, len(df), "earthquakes")
    time.sleep(1)
    return df

if __name__ == "__main__":
    frames = []                                                          #lists a container that holds the data in order
    for year in range(2000,2026):                                        #takes each year and produces numbers 2000,2001....
            frames.append(get_year(year))                                #adds the table to the end of the list
    eq= pd.concat(frames, ignore_index =True)                            #eq = earthquakes, pd.concat takes a list of tables and joins them, ignore_index=True renumbers the rows 0,1,2... 
    Path("data").mkdir(exist_ok = True)                                  #creates the data folder if it is missing, Path points to the folder and mkdir creates it, exist_ok=True means dont do it if it already exists
    eq.to_csv("data/earthquakes.csv", index = False)                     #writes the table to a file
    print(f"Saved {len(eq)} earthquakes to data/earthquakes.csv")        #Prints a message that it completed X earthquakes 
