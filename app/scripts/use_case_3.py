import datetime
import time
import requests
import dateutil.relativedelta
from ConfigParser import SafeConfigParser


conf_parser = SafeConfigParser()
conf_parser.read('config.txt')


SOLR_URL = conf_parser.get('general', 'SOLR_URL')
SOLR_AD_POINTS_CORE = conf_parser.get('general', 'SOLR_AD_POINTS_CORE')
SOLR_SEGMENT_CORE = conf_parser.get('general', 'SOLR_SEGMENT_CORE')

geocode_url = "http://maps.googleapis.com/maps/api/geocode/json?address={0}"

total_result = {}

def query(index, start_date, end_date, start_city_lat, start_city_lng, start_city_lat_lng_range, end_city_lat, end_city_lng, end_city_lat_lng_range, result_entity):
    if index == 0 :
        q_query = "q=*:*"
        start_date_query = "fq=start_date:[{0} TO *]".format(start_date)
        end_date_query = "fq=end_date:[* TO {0}]".format(end_date)
        start_lat_query = "fq=start_latitude:[{0} TO {1}]".format(start_city_lat - start_city_lat_lng_range, start_city_lat + start_city_lat_lng_range)
        start_lng_query = "fq=start_longitude:[{0} TO {1}]".format(start_city_lng - start_city_lat_lng_range, start_city_lng + start_city_lat_lng_range)
        end_lat_query = "fq=end_latitude:[{0} TO {1}]".format(end_city_lat - end_city_lat_lng_range, end_city_lat + end_city_lat_lng_range)
        end_lng_query = "fq=end_longitude:[{0} TO {1}]".format(end_city_lng - end_city_lat_lng_range, end_city_lng + end_city_lat_lng_range)

        url  = "{0}/{1}/select?wt=json&rows=2147483647&{1}&{2}&{3}&{4}&{5}&{6}&{7}&{8}".format(SOLR_URL, SOLR_SEGMENT_CORE, q_query, start_date_query, end_date_query, start_lat_query, start_lng_query, end_lat_query, end_lng_query)
        r = requests.get(url)
        docs = r.json()['response']['docs']
        tmp = {}
        for doc in docs:
            tmp.setdefault(doc['phone_number'][0], []).append(doc['id'])
        result_entity = tmp
        total_result[index] = tmp

        #those who go LA to SE, has these phones and their start date is after end date of NY to LA
    else:
        if result_entity.keys():
            tmp = {}
            for entity in result_entity:
                q_query = "q={0}".format(entity)
                #start_date_query = "fq=start_date:[{0} TO *]".format(result_entity[entity])
                start_date_query = "fq=start_date:[{0} TO *]".format(start_date)
                end_date_query = "fq=end_date:[* TO {0}]".format(end_date)
                start_lat_query = "fq=start_latitude:[{0} TO {1}]".format(start_city_lat - start_city_lat_lng_range, start_city_lat + start_city_lat_lng_range)
                start_lng_query = "fq=start_longitude:[{0} TO {1}]".format(start_city_lng - start_city_lat_lng_range, start_city_lng + start_city_lat_lng_range)
                end_lat_query = "fq=end_latitude:[{0} TO {1}]".format(end_city_lat - end_city_lat_lng_range, end_city_lat + end_city_lat_lng_range)
                end_lng_query = "fq=end_longitude:[{0} TO {1}]".format(end_city_lng - end_city_lat_lng_range, end_city_lng + end_city_lat_lng_range)
                url  = "{0}/{1}/select?wt=json&&rows=2147483647&{1}&{2}&{3}&{4}&{5}&{6}&{7}&{8}".format(SOLR_URL, SOLR_SEGMENT_CORE, q_query, start_date_query, end_date_query, start_lat_query, start_lng_query, end_lat_query, end_lng_query)
                r = requests.get(url)
                docs = r.json()['response']['docs']
                for doc in docs:
                    tmp.setdefault(doc['phone_number'][0], []).append(doc['id'])
            result_entity = tmp
            total_result[index] = tmp

    return result_entity


def use_case_3(list_of_cities, list_of_latlons, start_date, end_date):
    result_entity = {}
    selected_cities_segments = []

    start_d = datetime.datetime.strptime(start_date, "%m/%d/%Y")
    start_d = start_d - dateutil.relativedelta.relativedelta(months=1)
    start_date = time.mktime(start_d.timetuple())

    end_d = datetime.datetime.strptime(end_date, "%m/%d/%Y")
    end_d = end_d + dateutil.relativedelta.relativedelta(months=1)
    end_date = time.mktime(end_d.timetuple())

    if list_of_cities:
        for index in range(len(list_of_cities)-1):
            city_name, start_city_lat_lng_range = list_of_cities[index].items()[0]
            r = requests.get(geocode_url.format(city_name))
            point = r.json()['results'][0]['geometry']['location']
            start_city_lat = point['lat']
            start_city_lng = point['lng']
            start_city_lat_lng_range = float(start_city_lat_lng_range)/69

            city_name, end_city_lat_lng_range = list_of_cities[index+1].items()[0]
            r = requests.get(geocode_url.format(city_name))
            point = r.json()['results'][0]['geometry']['location']
            end_city_lat = point['lat']
            end_city_lng = point['lng']
            end_city_lat_lng_range = float(end_city_lat_lng_range)/69

            selected_cities_segments.append([start_city_lat, start_city_lng, end_city_lat, end_city_lng])

            result_entity = query(index, start_date, end_date, start_city_lat, start_city_lng, start_city_lat_lng_range, end_city_lat, end_city_lng, end_city_lat_lng_range, result_entity)


    elif list_of_latlons:
        for index in range(len(list_of_latlons)-1):
            start_latlon, start_city_lat_lng_range = list_of_latlons[index].items()[0]
            start_city_lat = float(start_latlon.split(",")[0])
            start_city_lng = float(start_latlon.split(",")[1])
            start_city_lat_lng_range = float(start_city_lat_lng_range)/69

            end_latlon, end_city_lat_lng_range = list_of_latlons[index+1].items()[0]
            end_city_lat = float(end_latlon.split(",")[0])
            end_city_lng = float(end_latlon.split(",")[1])
            end_city_lat_lng_range = float(end_city_lat_lng_range)/69

            selected_cities_segments.append([start_city_lat, start_city_lng, end_city_lat, end_city_lng])

            result_entity = query(index, start_date, end_date, start_city_lat, start_city_lng, start_city_lat_lng_range, end_city_lat, end_city_lng, end_city_lat_lng_range, result_entity)

    return total_result, selected_cities_segments
