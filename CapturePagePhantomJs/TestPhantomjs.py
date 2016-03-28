#encoding=utf8

import subprocess

def getDom(url):
    cmd = r'C:\Users\t-jizh\Downloads\phantomjs-2.1.1-windows\bin\phantomjs.exe constructionDom.js "%s"'%url
    print "cmd:", cmd
    stdout,stderr = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    print stderr
    return stdout

targetUrl = 'www.yahoo.com'
getDom(targetUrl)