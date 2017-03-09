from flask import Flask, render_template, jsonify
import requests
import urllib
from collections import Counter
from operator import itemgetter

app = Flask(__name__, static_url_path='/static')

SOLR_URL = "http://localhost:8983/solr"
jquery = "static/js/jquery.js"
simple_sidebar = "static/css/simple-sidebar.css"
app_css = "static/css/app.css"
sub_domain = ""

@app.route("/routeclustering")
def routeclustering():
    url = "{0}/{1}/select?q=*%3A*&wt=json&indent=true&rows=2147483647".format(SOLR_URL, "test")
    r = requests.get(url)
    response = r.json()
    docs = response['response']['docs']
    cluster = []
    for doc in docs:
        points = []
        for i in range(0, len(doc['points']), 2):
                points.append([doc['points'][i], doc['points'][i+1]])
            #level here means number of common segments between routes
        cluster.append({"code":doc['code'], "points":points, "phone":str(doc['phone'][0]), "level":doc['level'][0]})


    url = "{0}/{1}/select?q=*%3A*&fl=code&wt=json&indent=true&facet=true&facet.field=code&rows=2147483647".format(SOLR_URL, "clustered_routes")
    r = requests.get(url)
    response = r.json()
    codes = response['facet_counts']['facet_fields']['code']
    num_codes = len(codes)
    all_codes = []
    for i in range(0, num_codes, 2):
        all_codes.append([codes[i], codes[i+1]])
    
    return render_template('routeclustering.html', jquery=jquery, simple_sidebar=simple_sidebar, app_css=app_css, cluster=cluster, all_codes=all_codes, sub_domain=sub_domain)



@app.route("/cityclustering")
@app.route("/cityclustering/<find_city_state>")
def cityclustering(find_city_state = None):
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
        all_cities.append({'city_state':city_state, 'size':size, "circle":{"coordinates":[location[0], location[1]]}})



    if find_city_state:
        city = find_city_state.split("-")[0].replace("_", " ")
        state = find_city_state.split("-")[1].replace("_", " ")

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

    return render_template('cityclustering.html', jquery=jquery, simple_sidebar=simple_sidebar, app_css=app_css, all_cities=all_cities, sub_domain=sub_domain)


@app.route("/concurrent_phone_viewer")
@app.route("/concurrent_phone_viewer/<start_end_date>/<end_range>",  methods=['GET', 'POST'])
@app.route("/concurrent_phone_viewer/query_one_phone/<phone>/<start_end_date>",  methods=['GET', 'POST'])
def concurrent_phone_viewer(start_end_date=None, end_range=100, phone=None):
    all_dates = []
    url = "{0}/{1}/select?q=*%3A*&fl=date&wt=json&indent=true&facet=true&facet.field=date".format(SOLR_URL, "raw_data")
    r = requests.get(url)
    response = r.json()
    dates = response['facet_counts']['facet_fields']['date']
    for i in range(0, len(dates), 2):
        all_dates.append(dates[i])


    end_range = int(end_range)
    if end_range == 100:
        start_range = 0
    else:
        start_range = end_range - 100
    if start_end_date and not phone:
        start_date = start_end_date.split("_")[0]
        end_date = start_end_date.split("_")[1]
        url = "{0}/{1}/select?q=*%3A*&fq=date%3D%5B%22{2}%22+TO+%22{3}%22%5D&wt=json&indent=true&rows=2147483647&fl=phone".format(SOLR_URL, "raw_data", start_date, end_date)
        r = requests.get(url)
        response = r.json()
        docs = response['response']['docs']
        t = []
        for doc in docs:
            t.append(doc['phone'][0])
        unique_phones = []
        tmp = Counter(t)
        for each in tmp:
            unique_phones.append([each, tmp[each]])
        unique_phones = sorted(unique_phones, key=itemgetter(1), reverse=True)
        return  jsonify({"unique_phones":unique_phones[start_range:end_range]})

    phone_location = []
    if phone and start_end_date:
        start_date = start_end_date.split("_")[0]
        end_date = start_end_date.split("_")[1]
        url = "{0}/{1}/select?q=*{2}*&fq=date%3D%5B%22{3}%22+TO+%22{4}%22%5D&wt=json&indent=true&rows=2147483647".format(SOLR_URL, "raw_data", phone, start_date, end_date)
        r = requests.get(url)
        response = r.json()
        docs = response['response']['docs']
        for doc in docs:
            phone_location.append({'phone':phone, "circle":{"coordinates":[doc['location'][0],doc['location'][1]]}})

        return  jsonify({"phone_location":phone_location})


    return render_template('concurrent_phone_viewer.html', jquery=jquery, simple_sidebar=simple_sidebar, app_css=app_css, all_dates=all_dates, phone_location=phone_location, sub_domain=sub_domain)


if __name__ == "__main__":
    app.run(port=5000, debug = True)
