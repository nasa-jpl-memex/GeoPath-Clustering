
def filter_data(data):
    phone_numbers = data.keys()
    
    # replace consecutive repeated locations with one
    for phone_number in phone_numbers:
        refined_location = []
        prev_loc = ""
        for loc in data[phone_number]:
            if not prev_loc == loc:
                refined_location.append(loc)
            prev_loc=loc
        
        data[phone_number] = refined_location
        
    #Remove phone_numbers with just one location
    for phone_number in phone_numbers:
        if len(data[phone_number]) < 3:
            del data[phone_number]
    
    return data