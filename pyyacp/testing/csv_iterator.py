import os
import traceback

import datetime
import requests
import structlog
from collections import defaultdict
import time
log =structlog.get_logger()

odpwAPI="http://data.wu.ac.at/portalwatch/api/v1/"
datamonitorAPI="http://csvengine.ai.wu.ac.at/datamonitor/api/v1/"

base='sample_csvs'

def getCurrentSnapshot():
    now = datetime.datetime.now()
    y=now.isocalendar()[0]
    w=now.isocalendar()[1]
    sn=str(y)[2:]+'{:02}'.format(w)

    return sn

def getURLperPortal(odpwAPI,portal, snapshot, format):
    return odpwAPI+"portal/{}/{}/resources?format={}".format(portal, snapshot, format)

def getURLInfo(datamonitorAPI,url):
    return datamonitorAPI+"info/{}".format(url)

def url_iter(portalID, snapshot=getCurrentSnapshot()):
    requestURL = getURLperPortal(odpwAPI, portalID, snapshot, 'csv')
    log.info("ODPW", url=requestURL)
    res = requests.get(requestURL)
    log.info("ODPW", url=requestURL, status=res.status_code)

    if res.status_code == 200:
        data=res.json()
        log.info("ODPW SUCCESS", portal=portalID,snapshot=snapshot, format=format, urls=len(data))
        for url in data:
            yield url

def csvContent_iter(portalID, snapshot=getCurrentSnapshot(), useDatamonitor=False):
    urls=[url for url in url_iter(portalID, snapshot)]
    print len(urls)
    for url in urls:
        print url
        content=None
        if useDatamonitor:
            inforequestURL = getURLInfo(datamonitorAPI, url)
            info = requests.get(inforequestURL)
            log.info("DATAMONITOR SUCCESS", url=inforequestURL, status=info.status_code)
            if info.status_code == 200:
                data = info.json()
                print data
                if 'status' not in data or data['status'] == '404':
                    indexFromURL = True
            content=None

        if content:
            filename=cached(url, content)
        else:
            filename = cached(url)

        yield url, filename




def cached(uri, content=None):
    import hashlib
    m = hashlib.md5()
    m.update(uri)
    hashid= m.hexdigest()
    filename=os.path.join(base,hashid+".csv")
    if not os.path.isfile(filename):
        if not content:
            resp = requests.get(uri, stream=True)
            if resp.status_code == 200:
                content=resp.text
        if content:
            with open(filename, "wb") as handle:
                for data in resp.iter_content():
                    handle.write(data)
        else:
            return None

    return filename

