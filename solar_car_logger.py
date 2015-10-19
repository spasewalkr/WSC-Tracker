#!/usr/bin/env/python

import os,sys
import json
import optparse
import urllib2
import time
import datetime

class Position:
    def __init__(self, lat, lon, time, gps_age):
        self.latitude = lat
        self.longitude = lon
        self.timestamp = datetime.datetime.strptime(time, "%Y-%m-%d %X")
        self.loc_age = gps_age
    
    def __eq__(self, other):
        lats = self.latitude == other.latitude
        longs = self.longitude == other.longitude
        times = self.timestamp == other.timestamp

        return lats and longs and times

class SolarCar:
    def __init__(self, team_id, team_name, number, name, country_code, car_class, position):
        self.team_id = team_id
        self.team_name = team_name
        self.team_number = number
        self.car_name = name
        self.country_code = country_code
        self.car_class = car_class
        self.position = position
        

def main():
    usage = "Usage: solar_car_logger.py -o <outfile>"
    parser = optparse.OptionParser(usage)
    parser.add_option("-o", "--outfile", dest="filename", action="store", type="string",
        default="~/Desktop/solar_car_data.log",
        help="Write logged data to <outfile>")
    
    (options, args) = parser.parse_args()
    options.filename = os.path.expanduser(options.filename)
    
    of = open(options.filename, 'w')
    
    # Dictionary of known cars, indexed by team number
    seen_cars = {}
    
    try:
        while(True):
            json_data = collect_data()
            data = json.loads(json_data)
        
            for car_data in data:
                car_position = Position(car_data['lat'], car_data['lng'], car_data['gps_when'], car_data['gps_age'])
                car = SolarCar(car_data['id'], car_data['name'], car_data['number'], car_data['car_name'], car_data['country'], car_data['class_id'], car_position)
                
                try:
                    prev_car = seen_cars[car.team_number]
                    prev_loc = prev_car.position
                    
                    seen_cars[car.team_number] = car
                    
                    if prev_loc == car.position:
                        print "Location unchanged", car.team_name
                    else:
                        of.write(json_data)
                        print "New data collected.", car.team_name
                except KeyError:
                    seen_cars[car.team_number] = car
                    of.write(json_data)
                    print "Car not seen before.", car.team_name
                    
            print "Trying again in 10 seconds..."
            time.sleep(10)
                
    except KeyboardInterrupt:
        of.close()
        print "File saved.  Data written to ", options.filename
        sys.exit()

# Returns the WSC data from wsc.org    
def collect_data():
    data = urllib2.urlopen("http://www.worldsolarchallenge.org/api/positions")
    return data.read()
    

if __name__ == "__main__":
    main()
