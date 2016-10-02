#encoding=utf8
# -*- coding: gb2312 -*-

######################################################################################
#Python script for grabing fund data and do recommmandation based on defined pattern
#Python version: 2.7
#Owner: micerin@hotmail.com
#Git: https://github.com/micerin
#note -- gp=gupiao, hh=hunhe, zs=zhishu, zq=zhaiquan, ct=changnei
######################################################################################

import urllib2
import re
import csv
import string
import time
import datetime
import BeautifulSoup
import threadpool
from FindMaxMinMFromN import*
import smtplib
from email.mime.text import MIMEText

#global
urlTemp = 'http://fund.eastmoney.com/data/rankhandler.aspx?' \
          'op=ph&dt=kf&ft=%s&rs=&gs=0&sc=zzf&st=desc&sd=%s&ed=%s&qdii=&tabSubtype=,,,,,&pi=1&pn=%s&dx=1'
urlCtTemp = 'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=fb&ft=ct&rs=&gs=0&sc=zzf&st=desc&pi=1&pn=1000'

re_strforfund = r'(\"[^\"]+\"[,]?)'
re_pat = re.compile(re_strforfund)

#Utility function to calculate func excution time
def exeTime(func):
	def newFunc(*args, **args2):
		t0 = time.time()
		print "@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__)
		back = func(*args, **args2)
		print "@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__)
		print "@%.3fs taken for {%s}" % (time.time() - t0, func.__name__)
		return back
	return newFunc


@exeTime
#find out weekday and day which has max num of decrease for given time span
def getFundHistoryStatistics(fundcode, days):
    jjjzUrlTemp = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=%s&page=1&per=%d&sdate=&edate=%s'
    jjjzUrl = jjjzUrlTemp % (fundcode, days, etimeforhis)
    content = urllib2.urlopen(jjjzUrl).read()
    re_strforjjjz = r'<tr><td>([\d-]+)</td><td class=\'tor bold\'>([\d.]+)</td><td class=\'tor bold\'>([\d.]+)</td><td class=\'tor bold (\w{3,5})\'>(([\d.-]+)?\%)?</td>'
    re_patforjjjz = re.compile(re_strforjjjz)
    #todayDate = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))#'2016-04-03'

    flist = re.findall(re_patforjjjz, content)
    countForWeekday = dict()
    countForDay = dict()
    funddict = dict()

    week_day_dict = {
    0 : 'Monday',
    1 : 'Tuesday',
    2 : 'Wednesday',
    3 : 'Thursday',
    4 : 'Friday',
    5 : 'Saturday',
    6 : 'Sunday',
    }
    for item in flist:
        date = item[0]
        fundincrease = item[5]
        funddict[date] = fundincrease

    for i in range(0, 7):
        countForWeekday[i] = 0

    for i in range(0, 32):
        countForDay[i] = 0

    for item in funddict.keys():
        #print '%s %s' % (item, funddict[item])
        weekday = datetime.datetime.strptime(item,  '%Y-%m-%d').weekday()
        day =datetime.datetime.strptime(item,  '%Y-%m-%d').day
        if(string.atof(funddict[item]) < 0):
            countForWeekday[weekday] +=1
            countForDay[day] +=1

    dropmaxweekday = 0
    maxnum = 0
    for i in range(0, 7):
        print '%s %s' % (i, countForWeekday[i])
        if(countForWeekday[i] >= maxnum):
            dropmaxweekday = i
            maxnum = countForWeekday[i]

    dropmaxday = 0
    maxnum = 0
    for i in range(0, 32):
        print '%s %s' % (i, countForDay[i])
        if(countForDay[i] >= maxnum):
            dropmaxday = i
            maxnum = countForDay[i]

    print 'max drop weekday is %s' % week_day_dict[dropmaxweekday]
    print 'max drop day is %s' % dropmaxday
    print 'complete'






#Parameters
#Main calls
myfundlist = ['377010','270005','110029','590008','163406','161810','519113','162010', '166011','530018','161810','161017','320010', '100038', '040016']
daysearlier = 0
etimeforhis = (datetime.datetime.now() - datetime.timedelta(days=daysearlier)).strftime("%Y-%m-%d")
print '-------Start Analysis-------'
fundcode = '519977'
daystocheck = 750
getFundHistoryStatistics(fundcode, daystocheck)

print '-------Analysis Completed-------'

