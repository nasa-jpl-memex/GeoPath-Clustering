'''
Creates a vector of ordered location for each user and clusters them on based of edit distance

User:
U1 : LA -> NYC -> Chicago
U2 : LA -> NYC -> Seattle

U1 : [012]
U2 : [013]

Edit Dist : 1
'''
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import pairwise_distances

import cPickle as pickle

# Test data
# data = { "ph1":["LA", "NYC", "Chicago"], "ph2":["LA","NYC","Seattle"], "ph3":["tst1","tst2","tst3"] }

line = open("phones_and_cities.json","r").readline()
data = eval(line)


phone_numbers = data.keys()
list_location_encoded = []
similarity_matrix = np.zeros((len(data),len(data)))

#Remove phone_numbers with just one location
for phone_number in phone_numbers:
    if len(data[phone_number]) < 2:
        del data[phone_number]

phone_numbers = data.keys()

# Encode locations to unique integers
# Map a unique integer to each location
loc_to_idx = {}
# Find all uniques_locations
uniques_locations = set([])
for phone_number, locations in data.iteritems():
    uniques_locations = uniques_locations.union( set(locations) )

loc_to_idx = dict([(v,k) for k,v in enumerate(uniques_locations)])

print "Unique locations- ", len(loc_to_idx)

for phone_number in phone_numbers:
    str_location = data[phone_number]
    encoded_location = [ loc_to_idx[location] for location in str_location]
    
    list_location_encoded.append(encoded_location) 

print "Encoded locations, Total data set- ", len(list_location_encoded)


def edit_dist(i,j):
    i, j = int(i[0]), int(j[0])
    if i == j:
        return 0 
    
    s1, s2 = list_location_encoded[i], list_location_encoded[j]
    
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    
    # Normalize distance w.r.t. to len(s1) to ensure similar result for varied length lists
    return (1.0 * distances[-1] / len(s1))

n_jobs = 2

X = np.arange(len(list_location_encoded)).reshape(-1, 1)
similarity_matrix = pairwise_distances(X,metric=edit_dist, n_jobs=n_jobs)

pickle.dump(similarity_matrix, open("./static/data/similarity_matrix_edit.p","w"), protocol=2)
print "Calculated similarity_matrix", similarity_matrix.shape

db = DBSCAN(eps=0.5, min_samples=2, metric='precomputed', n_jobs=n_jobs).fit(similarity_matrix)
  
print 'Number of unique cluster lables', len(np.unique(db.labels_))

pickle.dump(db.labels_, open("./static/data/clusters_edit.p","w"), protocol=2)
pickle.dump(phone_numbers, open("./static/data/phone_numbers_edit.p","w"), protocol=2)




