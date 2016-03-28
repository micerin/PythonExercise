import urllib
import json
import socket
socket.setdefaulttimeout(10)
proxys = []
proxys.append({"http":"http://121.42.195.145:808"})
proxys.append({"http":"http://115.160.137.178:8088"})
baseid = 315681

for id in range(0,15,1):
    try:
        url = "http://chanyouji.com/api/trips/"+`(baseid+id)`+".json"
        res = urllib.urlopen(url,proxies=proxys[1]).read()
        res_json = json.loads(res)
        print res_json['name']
    except Exception,e:
        print e
        continue