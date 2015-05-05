import requests
import secret
from lxml import html
import csv
import re
import datetime
import urllib

v2c = {} #column number <- variable
existing = {}
i = 0
with open("data.csv") as fin:
    csvr = csv.reader(fin)
    for row in csvr:
        if i == 0:
            j = 0
            for item in row:
                v2c[item] = j
                j += 1
        else:
            try:
                existing[row[v2c['code']]]
            except:
                existing[row[v2c['code']]] = {}    
            existing[row[v2c['code']]][row[v2c['date']]] = True
        i += 1

url = "http://www.darcovskasms.cz/nno/prehled-pro-nno.html"

params = {
  "login": secret.nno_login,
  "pass": secret.nno_pass,
  "logmeplease": secret.nno_logmeplease
}
headers = {
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:37.0) Gecko/20100101 Firefox/37.0',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.5',
    'accept-encoding': 'gzip, deflate',
    'referer': 'http://www.darcovskasms.cz/nno/prehled-pro-nno.html'
}
cookies = {
    "userdms":"NWQzMmI1MS8xNzg1ZjU3YDhkZC9lYzMzNDU3ZTpgNTQ8Ojw%3D"
}
r = requests.post(url, data = params, headers = headers, cookies=cookies)
    #note: not sure what works; do not know how to get the cookie
    
    
dtnow = datetime.datetime.now()
dtutcnow = datetime.datetime.utcnow()
delta = dtnow - dtutcnow
hh,mm = divmod((delta.days * 24*60*60 + delta.seconds + 30) // 60, 60)
t = "%s%+03d:%02d" % (dtnow.isoformat(), hh, mm)
o = {"id":"darcovskasms_cz", "date":t, "key": secret.key}

campaigns = []

if r.status_code == requests.codes.ok:
    domtree = html.fromstring(r.content)
    trs = domtree.xpath('//table/tr')
    if len(trs) > 0:
        for i in range(1,len(trs)):
            tds = trs[i].xpath('td')
            campaign = {
                "project": tds[0].xpath('a')[0].text,
                "organization": tds[1].text,
                "code": tds[2].xpath('strong/a')[0].text,
                "link": tds[2].xpath('strong/a/@href')[0]
            }
            campaigns.append(campaign)

    
        for campaign in campaigns:
            nrows = []
            url = "http://www.darcovskasms.cz" + campaign['link']
            print("downloading:"+url)
            r = requests.post(url, data = params, headers = headers, cookies=cookies)
            if r.status_code == requests.codes.ok:
                domtree = html.fromstring(r.content)
                trs = domtree.xpath('//table/tr')
                for tr in trs:
                    tds = tr.xpath('td')
                    if len(tds) > 0:
                        match = re.search("([0-9]{2}).([0-9]{2}).\ ([0-9]{4})",tds[0].text)
                        date = match.group(3)+'-'+match.group(2)+'-'+match.group(1)
                        code = tds[1].text.replace(' ','').replace('DMS','')
                        try:
                            existing[code][date]
                        except:
                            nrow = campaign.copy()
                            nrow['date'] = date
                            nrow['dms'] = tds[2].text.replace(' ','').replace('dms','')
                            match = re.search("([0-9]{1,})",domtree.xpath('//h3')[1].text)
                            nrow['total'] = match.group(1)
                            nrows.append(nrow)
                with open("data.csv","a") as fout:
                    csvw = csv.writer(fout)
                    for r in nrows:
                        csvw.writerow([r['project'],r['organization'],r['code'],r['link'],r['date'],r['dms'],r['total'],t])
            else:
                o["status"] = "failed"
                o["message"] = "page:" + campaign.link + " " + r.status_code
    
    else:
        o["status"] = "failed"
        o["message"] = "first page: no table"
else:
    o["status"] = "failed"
    o["message"] = "first page:" + r.status_code
apiurl = urllib.parse.urljoin(current_url.url,'../www/api.php')
r = requests.get(apiurl,params=o) 

print(o)
