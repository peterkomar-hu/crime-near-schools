import re
import csv
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import datetime as dt

def GPSdistance(lat1, long1, lat2, long2):
 
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = np.pi/180.0
         
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
         
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
         
    # Compute spherical distance from spherical coordinates.
         
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
     
    cos = (np.sin(phi1)*np.sin(phi2)*np.cos(theta1 - theta2) + 
           np.cos(phi1)*np.cos(phi2))
    arc = np.arccos( cos )
    dist = 3959 * arc
    return dist

# determine the closest school ID and distance to it for each crime
def closest_school(crime_lat, crime_long, school_locations):
    closest_school_id = []
    for num in range(0, len(crime_lat)):
        if ~np.isnan(crime_lat[num]) & ~np.isnan(crime_long[num]):
            school_locations['distance_from_this_crime'] = GPSdistance(crime_lat[num], \
                                                                      crime_long[num], \
                                                                      school_locations['latitude'], \
                                                                      school_locations['longitude'] )
            closest_school_id.append( \
                        school_locations['SCHOOLID'][school_locations['distance_from_this_crime'].argmin()])
        else:
            closest_school_id.append(np.nan)
    return closest_school_id


# extract schoolid and location data from kml file
kmlfilename = 'Chicago Public Schools - School Locations (2014- 2015) - Map.kml'
id_pat = r'SCHOOLID</span>:</strong> <span class="atr-value">(.+)</span>'
long_pat = r'<longitude>(.+)</longitude>'
lat_pat  = r'<latitude>(.+)</latitude>'
    
file = open(kmlfilename, 'r')
filecontent = file.read()
file.close()

match_id = re.findall(id_pat, filecontent)
match_long = re.findall(long_pat, filecontent)
match_lat = re.findall(lat_pat, filecontent)

match_long.pop(0)
match_lat.pop(0)


csvfile = open('./school_locations.csv', 'w')

csvfile.write('SCHOOLID' + ',' + 'latitude' + ',' + 'longitude' + '\n' )
for index in range( 0, len(match_id) ):
    csvfile.write('%s,%s,%s\n' % (match_id[index], match_lat[index], match_long[index]) )

csvfile.close()

# number of rows to read
number_of_rows = None

# import data
school_locations = pd.read_csv('./school_locations.csv')
school_names = pd.read_csv('./CPS_School_Locations_SY1415.csv')
crime = pd.read_csv('./Crimes_2014.csv', parse_dates = ['Date'], nrows = number_of_rows)

# separate out year, day and hour or crimes
crime['weekday'] = crime['Date'].dt.weekday
crime['hour'] = crime['Date'].dt.hour
crime['year'] = crime['Date'].dt.year

# time filters
in_2014 = crime['year'] == 2014
during_school_hours = (crime['hour'] >= 8) & (crime['hour'] <= 17 )
on_school_day   = crime['weekday'].isin([0, 1, 2, 3, 4])

# filters relevant for children going to school
# domestic crimes
domestic = crime['Domestic'] == True


# crimes at public locations with children
public_locations_w_children = ['STREET', 'SIDEWALK', 'PARKING LOT/GARAGE(NON.RESID.)', 'ALLEY', \
                               'SCHOOL, PUBLIC, BUILDING', 'VEHICLE NON-COMMERCIAL', 'PARK PROPERTY', \
                               'SCHOOL, PUBLIC, GROUNDS', 'OTHER', 'DAY CARE CENTER', 'SCHOOL, PRIVATE, BUILDING', \
                               'SCHOOL, PRIVATE, GROUNDS', 'BRIDGE', 'DRIVEWAY', 'NURSING HOME', 'CTA TRAIN', \
                               'CTA PLATFORM', 'CTA BUS STOP', 'CTA STATION']
at_public_space_w_children = crime['Location Description'].isin(public_locations_w_children )

# all filters together
school_2014 = in_2014 & at_public_space_w_children & during_school_hours & on_school_day & ~domestic

# determine the closest school ID and distance to it for each crime
crime['closest_school_id'] = pd.DataFrame( \
                        closest_school(np.array(crime['Latitude']), \
                                       np.array(crime['Longitude']), \
                                       school_locations) )
school_latitudes = school_locations.set_index('SCHOOLID')['latitude'].to_dict()
school_longitudes = school_locations.set_index('SCHOOLID')['longitude'].to_dict()
crime['closest_school_latitude'] = crime['closest_school_id'].map(school_latitudes)
crime['closest_school_longitude'] = crime['closest_school_id'].map(school_longitudes)
crime['closest_school_distance'] = \
       GPSdistance(crime['Latitude'], crime['Longitude'], \
                   crime['closest_school_latitude'], crime['closest_school_longitude'])
				   
# histogram of the schools vs the number of crimes in their radius
school_radius = 0.25 # in miles
in_school_radius = crime['closest_school_distance'] < school_radius
number_of_crimes_nearby = crime[in_school_radius].groupby('closest_school_id')['ID'].count()

# count the number of crimes in the radius of each school
number_of_crimes_nearby_dict = number_of_crimes_nearby.to_dict()
school_locations['number_of_crimes_in_radius'] = school_locations['SCHOOLID'].map(number_of_crimes_nearby.to_dict())
integer_bins = np.array(range(0,2000,20))-0.5

hist_figure = school_locations['number_of_crimes_in_radius'].fillna(0).plot(kind = 'hist', bins = integer_bins, \
                                                                        color = 'black')
plt.title('Crimes in 2014, in Chicago, during school hours (8-17),\n on schooldays (M-F), at public spaces with children')
plt.xlabel('Number of non-domestic crimes in radius of school (' + str(school_radius) + ' miles)')
plt.ylabel('Number of schools')
plt.savefig('Hist_schools_w_number_of_crimes.pdf')

# add names to schools
schools = pd.merge(school_locations.fillna(0), school_names, left_on = 'SCHOOLID', right_on = 'SCHOOLID')
schools = schools.set_index('SCHOOLNAME').sort()

# define the bins corresponding to the colors on the map
bin_limits = [25, 50, 100, 200, 400, 800, 10000]
bin_colors = {0: 'ff008800', \
              1: 'ff00ff00', \
              2: 'ff00ff88', \
              3: 'ff00ffff', \
              4: 'ff0088ff', \
              5: 'ff0000ff', \
              6: 'ff000088'}

def find_crime_bin(number, bin_limits):
    for bin_num in range(0, len(bin_limits)):
        if number <= bin_limits[bin_num]:
            break
    return bin_num

	# create KML file
kmlfile = open('crime_near_schools.kml', 'w')

layer_title = "Number of crimes close to schools in Chicago, in 2014"

# print header of KML file
kmlfile.write("<?xml version='1.0' encoding='UTF-8'?>\n")
kmlfile.write("<kml xmlns=\"http://earth.google.com/kml/2.2\">\n")
kmlfile.write("\t<Document>\n")
kmlfile.write("\t\t<name>" +  layer_title + "</name>\n")

# add marker info


for ix in schools.index:
    kmlfile.write("\t\t<Placemark>\n")
    this_bin = find_crime_bin( schools.loc[ix]['number_of_crimes_in_radius'] , bin_limits)
    kmlfile.write("\t\t\t<styleUrl>#icon-" + str(int(this_bin)) +"</styleUrl>\n")
    this_name = ''.join(e for e in ix if e.isalnum() | e.isspace())
    this_name = this_name + ' (' + schools.loc[ix]['ADDRESS']  + ')'
    kmlfile.write("\t\t\t<name>" + this_name + "</name>\n")
    this_description = str(int(schools.loc[ix]['number_of_crimes_in_radius'])) + " crimes nearby (in 2014)" 
    kmlfile.write("\t\t\t<description><![CDATA[" + this_description + "]]></description>\n")
    kmlfile.write("\t\t\t<Point>\n")
    kmlfile.write("\t\t\t\t<coordinates>" + str(schools.loc[ix]['longitude']) + "," + str(schools.loc[ix]['latitude']) + ",0.0</coordinates>\n")
    kmlfile.write("\t\t\t</Point>\n")
    kmlfile.write("\t\t</Placemark>\n")
    
# add style info
for bin_num in range(0, len(bin_colors)):
    kmlfile.write("\t\t<Style id='icon-" + str(int(bin_num)) + "'>\n")
    kmlfile.write("\t\t\t<IconStyle>\n")
    kmlfile.write("\t\t\t\t<color>" + bin_colors[bin_num] + "</color>\n")
    kmlfile.write("\t\t\t\t<Icon>\n")
    kmlfile.write("\t\t\t\t\t<href>http://www.gstatic.com/mapspro/images/stock/959-wht-circle-blank.png</href>\n")
    kmlfile.write("\t\t\t\t</Icon>\n")
    kmlfile.write("\t\t\t</IconStyle>\n")
    kmlfile.write("\t\t</Style>\n")
               
# print footer
kmlfile.write("\t</Document>\n</kml>")

kmlfile.close()