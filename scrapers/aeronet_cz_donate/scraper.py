import requests
import json
from lxml import html
import re
import datetime
import csv
import urllib

import current_url
import secret

url = "http://aeronet.cz/news/category/z-domova/"
r = requests.get(url)

dtnow = datetime.datetime.now()
dtutcnow = datetime.datetime.utcnow()
delta = dtnow - dtutcnow
hh,mm = divmod((delta.days * 24*60*60 + delta.seconds + 30) // 60, 60)
t = "%s%+03d:%02d" % (dtnow.isoformat(), hh, mm)

o = {"id":"aeronet_cz_donate", "date":t, "key": secret.key}
if r.status_code == requests.codes.ok:
    domtree = html.fromstring(r.text)
    p = domtree.xpath('//p[@class="progress-sidebar"]')[0].text
    matches = re.findall("€[+-]?[0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})",p)
    if len(matches) == 2:
        row = [
            matches[0][1:].replace(',',''),
            matches[1][1:].replace(',',''),
            t,
            url
        ]
        with open("data.csv","a") as fout:
            csvw = csv.writer(fout)
            csvw.writerow(row)
            
        o["status"] = "ok"
        o["message"] = "OK"
    else:
        o["status"] = "failed"
        o["message"] = "Wrong number of € values"
else:
    o["status"] = "failed"
    o["message"] = r.status_code

apiurl = urllib.parse.urljoin(current_url.url,'../www/api.php')
r = requests.get(apiurl,params=o) 

print(o)  
