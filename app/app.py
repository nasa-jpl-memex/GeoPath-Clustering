from flask import Flask, render_template, jsonify, request
import requests
import datetime
from ConfigParser import SafeConfigParser

from scripts.use_case_2 import use_case_2
from scripts.use_case_3 import use_case_3
from scripts.use_case_4 import use_case_4

app = Flask(__name__, static_url_path='/static')


conf_parser = SafeConfigParser()
conf_parser.read('config.txt')

FLASK_HOST = conf_parser.get('general', 'FLASK_HOST')
FLASK_PORT = conf_parser.get('general', 'FLASK_PORT')
SOLR_URL = conf_parser.get('general', 'SOLR_URL')
SOLR_AD_POINTS_CORE = conf_parser.get('general', 'SOLR_AD_POINTS_CORE')
SOLR_SEGMENT_CORE = conf_parser.get('general', 'SOLR_SEGMENT_CORE')
SUBDOMAIN = conf_parser.get('general', 'SUBDOMAIN')

jquery = "static/js/jquery.js"
simple_sidebar = "static/css/simple-sidebar.css"
app_css = "static/css/app.css"




#to get first and last date
min_date = 883728000.0
max_date = 1492844400.0
all_dates = []
url  = "{0}/{1}/select?q=*%3A*&wt=json&fl=date&rows=2147483647".format(SOLR_URL, SOLR_AD_POINTS_CORE)
# r = requests.get(url)
# docs = r.json()['response']['docs']
# for doc in docs:
#     if doc['date'][0] not in all_dates:
#         all_dates.append(doc['date'][0])
# min_date = min(all_dates)
# max_date = max(all_dates)

min_date = datetime.datetime.fromtimestamp(int(min_date)).strftime('%m/%d/%Y')
max_date = datetime.datetime.fromtimestamp(int(max_date)).strftime('%m/%d/%Y')

@app.route("/")
def index():
    return render_template('index.html', app_css=app_css, sub_domain=SUBDOMAIN)

@app.route("/routeclustering/search", methods=['GET', 'POST'])
@app.route("/routeclustering")
def routeclustering():
    cluster = []
    selected_cities_segments = []
    j = request.get_json()
    if j:
        if "cities" in j:
            entity_found_tmp = {}
            results, selected_cities_segments = use_case_3(j['cities'], None, j['start_date'], j['end_date'])
        if "latlon" in j:
            entity_found_tmp = {}
            results, selected_cities_segments = use_case_3(None, j['latlon'], j['start_date'], j['end_date'])
        for each in results:
            for entity in results[each]:
                if entity in entity_found_tmp:
                    entity_found_tmp[entity] += 1
                else:
                    entity_found_tmp[entity] = 1
                for segment_id in results[each][entity]:
                    url  = "{0}/{1}/select?q=*%3A*&fq=id%3A{2}&wt=json&indent=true&rows=2147483647".format(SOLR_URL, SOLR_SEGMENT_CORE, segment_id)
                    r = requests.get(url)
                    docs = r.json()['response']['docs']
                    for doc in docs:
                        cluster.append({"id":str(doc['id']), \
                                    "code":str(doc['phone_number'][0]), \
                                    "points":[[str(doc['start_longitude'][0]), str(doc['start_latitude'][0])],[str(doc['end_longitude'][0]), str(doc['end_latitude'][0])]], \
                                    "phone":str(doc['phone_number'][0]), \
                                    "start_city":str(doc['start_city'][0]), \
                                    "end_city":str(doc['end_city'][0]), \
                                    "start_date":datetime.datetime.fromtimestamp(int(doc['start_date'][0])).strftime('%Y-%m-%d'), \
                                    "end_date":datetime.datetime.fromtimestamp(int(doc['end_date'][0])).strftime('%Y-%m-%d')
                                    })
        for each in selected_cities_segments:
            cluster.append({"phone":str("selected_cities"), \
                            "points":[[str(each[1]), str(each[0])],[str(each[3]), str(each[2])]], \
                            })
        entity_found = []
        for each in entity_found_tmp:
            entity_found.append([each, entity_found_tmp[each]])
        entity_found.sort(key=lambda x: x[1], reverse=True)
        return jsonify({'entity_found':entity_found, "cluster" :cluster}), 200
    else:
        return render_template('routeclustering.html', app_css=app_css, cluster=cluster, sub_domain=SUBDOMAIN, min_date=min_date, max_date=max_date)



@app.route("/cityreport/query", methods=['GET', 'POST'])
@app.route("/cityreport")
def city_report():
    cities_found = []
    j = request.get_json()
    if j:
        city_found, segments, entities_found = use_case_4( j['city'], j['start_date'], j['end_date'], j['radius']) #"Denver", "01/01/2015", "10/01/2015")
        for key, value in city_found.items():
            lat = key.split("_")[0]
            lon = key.split("_")[1]
            city_name = value['city_name']
            in_goings = value['in']
            out_goings = value['out']
            cities_found.append({'lat':lat, \
                                'lon': lon, \
                                'city_name': city_name, \
                                'in_goings': in_goings, \
                                'out_goings': out_goings
                                })
        tmp = []
        for key, value  in entities_found.items():
            tmp.append([key, value['in'], value['out']])
        entities_found = tmp

        return jsonify({'cities_found':cities_found, 'segments':segments, 'entities_found':entities_found}), 200
    else:
        return render_template('cityreport.html', app_css=app_css, sub_domain=SUBDOMAIN, min_date=min_date, max_date=max_date)


@app.route("/concurrent_phone_viewer/query", methods=['GET', 'POST'])
@app.route("/concurrent_phone_viewer")
def concurrent_phone_viewer():
    entities_found = []
    j = request.get_json()
    if j:
        results = use_case_2(j['start_date'], j['end_date'], j['phone_number']) #"Denver", "01/01/2015", "10/01/2015")
        for key, value in results.items():
            entities_found.append([key, value['count'], value['locations']])

        entities_found.sort(key=lambda x: x[1], reverse=True)

        return jsonify({'entities_found':entities_found, 'results':results}), 200
    else:
        return render_template('concurrent_phone_viewer.html', app_css=app_css, sub_domain=SUBDOMAIN, min_date=min_date, max_date=max_date)

if __name__ == "__main__":
    flask_port = int(FLASK_PORT)
    app.run(host=FLASK_HOST, port=flask_port, debug = True)
