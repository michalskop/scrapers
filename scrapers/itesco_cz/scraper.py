import requests
from lxml import html
import datetime
import csv
import json
import urllib
import os

import current_url
import secret

def t():
    dtnow = datetime.datetime.now()
    dtutcnow = datetime.datetime.utcnow()
    delta = dtnow - dtutcnow
    hh,mm = divmod((delta.days * 24*60*60 + delta.seconds + 30) // 60, 60)
    t = "%s%+03d:%02d" % (dtnow.isoformat(), hh, mm)
    return t

def decode_some_html(text):
    text = text.replace("Ä\x8c","Č")
    text = text.replace("Ä\x8d","č")
    text = text.replace("Ä\x8e","Ď")
    text = text.replace("Ä\x8f","ď")
    text = text.replace("Ä\x9a","Ě")
    text = text.replace("Ä\x9b","ě")
    text = text.replace("Å\x88","ň")
    text = text.replace("Å\x87","Ň")
    text = text.replace("Å\x99","ř")
    text = text.replace("Å\x98","Ř")
    text = text.replace("Å\xa0","Š")
    text = text.replace("Å\xa1","š")
    text = text.replace("Å\xa4","Ť")
    text = text.replace("Å\xa5","ť")
    text = text.replace("Å\xae","Ů")
    text = text.replace("Å\xaf","ů")
    text = text.replace("Å\xbd","Ž")
    text = text.replace("Å\xbe","ž")
    return text

def single_page(domtree):
    products = []
    div = domtree.xpath('//div[@id="listedProductItems"]')[0]
    lis = div.xpath('ul/li')
    for li in lis:
        product = {}
        product['name'] = decode_some_html(li.xpath('div/div/div/h2/a/@title')[0])
        product['link'] = li.xpath('div/div/div/h2/a/@href')[0]
        full_price = decode_some_html(li.xpath('div/div/div/div/form/div/p/span')[0].text)
        product['price'] = full_price.replace('Kč','').strip().replace(',','.').replace(u"\u00A0","")
        full_unit_price = decode_some_html(li.xpath('div/div/div/div/form/div/p/span')[1].text).strip()
        up = full_unit_price.split(' ')
        product['unit_price'] = up[0].strip('(').replace(',','.').replace(u"\u00A0","")
        product['unit'] = up[1].strip(')').replace('Kč','').strip('/')
        idd = product['link'].split('/')
        product['id'] = idd[len(idd)-1]
        promo = li.xpath('div/div/div/div[@class="promo"]/p[@class="promoMsg"]')
        if len(promo) > 0:
            product['promo'] = decode_some_html(promo[0].text.strip())
        else:
            product['promo'] = ''
        
        products.append(product)

    return products

o = {"id":"itesco_cz", "date":t, "key": secret.key}
today = datetime.datetime.now().strftime("%Y-%m-%d")
last = "?"



try:
    url = "http://nakup.itesco.cz/cs-CZ/"
    last = url
    r = requests.get(url)
    print("downloaded: " + url)

    i = 0

    domtree = html.fromstring(r.content)
    ass = domtree.xpath('//div[@id="secondaryNavWrapper"]/div/ul/li/a/@href')
    groups = domtree.xpath('//div[@id="secondaryNavWrapper"]/div/ul/li/a/text()')
    
    
    for a in ass:
        url = "http://nakup.itesco.cz" + a
        r = requests.get(url)
        print("downloaded: " + url)
        last = url
        domtree = html.fromstring(r.content)
        h3as = domtree.xpath('//h3/a')
        uls = domtree.xpath('//ul[@class="navigation"]')
        j = 0
        
        for ul in uls[2:]:
            products = []
            lias = ul.xpath('li/a')
            for lia in lias:
                url = "http://nakup.itesco.cz" + lia.xpath('@href')[0]
                r = requests.get(url)
                print("downloaded: " + url)
                last = url
                category_link = lia.xpath('@href')[0]
                category = lia.text.strip()
                domtree = html.fromstring(r.content)
                products.append(single_page(domtree))
                
                
                if r.text.count("pageNo") > 1:
                    for pn in range(2,int((r.text.count("pageNo")-1)/2+1)):
                        url = "http://nakup.itesco.cz" + lia.xpath('@href')[0] + "&sortBy=Default&pageNo=" + str(pn)
                        r = requests.get(url)
                        print("downloaded: " + url)
                        last = url
                        
                        domtree = html.fromstring(r.content)
                        product = single_page(domtree)
                        products.append(product)
                        
                
                
                
                dir = os.path.dirname("__file__")
                filename = os.path.join(dir, "data.csv")
                with open(filename,"a") as fout:
                    csvw = csv.writer(fout)
                    for page in products:
                        for r in page:
                            csvw.writerow([
                                r['id'],
                                decode_some_html(groups[i]),
                                a,
                                #h3as[j].text.strip(),  #two columns in html without structure <h3><div>
                                #h3as[j].xpath('@href')[0],
                                category,
                                category_link,
                                r['name'],
                                r['link'],
                                r['price'],
                                r['unit_price'],
                                r['unit'],
                                today,
                                t(),
                                r['promo']
                            ])    
                o["status"] = "ok"
                o["message"] = "OK"      
                #raise(Exception)
                    
            
            j += 1
        i += 1

except:
    o["status"] = "failed"
    o["message"] = last


apiurl = urllib.parse.urljoin(current_url.url,'../www/api.php')
r = requests.get(apiurl,params=o) 

print(o) 
