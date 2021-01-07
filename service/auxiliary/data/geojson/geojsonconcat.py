import geojson
import os
import json
from jsonmerge import merge
directory = "./data"
i = 0
for filename in os.listdir(directory):
    with open("./data/"+filename) as f:
        if i == 0:
            gj = geojson.load(f)
            
        else:

            new = geojson.load(f)
            gj["features"] += new["features"]
            
             

        i += 1


with open('allcp.geojson', 'w') as outfile:
    json.dump(gj, outfile)
