#-*-coding:utf-8-*-
import urllib2
from PIL import Image
import cStringIO
import BeautifulSoup

def getCode(domain):
    print "Get code...."
    getcode_url="http://icp.alexa.cn/captcha.php?q="+domain+"&sid=0&icp_host=hncainfo"
    getcode_headers = {}
    getcode_headers['Referer']="http://icp.alexa.cn/captcha.php?q=163.com&sid=0&icp_host=hncainfo"
    getcode_headers['Cache-Control']="max-age=0"
    getcode_request = urllib2.Request(getcode_url,headers=getcode_headers)
    getcode_res = urllib2.urlopen(getcode_request).read()
    image = Image.open(cStringIO.StringIO( getcode_res))
    print "Get code succeeded"
    image.show()
def checkcode(domain,code):
    print "Begin check code..."
    checkcode_url = "http://icp.alexa.cn/index.php?q="+domain+"&code="+code+"&icp_host=hncainfo"
    checkcode_headers={}
    checkcode_headers['User-Agent']="Mozilla/5.0 (Windows NT 6.3; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0"
    checkcode_request = urllib2.Request(checkcode_url,headers=checkcode_headers)
    checkcode_res = urllib2.urlopen(checkcode_request).read()
    if(checkcode_res.count("主办单位名称")>0):
        print "Pass"
        checkcode_soup = BeautifulSoup.BeautifulSoup(checkcode_res)
        print "Agent name:"+checkcode_soup.findAll("table")[0].findAll("tr")[0].findAll("td")[1].text.encode("utf8")
    else:
        print "Fail"
domain = raw_input("Input domain:")
getCode(domain)
code = raw_input("Input code:")
checkcode(domain,code)