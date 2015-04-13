Public safety around schools of Chicago
=======================================

Public data:
------------
Chicago crimes in 2014: https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-present/ijzp-q8t2
[Filter: year 2014, and export as CSV file]

Chicago Public Schools (2014-2015): https://data.cityofchicago.org/Education/Chicago-Public-Schools-School-Locations-2014-2015-/3fhj-xtn5
[export as CSV and KML files]



Motivation:
-----------
Choosing the right school for a child requires parents to assess a multitude of different pieces of information. An important one is the safety of the school’s immediate environment. The frequency of the crimes in the prior year can be used as a proxy.

Challenge:
----------
Although the data is publicly available on the City of Chicago Data portal, translating the GPS information to proximity and filtering the crimes that can affect schoolchildren requires data processing. 

Solution:
---------
In this project I combine the crime records of the city of Chicago from 2014 with the geographic locations of the public schools. First, I select the crimes that took place on schooldays during school time, at public spaces where children are likely present. Then I determine the distance of each crime from each school. And finally I count the number of crimes in a 0.25-mile radius of each school.

Results:
--------
I plotted the schools as a function of the number of nearby crimes as a histogram (Hist_schools_w_number_of_crimes.pdf), and I created a map (crime_near_schools.kml) of the schools around Chicago. The color of the markers indicates the number of crimes nearby, and labels show the exact number. (the map can be viewd here: https://www.google.com/maps/d/edit?mid=z0f0NmLaLfg0.kZIHoM3mJsnk)

Outlook:
--------
I imagine continuing implementing these ideas with a graphical user interface, where the user can customize the filters for time and date, place and type of crime, and set the size of the radius of the schools, this data can be made accessible to a large group of users. A web-based application based on these ideas can generate a significant traffic from parents with small children.

