import datetime
import time
import requests
from ConfigParser import SafeConfigParser


conf_parser = SafeConfigParser()
conf_parser.read('config.txt')


SOLR_URL = conf_parser.get('general', 'SOLR_URL')
SOLR_AD_POINTS_CORE = conf_parser.get('general', 'SOLR_AD_POINTS_CORE')
SOLR_SEGMENT_CORE = conf_parser.get('general', 'SOLR_SEGMENT_CORE')
SUBDOMAIN = conf_parser.get('general', 'SUBDOMAIN')

geocode_url = "http://maps.googleapis.com/maps/api/geocode/json?address={0}"



def use_case_2(start_date, end_date, phone_number=None):

    entities_found = dict()
    start_d = datetime.datetime.strptime(start_date, "%m/%d/%Y")
    start_date = time.mktime(start_d.timetuple())

    end_d = datetime.datetime.strptime(end_date, "%m/%d/%Y")
    end_date = time.mktime(end_d.timetuple())

    q_query = "q=*:*"
    date_query = "fq=date:[{0} TO {1}]".format(start_date, end_date)
    phone_query = "q=phone_number%3A*{0}*".format(phone_number)

    if phone_number:
        url  = "{0}/{1}/select?wt=json&rows=2147483647&{1}&{2}&{3}".format(SOLR_URL, SOLR_AD_POINTS_CORE, date_query, phone_query)
    else:
        url  = "{0}/{1}/select?wt=json&rows=2147483647&{1}&{2}&{3}".format(SOLR_URL, SOLR_AD_POINTS_CORE, q_query, date_query)

    r = requests.get(url)
    docs = r.json()['response']['docs']
    for doc in docs:
        date = datetime.datetime.fromtimestamp(int(doc['date'][0])).strftime('%Y-%m-%d')
        if doc['phone_number'][0] in entities_found:
            entities_found[doc['phone_number'][0]]["count"] += 1
            is_city = False
            each = None
            for each in entities_found[doc['phone_number'][0]]["locations"]:
                if each['city_name'] == doc['city'][0]:
                    is_city = True
                    break
            if is_city:
                each['count'] += 1
                if date not in each['dates']:
                    each['dates'].append(date)
            else:
                entities_found[doc['phone_number'][0]]["locations"].append({"city_name":doc['city'][0], "latitude":doc['latitude'][0], "longitude":doc['longitude'][0], "count":1, "dates":[date]})
        else:
            entities_found[doc['phone_number'][0]] = {"count":1, 'locations':[{"city_name":doc['city'][0], "latitude":doc['latitude'][0], "longitude":doc['longitude'][0], "count":1, "dates":[date]}]}

    return entities_found
