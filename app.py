from flask import Flask, render_template, jsonify
import requests
import json
import urllib

app = Flask(__name__, static_url_path='/static')

SOLR_URL = "http://localhost:8983/solr"


def query_solr(url):
    r = requests.get(url)
    response = r.json()
    docs = response['response']['docs']
    features = {"features": []}
    for doc in docs:
        date = eval(doc['date'][0])
        num_dates = len(date)
        for doc_date in range(num_dates):
            if num_dates == 1:
                location = [eval(doc["location"][0].encode())]
            else:
                location = eval(doc["location"][0].encode())
            features["features"].append({ "type": "Feature", "properties": { "id": doc["phone"][0].encode() , "date": date[doc_date], "num_date": doc["num_date"]}, "geometry": { "type": "Point", "coordinates": location[doc_date]}} )

    return str(features).replace("'", '"')

#list of static files
jquery = "static/js/jquery.js"
simple_sidebar = "static/css/simple-sidebar.css"
app_css = "static/css/app.css"

@app.route("/")
@app.route("/phonelocator")
def index():
    '''
    Index page
    '''
    url = "{0}/{1}/select?q=*%3A*&wt=json&indent=true&sort=num_date+desc&rows=2147483647".format(SOLR_URL, "core_name")
    features = query_solr(url)

    return render_template('phonelocator.html', features=features, jquery=jquery, simple_sidebar=simple_sidebar, app_css=app_css)

# @app.route("/<keyword>")
# def search(keyword):
#     '''
#     Search page
#     '''
#     url = "{0}/{1}/select?q=phone:*{2}*&wt=json&indent=true&sort=num_date+desc&rows=2147483647".format(SOLR_URL, CORE_NAME, keyword)
#     features = query_solr(url)
# 
#     return render_template('phonelocator.html', features=features, jquery=jquery, simple_sidebar=simple_sidebar, app_css=app_css)


@app.route("/routeclustering")
def routeclustering():
    data = "static/data/"
    url = "{0}/{1}/select?q=*%3A*&wt=json&indent=true&rows=2147483647".format(SOLR_URL, "clustered_routes")
    r = requests.get(url)
    response = r.json()
    docs = response['response']['docs']
    cluster = []
    for doc in docs:
        cluster.append({"code":doc['code'], "lat1":str(doc['start_lat'][0]), "lon1":str(doc['start_lon'][0]), "lat2":str(doc['end_lat'][0]), "lon2":str(doc['end_lon'][0]), "phone":str(doc['phone'][0])})

    url = "{0}/{1}/select?q=*%3A*&fl=code&wt=json&indent=true&facet=true&facet.field=code&rows=2147483647".format(SOLR_URL, "clustered_routes")
    r = requests.get(url)
    response = r.json()
    codes = response['facet_counts']['facet_fields']['code']
    num_codes = len(codes)
    all_codes = []
    for i in range(0, num_codes, 2):
        all_codes.append([codes[i], codes[i+1]])
    
    return render_template('routeclustering.html', jquery=jquery, simple_sidebar=simple_sidebar, app_css=app_css, data=data, cluster=cluster, all_codes=all_codes)



@app.route("/cityclustering")
def cityclustering():
    data = "static/data/"

    url = "{0}/{1}/select?q=*%3A*&fl=city_state%2Clocation&wt=json&indent=true&facet=true&facet.field=city_state&rows=2147483647".format(SOLR_URL, "raw_data")
    r = requests.get(url)
    response = r.json()
    all_city_state = {}
    docs = response['response']['docs']
    for doc in docs:
        all_city_state[doc['city_state'][0]] = doc['location']

    all_cities = []
    city_state_size = response['facet_counts']['facet_fields']['city_state']
    for i in range(0, len(city_state_size), 2):
        city_state = city_state_size[i]
        size = city_state_size[i+1]
        location = all_city_state[city_state]
        city_state = city_state.replace(" ","_").replace(",","-")
        all_cities.append({'city_state':city_state, 'size':size, 'lat':location[0], 'lon':location[1]})

    return render_template('cityclustering.html', jquery=jquery, simple_sidebar=simple_sidebar, app_css=app_css, data=data, all_cities=all_cities) # phones=phones,

@app.route("/find_route/<city_state>")
def find_route(city_state):
    '''
    '''
    city = city_state.split("-")[0].replace("_", " ")
    state = city_state.split("-")[1].replace("_", " ")

    url = "{0}/{1}/select?q=*%3A*&fq=city%3A%22{2}%22&fq=state%3A%22{3}%22&wt=json&indent=true&rows=2147483647".format(SOLR_URL, "raw_data", city, state)
    r = requests.get(url)
    response = r.json()
    docs = response['response']['docs']
    all_phones = {}
    for doc in docs:
        all_phones.setdefault(doc['phone'][0], []).append(doc['date'][0])

    tmp_phones = {}
    range_num = 400 
    num_all_phones = len(all_phones.keys())
    all_phones_range = range(0 , num_all_phones , range_num)
    for i in all_phones_range:
        tmp = []
        for each in all_phones.keys()[i:i+range_num]:
            tmp.append(urllib.quote_plus('"' + each + '"'))
        url = "{0}/{1}/select?q=*%3A*&fq=phone%3A{2}&wt=json&indent=true&rows=2147483647".format(SOLR_URL, "raw_data", ("").join(tmp))
        r = requests.get(url)
        response = r.json()
        docs = response['response']['docs']
        for doc in docs:
            tmp_phones.setdefault(doc['phone'][0], []).append({"city": doc['city'][0], "country":doc['country'][0], "city_state":doc['city_state'][0], "state":doc['city'][0], "location":doc['location'], "date":doc['date'][0]})
    phones = []
    found_phones = []
    for i, phone in enumerate(all_phones):
        data = tmp_phones[phone]
        if len(data) >= 2:
            for d in all_phones[phone]:
                tmp_date = []
                for each in tmp_phones[phone]:
                    tmp_date.append(each['date'])
                city_phone_index = tmp_date.index(d)
                if city_phone_index == 0:
                    status = "from"
                    city = data[0]['city']
                    phones.append({"code":'a'+str(i), "lat1":str(data[0]['location'][0]), "lon1":str(data[0]['location'][1]), "lat2":str(data[1]['location'][0]),
                               "lon2":str(data[1]['location'][1]), "phone":phone, "status":status})
                    found_phones.append([{'phone': phone, 'date':d, 'status': status}])
                else:
                    status = "to"
                    city = data[city_phone_index]['city']
                    phones.append({"code":'a'+str(i), "lat1":str(data[city_phone_index]['location'][0]), "lon1":str(data[city_phone_index]['location'][1]), "lat2":str(data[city_phone_index - 1]['location'][0]),
                               "lon2":str(data[city_phone_index - 1]['location'][1]), "phone":phone, "status":status})
                    found_phones.append([{'phone': phone, 'date':d, 'status': status}])
                    try:
                        status = "from"
                        city = data[city_phone_index]['city']
                        phones.append({"code":'a'+str(i), "lat1":str(data[city_phone_index]['location'][0]), "lon1":str(data[city_phone_index]['location'][1]), "lat2":str(data[city_phone_index + 1]['location'][0]),
                               "lon2":str(data[city_phone_index + 1]['location'][1]), "phone":phone, "status":status})
                        found_phones.append([{'phone': phone, 'date':d, 'status': status}])
                    except:
                        pass

    return jsonify({"phones":phones, "found_phones":found_phones, "city":city})

if __name__ == "__main__":
    app.run(port=5000, debug = True)
