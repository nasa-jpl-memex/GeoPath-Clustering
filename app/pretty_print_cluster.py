import cPickle as pickle

suffix = "edit" #location

labels = pickle.load(open("./static/data/clusters_" + suffix + ".p","r"))
phones = pickle.load(open("./static/data/phone_numbers_" + suffix + ".p","r"))

label_to_phone = {}

for idx,label in enumerate(labels):
    if label not in label_to_phone and label != -1:
        label_to_phone[label] = []
    
    if label != -1:
        label_to_phone[label].append(phones[idx])
    
print "Total clusters - ",len(label_to_phone)

pickle.dump(label_to_phone.values() , open("./static/data/clustered_phone_" + suffix + ".p","w"), protocol=2)