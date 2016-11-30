'''
Creates a vector of ordered location for each user and clusters them on based of edit distance

User:
U1 : LA -> NYC -> Chicago
U2 : LA -> NYC -> Seattle

U1 : [012]
U2 : [013]

Edit Dist : 1
'''
import editdistance
import numpy as np
from sklearn.cluster import DBSCAN
import cPickle as pickle

# Test data
# data = { "ph1":["LA", "NYC", "Chicago"], "ph2":["LA","NYC","Seattle"], "ph3":["tst1","tst2","tst3"] }

line = open("phones_and_cities.json","r").readline()
data = eval(line)


phone_numbers = data.keys()
list_location_encoded = []
similarity_matrix = np.zeros((len(data),len(data)))

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
    encoded_location = [ str(loc_to_idx[location]) for location in str_location]
    
    list_location_encoded.append("".join(encoded_location) )

print "Encoded locations, Total data set- ", len(list_location_encoded)

# for i in range(len(phone_numbers)):
#     for j in range(i,len(phone_numbers)):
#         dist = edit_dist(list_location_encoded[i],list_location_encoded[j])
#         
#         similarity_matrix[i][j] = dist
#         similarity_matrix[j][i] = dist
# 
# db = DBSCAN(eps=0.9, min_samples=2, metric='precomputed').fit(similarity_matrix)


def edit_dist(i,j):
    i, j = int(i[0]), int(j[0])
    if i == j:
        return 0 
    return editdistance.eval(list_location_encoded[i],list_location_encoded[j])

X = np.arange(len(data)).reshape(-1, 1)

db = DBSCAN(metric=edit_dist, eps=1, min_samples=2, n_jobs=1).fit(X)  
print 'Number of unique cluster lables', len(np.unique(db.labels_))

pickle.dump(db.labels_, open("./static/data/clusters_edit.p","w"), protocol=2)
pickle.dump(phone_numbers, open("./static/data/phone_numbers_edit.p","w"), protocol=2)




