'''
Creates a location vector for each user and clusters them using that vector.

User:
U1 : LA -> NYC -> Chicago
U2 : NYC -> LA ->  Seattle

Vector index:
LA : 0 
NYC : 1 
Chicago : 2 
Seattle : 3 

Resultant Vectors:
U1 : [1,1,1,0]
U2 : [1,1,0,1]
'''

import numpy as np
from sklearn.cluster import KMeans
import cPickle as pickle

n_clusters=500

# Test data
# data = { "ph1":["LA", "NYC", "Chicago"], "ph2":["LA","NYC","Seattle"], "ph3":["tst1","tst2","tst3"] }
# n_clusters=2

line = open("phones_and_cities.json","r").readline()
data = eval(line)


phone_numbers = data.keys()
phone_location_vector = []

# Find all uniques_locations
uniques_locations = set([])
for phone_number, locations in data.iteritems():
    uniques_locations = uniques_locations.union( set(locations) )

loc_to_idx = dict([(v,k) for k,v in enumerate(uniques_locations)])

print "Unique locations- ", len(uniques_locations)

for phone_number in phone_numbers:
    str_location = data[phone_number]
    location_vector = [0]*len(uniques_locations)
    for location in str_location:
        location_vector[loc_to_idx[location]] = location_vector[loc_to_idx[location]]+1
    
    phone_location_vector.append(location_vector) 

print "Created vectors, Total vectors- ", len(phone_location_vector)

n_jobs = 2

db = KMeans(n_clusters=n_clusters, n_jobs=n_jobs, verbose=0).fit(phone_location_vector)
  
print 'Number of unique cluster lables', len(np.unique(db.labels_))


pickle.dump(db.labels_, open("./static/data/clusters_location.p","w"), protocol=2)
pickle.dump(phone_numbers, open("./static/data/phone_numbers_location.p","w"), protocol=2)





