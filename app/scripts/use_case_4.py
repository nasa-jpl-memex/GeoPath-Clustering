import datetime
import time
import requests
from ConfigParser import SafeConfigParser


conf_parser = SafeConfigParser()
conf_parser.read('config.txt')


SOLR_URL = conf_parser.get('general', 'SOLR_URL')
SOLR_AD_POINTS_CORE = conf_parser.get('general', 'SOLR_AD_POINTS_CORE')
SOLR_SEGMENT_CORE = conf_parser.get('general', 'SOLR_SEGMENT_CORE')


geocode_url = "http://maps.googleapis.com/maps/api/geocode/json?address={0}"



def use_case_4(city, start_date, end_date, radius):
    city_found = dict()
    segments = []
    entities_found = dict()
    start_d = datetime.datetime.strptime(start_date, "%m/%d/%Y")
    start_date = time.mktime(start_d.timetuple())

    end_d = datetime.datetime.strptime(end_date, "%m/%d/%Y")
    end_date = time.mktime(end_d.timetuple())

    r = requests.get(geocode_url.format(city))
    point = r.json()['results'][0]['geometry']['location']
    city_lat = point['lat']
    city_lng = point['lng']
    city_lat_lng_range = float(radius) / 69
    print city_lat_lng_range
    start_lat_query = "fq=start_latitude:[{0} TO {1}]".format(city_lat - city_lat_lng_range, city_lat + city_lat_lng_range)
    start_lng_query = "fq=start_longitude:[{0} TO {1}]".format(city_lng - city_lat_lng_range, city_lng + city_lat_lng_range)
    end_lat_query = "fq=end_latitude:[{0} TO {1}]".format(city_lat - city_lat_lng_range, city_lat + city_lat_lng_range)
    end_lng_query = "fq=end_longitude:[{0} TO {1}]".format(city_lng - city_lat_lng_range, city_lng + city_lat_lng_range)

    q_query = "q=*:*"
    start_date_query = "fq=start_date:[{0} TO *]".format(start_date)
    end_date_query = "fq=end_date:[* TO {0}]".format(end_date)

    #query if city is start city
    url  = "{0}/{1}/select?wt=json&rows=2147483647&{1}&{2}&{3}&{4}&{5}&{6}".format(SOLR_URL, SOLR_SEGMENT_CORE, q_query, start_date_query, end_date_query, start_lat_query, start_lng_query)
    r = requests.get(url)
    docs = r.json()['response']['docs']
    for doc in docs:
        tmp = "{0}_{1}".format("{0:.1f}".format(float(doc["end_latitude"][0])), "{0:.1f}".format(float(doc["end_longitude"][0])))
        if tmp in city_found:
            city_found[tmp]['out'] += 1
        else:
            city_found[tmp] = {'in':0, 'out':1, 'city_name':doc['end_city'][0]}
        segments.append({"id":str(doc['id']), \
                        "code":str(doc['phone_number'][0]), \
                        "points":[[str(doc['start_longitude'][0]), str(doc['start_latitude'][0])],[str(doc['end_longitude'][0]), str(doc['end_latitude'][0])]], \
                        "phone":str(doc['phone_number'][0]), \
                        "start_city":str(doc['start_city'][0].encode("ascii", "ignore")), \
                        "end_city":str(doc['end_city'][0].encode("ascii", "ignore")), \
                        "start_date":datetime.datetime.fromtimestamp(int(doc['start_date'][0])).strftime('%Y-%m-%d'), \
                        "end_date":datetime.datetime.fromtimestamp(int(doc['end_date'][0])).strftime('%Y-%m-%d'),\
                        "bound": "out"
                        })
        if doc['phone_number'][0] in entities_found:
            entities_found[doc['phone_number'][0]]['out'] +=1
        else:
            entities_found[doc['phone_number'][0]] = {'in':0, 'out':1}

    #query if city is end city
    url  = "{0}/{1}/select?wt=json&rows=2147483647&{1}&{2}&{3}&{4}&{5}&{6}".format(SOLR_URL, SOLR_SEGMENT_CORE, q_query, start_date_query, end_date_query, end_lat_query, end_lng_query)
    r = requests.get(url)
    docs = r.json()['response']['docs']
    for doc in docs:
        tmp = "{0}_{1}".format("{0:.1f}".format(float(doc["start_latitude"][0])), "{0:.1f}".format(float(doc["start_longitude"][0])))
        if tmp in city_found:
            city_found[tmp]['in'] += 1
        else:
            city_found[tmp] = {'in':1, 'out':0, 'city_name':doc['start_city'][0]}
        segments.append({"id":str(doc['id']), \
                        "code":str(doc['phone_number'][0]), \
                        "points":[[str(doc['start_longitude'][0]), str(doc['start_latitude'][0])],[str(doc['end_longitude'][0]), str(doc['end_latitude'][0])]], \
                        "phone":str(doc['phone_number'][0]), \
                        "start_city":str(doc['start_city'][0].encode("ascii", "ignore")), \
                        "end_city":str(doc['end_city'][0].encode("ascii", "ignore")), \
                        "start_date":datetime.datetime.fromtimestamp(int(doc['start_date'][0])).strftime('%Y-%m-%d'), \
                        "end_date":datetime.datetime.fromtimestamp(int(doc['end_date'][0])).strftime('%Y-%m-%d'), \
                        "bound": "in"
                        })
        if doc['phone_number'][0] in entities_found:
            entities_found[doc['phone_number'][0]]['in'] +=1
        else:
            entities_found[doc['phone_number'][0]] = {'in':1, 'out':0}

    return city_found, segments, entities_found
