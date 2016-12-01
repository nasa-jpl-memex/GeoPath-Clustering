import cPickle as pickle

suffix = "edit" #location

labels = pickle.load(open("./static/data/clusters_" + suffix + ".p","r"))
phones = pickle.load(open("./static/data/phone_numbers_" + suffix + ".p","r"))

label_to_phone = {}

for idx,label in enumerate(labels):
    if label not in label_to_phone:
        label_to_phone[label] = []
    
    label_to_phone[label].append(phones[idx])
    

pickle.dump(label_to_phone.values() , open("./static/data/clustered_phone_" + suffix + ".p","w"), protocol=2)