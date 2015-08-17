import requests
import json
from lxml import html
import re
import datetime
import csv
import urllib
import os

import current_url
import secret

url = "http://blog.aktualne.cz/"
r = requests.get(url)

dtnow = datetime.datetime.now()
dtutcnow = datetime.datetime.utcnow()
delta = dtnow - dtutcnow
hh,mm = divmod((delta.days * 24*60*60 + delta.seconds + 30) // 60, 60)
t = "%s%+03d:%02d" % (dtnow.isoformat(), hh, mm)

o = {"id":"blog_aktualne_cz", "date":t, "key": secret.key}
data = []
if r.status_code == requests.codes.ok:
    domtree = html.fromstring(r.content)
    a = domtree.xpath('//a[@class="clearfix"]/@href')[0]
    ass = domtree.xpath('//h2[@class="blogy-titulek"]/a/@href')
    ass = [a] + ass
    
    i = 1
    for a in ass:
        url = a
        print("downloading:"+url)
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            try:
                domtree = html.fromstring(r.content)
                dli = domtree.xpath('//small[@class="contentitemdate"]')[0].text.replace('.','').split(' ')
                nli = bytes(domtree.xpath('//small[@class="contentitemviewed"]')[0].text,'iso-8859-1').decode('utf-8').replace('.','').split(' ')
                item = {
                    'link': url,
                    'header': bytes(domtree.xpath('//h2[@class="nadpis-prispevku"]')[0].text,'iso-8859-1').decode('utf-8'),
                    'author': bytes(domtree.xpath('//meta/@content')[0],'iso-8859-1').decode('utf-8'),
                    'date': dli[2] + '-' + dli[1] + '-' + dli[0] + 'T' + dli[4] + ':00',
                    'total': nli[1],
                    'rank': i
                }
                data.append(item)
                i += 1
            except:
                o["status"] = "failed"
                o["message"] = "page:" + url + " " + r.status_code
        else:
            o["status"] = "failed"
            o["message"] = "page:" + url + " " + r.status_code
    dir = os.path.dirname("__file__")
    filename = os.path.join(dir, "data.csv")
    with open(filename,"a") as fout:
        csvw = csv.writer(fout)
        for r in data:
            csvw.writerow([r['header'],r['author'],r['total'],r['date'],r['rank'],r['link'],t])    
    o["status"] = "ok"
    o["message"] = "OK"

else:
    o["status"] = "failed"
    o["message"] = r.status_code

apiurl = urllib.parse.urljoin(current_url.url,'../www/api.php')
r = requests.get(apiurl,params=o) 

print(o)  
