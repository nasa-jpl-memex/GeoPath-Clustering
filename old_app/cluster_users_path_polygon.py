'''
Creates a vector of ordered location for each user and clusters them using that vector.

User:
U1 : LA -> NYC -> Chicago
U2 : LA -> NYC -> Seattle

Location coordinate:
LA : 33.98997825,-118.1799805 
NYC : 40.74997906,-73.98001693 
Chicago : 41.82999066,-87.75005497 
Seattle : 47.57000205,-122.339985 

U1 : [(33.98997825,-118.1799805), (40.74997906,-73.98001693), (41.82999066,-87.75005497)]
U2 : [(33.98997825,-118.1799805), (40.74997906,-73.98001693), (47.57000205,-122.339985)] 
'''
from distance_util import  frechetDist
import matplotlib.pyplot as plt
import numpy as np
import json
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import pairwise_distances
import cPickle as pickle

from data_util import filter_data

if __name__ == '__main__':
    line = open("test.json","r").readline()
    raw_data = eval(line)
    data = {}
    # converting data to dictionary K-> phone , V-> list of cordinates
    for obj in raw_data:
        data[obj["phone"]] = obj["points"]
        
    data = filter_data(data)
    
    phone_numbers = data.keys()
    routes = data.values()
    
    print len(data)
    
    def get_frechet_dist(i,j):
        i, j = int(i[0]), int(j[0])
        if i == j:
            return 0 
        s1, s2 = routes[i], routes[j]
        
         
        return frechetDist(s1, s2)
    
    n_jobs = 1

    X = np.arange(len(routes)).reshape(-1, 1)
    similarity_matrix = pairwise_distances(X,metric=get_frechet_dist, n_jobs=n_jobs)
    
    print "Calculated similarity_matrix", similarity_matrix.shape
    pickle.dump(similarity_matrix, open("./static/data/similarity_matrix_frechet.p","w"), protocol=2)
    
    db = DBSCAN(eps=0.3, metric='precomputed', n_jobs=n_jobs).fit(similarity_matrix)
      
    print 'Number of unique cluster lables', len(np.unique(db.labels_))
    
    pickle.dump(db.labels_, open("./static/data/clusters_frechet.p","w"), protocol=2)
    pickle.dump(phone_numbers, open("./static/data/phone_numbers_frechet.p","w"), protocol=2)
    
    colors = [ "blue","green","red","cyan","magenta","yellow","black","white","brown","burlywood"]
    for idx,route in enumerate(routes):
        P = np.array(route)
        if db.labels_[idx] >= 0:
            plt.plot(P[:,0], P[:,1], marker="o", color=colors[db.labels_[idx] ])
            print colors[db.labels_[idx] ],"\t",phone_numbers[idx],"\t", route


    plt.savefig("clusters")
    plt.close()
    
    for idx,route in enumerate(routes):
        P = np.array(route)
        plt.plot(P[:,0], P[:,1], marker="o", color="black")
    
    plt.savefig("data")


