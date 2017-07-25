# GeoPath-Clusetring
Memex Route Clustering project is trying to provide tools and technologies to be able explore some Memex data as route format. Routes is defined as moving object through time into different geo-location. One of main goal of this project is to develop an algorithm to be able to cluster routes that are traveling same path which helps us to not only understand more about the data but also find some anomalies.


### 4 usecases:

#### Use case 1:

Using text input (phone numbers, emails, names, ad text) and other facets of the data (eg, time, location) search for relevant routes and clusters of routes that match the entered criteria ( over a time range ?)
https://oodt.jpl.nasa.gov/wiki/display/MEMEX/Use+case+1%3A+Search+for+Routes+by+ad+data

#### Use case 2:

As a user, I should be able to search for ads that appear in multiple locations within the same time range.
https://oodt.jpl.nasa.gov/wiki/display/MEMEX/Use+case+2%3A+Identify+Concurrent+Ads

#### Use case 3:

As a user, I should be able to enter a route and expect to see similar routes.
https://oodt.jpl.nasa.gov/wiki/display/MEMEX/Use+case+3%3A+Search+for+Routes+by+Traffic+Pattern

#### Use case 4:

Given a specific city, present information about the routes that enter and exit through the city ( over a time range ?)
https://oodt.jpl.nasa.gov/wiki/display/MEMEX/Use+case+4%3A+City+Report

Currently use case number 1 has not been implemented

#### Dataset and Schema:

We used Apache Solr to index ads data point and segments as two separate core, you can find the shcema format for each in  https://oodt.jpl.nasa.gov/wiki/display/MEMEX/Dataset+and+Schema 


#### Installation:

To run this application Solr is need. Data need to be extracted from lattice_hdfs and converted to json following the schema and indexed to Solr. You can change config.txt for Solr and Flask port and more.

Flask, requests and ConfigParser can be installed through 'pip install'
