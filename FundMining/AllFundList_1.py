#encoding=utf8
# -*- coding: gb2312 -*-

######################################################################################
#Python script for grabing fund data and do recommmandation based on defined pattern
#Python version: 2.7
#Owner: micerin@hotmail.com
#Git: https://github.com/micerin
#note -- gp=gupiao, hh=hunhe, zs=zhishu, zq=zhaiquan
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

urlTemp = 'http://fund.eastmoney.com/data/rankhandler.aspx?' \
          'op=ph&dt=kf&ft=%s&rs=&gs=0&sc=zzf&st=desc&sd=%s&ed=%s&qdii=&tabSubtype=,,,,,&pi=1&pn=%s&dx=1'
re_strforfund = r'(\"[^\"]+\"[,]?)'
re_pat = re.compile(re_strforfund)

#Class for fund
class Fund:
    def __init__(self):
        self.fundcode = ''
        self.name = ''
        self.latestvalue = ''
        self.overallvalue = ''
        self.latestdelta = ''
        self.weekdelta = ''
        self.monthdelta = ''
        self.threemonthdelta = ''
        self.halfyeardelta = ''
        self.yeardelta = ''
        self.twoyeardelta = ''
        self.threeyeardelta = ''
        self.thisyear = ''
        self.fromstartup = ''
        self.starttime = ''

        #customized properties
        self.weighted = ''
        self.managerperf = ''
        self.managerduration = ''
        self.highlyranked = False
        self.buyable = False
        self.maxdelta = ''
        self.maxdeltaindex = -1
        self.eventday = ''
        self.action = 0

class FundValue:
    def __init__(self):
        self.date = ''
        self.value = ''
        self.oavalue = ''
        self.dayincrease = ''

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

#Get fund list per filter
def getFundList(filter):
    url = urlTemp % filter
    content = urllib2.urlopen(url).read()
    return content

#Parse fund list info from given content
def parseFundList(content, savefile, filecsv):
    flist = re.findall(re_pat, content)
    print '%d funds for %s in total' % (len(flist),typeFilter)

    if savefile:
        saveAsCsv(flist, filecsv) # save all fund info to csv file

    fundinfolist = []
    for i in range(0,len(flist)):
        isplits = string.split(flist[i], ',')
        if(len(isplits) > 0):
            fund = Fund()
            fund.fundcode =isplits[0][1:]
            fund.name = isplits[1]
            fund.latestvalue = isplits[4]
            fund.overallvalue = isplits[5]
            fund.latestdelta = isplits[6]
            fund.weekdelta = isplits[7]
            fund.monthdelta = isplits[8]
            fund.threemonthdelta = isplits[9]
            fund.halfyeardelta = isplits[10]
            fund.yeardelta = isplits[11]
            fund.twoyeardelta = isplits[12]
            fund.threeyeardelta = isplits[13]
            fund.thisyear = isplits[14]
            fund.fromstartup = isplits[15]
            fund.starttime = isplits[16]
            fundinfolist.append(fund)

    #get overall data for all funds, all kinds
    #re_strforall = r'allNum:(.*),gpNum:(.*),hhNum:(.*),zqNum:(.*),zsNum:(.*),bbNum:(.*),qdiiNum:(.*),etfNum:(.*),lofNum:(.*)'
    #re_patforall = re.compile(re_strforall)
    index = string.index(content, 'allNum:')
    print content[index:-2]
    return fundinfolist

#Save fund items to csv file
def saveAsCsv(flist, file):
    csvfiletowrite = open(file ,'wb')
    spamwriter = csv.writer(csvfiletowrite, delimiter=',', quotechar='|')#, quoting=csv.QUOTE_MINIMAL)
    result=[]

    for item in flist:
        isplits = string.split(item, ',')
        if(len(isplits) > 0): # fund code
            isplits[0] = isplits[0][1:]
        for sitem in isplits:
            if sitem !='"': #sitem != '' and
                result.append(sitem)

        spamwriter.writerow(result)
        result = []
    csvfiletowrite.close()

#Check latest fund rank >=4
def isHighlyRanked(fund):
    rankUrlTemp = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=grade&code=%s&page=1&per=1'
    rankUrl = rankUrlTemp % fund.fundcode
    content = urllib2.urlopen(rankUrl).read()
    if '\'4\'' in content or '\'5\'' in content:
        fund.highlyranked = True

#Get manager perf for given fund item
def getManagerPerf(funditem):
    jjjllinkTemp = 'http://fund.eastmoney.com/f10/jjjl_%s.html'
    jjjllink = jjjllinkTemp % funditem.fundcode
    i = 0
    retrytimes= 10
    for i in range(0,retrytimes):#retry 4 times at most since sometimes the page load return null result...
        # utf-8 or gb2312 or gbk
        try:
            soup = BeautifulSoup.BeautifulSOAP(urllib2.urlopen(jjjllink).read().decode('gb2312').encode('utf8'))
        except:
            try:
                soup = BeautifulSoup.BeautifulSOAP(urllib2.urlopen(jjjllink).read().decode('gbk').encode('utf8'))
            except:
                soup = BeautifulSoup.BeautifulSOAP(urllib2.urlopen(jjjllink).read())
        table = soup.find('table', attrs={'class':'w782 comm jlchg'})
        if len(table.contents[1].contents) > 0:
            funditem.managerperf = table.contents[1].contents[0].contents[4].contents[0][0:-1]
            funditem.managerduration = table.contents[1].contents[0].contents[3].contents[0]
            #print table.contents[1].contents[0].contents[0].contents[0]
            break
        i+=1

    if i == retrytimes:#hit here after retrytimes times try, should indicate no manager change, get fromstartup
        funditem.managerperf = funditem.fromstartup
        funditem.managerduration = 'start @' + funditem.starttime
        #funditem.managerperf = '0' #default 0
    return funditem

#Check if fund buyable
def isBuyable(fund):
    fundlinkTemp = 'http://fund.eastmoney.com/%s.html'
    fundlink = fundlinkTemp % fund.fundcode
    # utf-8 or gb2312 or gbk
    try:
        soup = BeautifulSoup.BeautifulSOAP(urllib2.urlopen(fundlink).read())
    except:
        try:
            soup = BeautifulSoup.BeautifulSOAP(urllib2.urlopen(fundlink).read().decode('gb2312').encode('utf8'))
        except:
            soup = BeautifulSoup.BeautifulSOAP(urllib2.urlopen(fundlink).read().decode('gbk').encode('utf8'))
    buyNow = soup.find(id='buyNowStatic')

    #<a id="buyNowStatic" class="buyNowStatic unbuy" href="javascript:;" target="_self">立即购买</a>
    #<a id="buyNowStatic" class="buyNowStatic" href="https://trade.1234567.com.cn/FundtradePage/default2.aspx?fc=162010&amp;spm=pzm" target="_blank">立即购买</a>
    if 'trade' in dict(buyNow.attrs)['href']:
        fund.buyable = True

#Get fund history value
def getFundvalueHis(fundcode, days):
    jjjzUrlTemp = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=%s&page=1&per=%d&sdate=&edate=%s'
    jjjzUrl = jjjzUrlTemp % (fundcode, days, etimeforhis)
    content = urllib2.urlopen(jjjzUrl).read()
    re_strforjjjz = r'<tr><td>([\d-]+)</td><td class=\'tor bold\'>([\d.]+)</td><td class=\'tor bold\'>([\d.]+)</td><td class=\'tor bold (\w{3,5})\'>(([\d.-]+)?\%)?</td>'
    re_patforjjjz = re.compile(re_strforjjjz)

    flist = re.findall(re_patforjjjz, content)
    fundValueList = []
    for item in flist:
        dayfund = FundValue()
        dayfund.date = item[0]
        dayfund.value = item[1]
        dayfund.oavalue = item[2]
        dayfund.dayincrease = item[5]
        fundValueList.append(dayfund)
    return fundValueList

#Check max delta for given fund
def maxDropOrIncrease(fund):
    fundValueList = getFundvalueHis(fund.funcode, workingdays)

    if checkdrop:
        fund.maxdelta, fund.maxdeltaindex =  GetMinMFromN(fundValueList, deltadays)
    else:
        fund.maxdelta, fund.maxdeltaindex =  GetMaxMFromN(fundValueList, deltadays)
    fund.eventday = fundValueList[fund.maxdeltaindex].date
    #print '%.3f %s %s' % (fund.maxdelta, fund.fundcode, fund.eventday)

#Get fund perf for delta action days to determine action
def getPerfForFund(fund):
    fundValueList = getFundvalueHis(fund.fundcode, deltadaysforaction)
    fundlinkTemp = 'http://fund.eastmoney.com/%s.html'
    fundurl = fundlinkTemp % fund.fundcode
    print '  %s %s' % (fundurl, fundValueList[0].dayincrease)
    if string.atof(fundValueList[0].dayincrease) > 0:
        value = GetMaxFromM(fundValueList,deltadaysforaction)
        if value > upthreshold:
            fund.action = 1
    elif string.atof(fundValueList[0].dayincrease) < 0:
         value = GetMinFromM(fundValueList,deltadaysforaction)
         if value < downthreshould:
            fund.action = -1
    #default action=0

#New analysis patterns

@exeTime
def pattern5(fundinfolist, threadnum, days, isdrop, topnum):
    print 'Fund list 5: 侧重最近一年表现，新兴市场(少于两年=两年数据空)'
    #至少成立一年
    def passed5(fund):
        try:
            string.atof(fund.halfyeardelta)
            string.atof(fund.yeardelta)
            return fund.twoyeardelta == ""
            #return True
        except:
            return False

    fundInfoList5 = filter(passed5, fundinfolist)
    print 'total funds met requirements: %d' % len(fundInfoList5)

    pool0 = threadpool.ThreadPool(threadnum)
    requests0 = threadpool.makeRequests(maxDropOrIncrease, fundInfoList5)
    [pool0.putRequest(req) for req in requests0]
    pool0.wait()

    fundInfoListOrdered5 = sorted(fundInfoList5, key=lambda fund:string.atof(fund.maxdelta),reverse=(isdrop==False))
    fundlinkTemp = 'http://fund.eastmoney.com/%s.html'
    jjjzUrlTemp = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=%s&page=1&per=%d&sdate=&edate='
    for i in range(0,min(topnum, len(fundInfoListOrdered5))):
        fundlink = fundlinkTemp % fundInfoListOrdered5[i].fundcode
        jjjzUrl = jjjzUrlTemp % (fundInfoListOrdered5[i].fundcode, workingdays)
        if isdrop:
            print '   %s %s %s 净值:%s %d工作日最大回撤:%s 灾难日:%s' % (fundlink , jjjzUrl, fundInfoListOrdered5[i].name,
                                                        fundInfoListOrdered5[i].latestvalue, days,
                                                        fundInfoListOrdered5[i].maxdelta,
                                                        fundInfoListOrdered5[i].eventday)
        else:
            print '   %s %s %s 净值:%s %d工作日最大涨幅:%s 始于:%s' % (fundlink , jjjzUrl, fundInfoListOrdered5[i].name,
                                                        fundInfoListOrdered5[i].latestvalue,days,
                                                        fundInfoListOrdered5[i].maxdelta,
                                                        fundInfoListOrdered5[i].eventday)

@exeTime
def pattern6(fundcodelist):
    print 'Check delta for self selected fund, give buy/sell/noaction order'
    print 'Strategy: increased 8% in passed m days(at most) then sell, or dropped 5% then buy, otherwise, no action'

    fundlist6 = []
    for fundcode in fundcodelist:
        fund = Fund()
        fund.fundcode = fundcode
        fundlist6.append(fund)

    pool0 = threadpool.ThreadPool(len(fundcodelist))
    requests0 = threadpool.makeRequests(getPerfForFund, fundlist6)
    [pool0.putRequest(req) for req in requests0]
    pool0.wait()

    actionsum = 0
    for fund in fundlist6:
        actionsum +=fund.action

    #Strategy to sell or buy in under such unstable situation
    if actionsum > 2:
        print 'ActionSum: %d for %d funds, Time To Sell Out!!!' % (actionsum, len(fundcodelist))
    elif actionsum < -2:
        print 'ActionSum: %d for %d funds, Good To Buy In!!!' % (actionsum, len(fundcodelist))
    else:
        print 'ActionSum: %d for %d funds, No Valuable Action!!!' % (actionsum, len(fundcodelist))

#Parameters
#Map -- gp=gupiao, hh=hunhe, zs=zhishu, zq=zhaiquan
typeFilter = 'hh' # types allNum:2602,gpNum:469,hhNum:1174,zqNum:734,zsNum:344,bbNum:100,qdiiNum:94,etfNum:0,lofNum:147

#Get start and end date time
sDate = datetime.datetime.now() - datetime.timedelta(days=365)
sTime = sDate.strftime("%Y-%m-%d")
eTime = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))#'2016-04-03'

num = 10000 #Max number fund to load(10000 for all funds)
topNum = 30 #Top funds to print out
threadNum = topNum #Number for multi-thread
filecsv = 'funds.csv' #csv file name
savecsvfile = False #Whether save csv file or not
filters = (typeFilter, sTime, eTime, num)
workingdays = 100 #fund history value check working days window
deltadays = 10 #delta working days to check drop and increase max
checkdrop = False #check drop or increase

#parameter for pattern 6
myfundlist = ['377010','270005','110029','590008','163406','161810','519113','162010', '166011','530018','161810','161017','320010', '100038', '040016']
upthreshold = 8
downthreshould = -1
deltadaysforaction = 5
etimeforhis = (datetime.datetime.now() - datetime.timedelta(days=0)).strftime("%Y-%m-%d")

#Main calls
print '-------Start Analysis-------'

#Retrieve fund info list
listcontent = getFundList(filters)
fundInfoList = parseFundList(listcontent, savecsvfile, filecsv)

#Analysis based on defined pattern
#pattern5(fundInfoList, threadNum, deltadays, checkdrop, topNum)
pattern6(myfundlist)

print '-------Analysis Completed-------'

