import requests
import json
import re
import datetime
import csv
import urllib
import os
import sys

import current_url
import secret

url = "https://docs.google.com/spreadsheets/d/1_S5qqXfo1RUkxD1NglRhlewQ2-Sk44S4YnxIi0Bvexs/pubchart?oid=400028519&format=interactive"
r = requests.get(url)

dtnow = datetime.datetime.now()
dtutcnow = datetime.datetime.utcnow()
delta = dtnow - dtutcnow
hh,mm = divmod((delta.days * 24*60*60 + delta.seconds + 30) // 60, 60)
t = "%s%+03d:%02d" % (dtnow.isoformat(), hh, mm)

print(os.path.dirname(sys.argv[0]))
print('dir',os.path.dirname(__file__))

o = {"id":"slobodnyvysielac-sk-donate", "date":t, "key": secret.key}
if r.status_code == requests.codes.ok:
    match1 = re.search('"},{"v":([0-9.]{1,})',r.text)
    match2 = re.search('],"max":([0-9.]{1,})',r.text)
    try:
        row = [
            match1.group(1),
            match2.group(1),
            t,
            url
        ]
        dirr = os.path.dirname(__file__)
        filename = os.path.join(dirr, "data.csv")
        with open(filename,"a") as fout:
            csvw = csv.writer(fout)
            csvw.writerow(row)

        o["status"] = "ok"
        o["message"] = "OK"
    except:
        o["status"] = "failed"
        o["message"] = "Wrong number of € values"
else:
    o["status"] = "failed"
    o["message"] = r.status_code

apiurl = urllib.parse.urljoin(current_url.url,'../www/api.php')
r2 = requests.get(apiurl,params=o)

print(o)
