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
from bs4 import BeautifulSoup
import threadpool

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
    retrytimes= 5
    for i in range(0,retrytimes):#retry 4 times at most since sometimes the page load return null result...
        # utf-8 or gb2312 or gbk
        try:
            soup = BeautifulSoup(urllib2.urlopen(jjjllink).read().decode('gb2312').encode('utf8'), "html.parser")
        except:
            try:
                soup = BeautifulSoup(urllib2.urlopen(jjjllink).read().decode('gbk').encode('utf8'), "html.parser")
            except:
                soup = BeautifulSoup(urllib2.urlopen(jjjllink).read(), "html.parser")
        table = soup.find('table', attrs={'class':'w782 comm jlchg'})
        if table == None:
            continue

        if len(table.contents[1].contents) > 0:
            funditem.managerperf = table.contents[1].contents[0].contents[4].contents[0][0:-1]
            funditem.managerduration = table.contents[1].contents[0].contents[3].contents[0]
            #print table.contents[1].contents[0].contents[0].contents[0]
            break
        i+=1

    if i >= retrytimes-1:#hit here after retrytimes times try, should indicate no manager change, get fromstartup
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
        soup = BeautifulSoup(urllib2.urlopen(fundlink).read(), "html.parser")
    except:
        try:
            soup = BeautifulSoup(urllib2.urlopen(fundlink).read().decode('gb2312').encode('utf8'), "html.parser")
        except:
            soup = BeautifulSoup(urllib2.urlopen(fundlink).read().decode('gbk').encode('utf8'), "html.parser")
    buyNow = soup.find(id='buyNowStatic')

    #<a id="buyNowStatic" class="buyNowStatic unbuy" href="javascript:;" target="_self">立即购买</a>
    #<a id="buyNowStatic" class="buyNowStatic" href="https://trade.1234567.com.cn/FundtradePage/default2.aspx?fc=162010&amp;spm=pzm" target="_blank">立即购买</a>
    if 'trade' in dict(buyNow.attrs)['href']:
        fund.buyable = True

#Analysis patterns
def pattern1(fundinfolist):
    print 'Fund list 1: 净值最高'
    def passed1(fund):
        try:
            string.atof(fund.latestvalue)
            return True
        except:
            return False
    fundInfoList1 = filter(passed1, fundinfolist)
    fundInfoListOrdered1 = sorted(fundInfoList1,key=lambda fund:string.atof(fund.latestvalue), reverse=True)
    for i in range(0,topNum - 1):
        fundlinkTemp = 'http://fund.eastmoney.com/%s.html'
        fundlink = fundlinkTemp % fundInfoListOrdered1[i].fundcode
        print '   %s %s %.3f' % (fundlink , fundInfoListOrdered1[i].name, string.atof(fundInfoListOrdered1[i].latestvalue))

def pattern2(fundinfolist):
    print 'Fund list 2: 最近3个月增长最快，并且成立两年以上'
    def passed2(fund):
        try:
            string.atof(fund.threemonthdelta)
            string.atof(fund.twoyeardelta)
            return True
        except:
            return False
    fundInfoList2 = filter(passed2, fundinfolist)
    fundInfoListOrdered2 = sorted(fundInfoList2, key=lambda fund:string.atof(fund.threemonthdelta),reverse=True)
    meetnum = 0
    for i in range(0, len(fundInfoListOrdered2)):
        fundlinkTemp = 'http://fund.eastmoney.com/%s.html'
        fundlink = fundlinkTemp % fundInfoListOrdered2[i].fundcode
        print '   %s %s 净值:%s  近三个月:%.3f  两年数据:%s' % (fundlink , fundInfoListOrdered2[i].name, fundInfoListOrdered2[i].latestvalue,
                                                    string.atof(fundInfoListOrdered2[i].threemonthdelta), fundInfoListOrdered2[i].twoyeardelta)
        meetnum +=1
        if meetnum == topNum:
            break

@exeTime
def pattern3(fundinfolist, threadnum):
    #note, 'zq' would use separate weight formula per it's cycle period is not that sensitive
    if(typeFilter == 'zq'):
        print 'Fund list 3: 权重 0.1*近3个月 + 0.25*近半年 + 0.4*近一年 + 0.25*近两年, 且评级大于等于4星'
    else:
        print 'Fund list 3: 权重 0.2*近3个月 + 0.45*近半年 + 0.3*近一年 + 0.05*近两年, 且评级大于等于4星'
    weight= 0
    def passed3(fund):
        try:
            string.atof(fund.halfyeardelta)
            string.atof(fund.yeardelta)
            string.atof(fund.twoyeardelta)
            string.atof(fund.threemonthdelta)
            return True
        except:
            return False

    fundInfoList3 = filter(passed3, fundinfolist)

    #If highly ranked then calculate weighted value for fund
    def checkHighRankandCalWeight(item):
        isHighlyRanked(item)
        if(item.highlyranked):
            if typeFilter == 'zq':
                item.weighted = string.atof(item.threemonthdelta)* 0.1 + string.atof(item.halfyeardelta)* 0.25 +\
                                string.atof(item.yeardelta)*0.4 + string.atof(item.twoyeardelta)*0.25
            else:
                item.weighted = string.atof(item.threemonthdelta)* 0.2 + string.atof(item.halfyeardelta)* 0.45 +\
                                string.atof(item.yeardelta)*0.3 + string.atof(item.twoyeardelta)*0.05
        else:
           item.weighted = '-1000' #With this, no need do extra filter on highlyranked

    #Calculate fund weight
    pool0 = threadpool.ThreadPool(threadnum)
    requests0 = threadpool.makeRequests(checkHighRankandCalWeight, fundInfoList3)
    [pool0.putRequest(req) for req in requests0]
    pool0.wait()

    fundInfoListOrdered3 = sorted(fundInfoList3, key=lambda fund:string.atof(fund.weighted),reverse=True)

    meetnum = 0
    fundInfoList4 = []
    fundlinkTemp = 'http://fund.eastmoney.com/%s.html'

    for i in range(0, min(topNum,len(fundInfoListOrdered3))):
        fundInfoList4.append(fundInfoListOrdered3[i])
        fundlink = fundlinkTemp % fundInfoListOrdered3[i].fundcode
        print '   %s %s 净值:%s 权重:%s' % (fundlink , fundInfoListOrdered3[i].name,
                                        fundInfoListOrdered3[i].latestvalue, fundInfoListOrdered3[i].weighted)

    return fundInfoList4

@exeTime
def pattern4(fundinfolist4, maxreturn, threadnum):
    #Check fund manager perf
    print 'Fund list 4: 基于pattern3的结果，排序当前基金经理业绩'

    #Get manager perf if buyable
    def checkBuyableAndGetPerf(fund):
        isBuyable(fund)
        if fund.buyable:
            getManagerPerf(fund)
        else:
            fund.managerperf = '-1000' #With this, no need do extra filter on buyable

    #Get fund manager perf
    pool2 = threadpool.ThreadPool(threadnum)
    requests2 = threadpool.makeRequests(checkBuyableAndGetPerf, fundinfolist4)
    [pool2.putRequest(req) for req in requests2]
    pool2.wait()

    fundInfoListOrdered4 = sorted(fundinfolist4, key=lambda fund:string.atof(fund.managerperf),reverse=True)

    meetnum = 0
    fundlinkTemp = 'http://fund.eastmoney.com/%s.html'
    jjjllinkTemp = 'http://fund.eastmoney.com/f10/jjjl_%s.html'

    for i in range(0, min(maxreturn,len(fundInfoListOrdered4))):
        fundinfolist4.append(fundInfoListOrdered4[i])
        fundlink = fundlinkTemp % fundInfoListOrdered4[i].fundcode
        jjjllink = jjjllinkTemp % fundInfoListOrdered4[i].fundcode
        print '   %s %s %s 净值:%s 业绩:%s Duration:%s' % (fundlink, jjjllink, fundInfoListOrdered4[i].name,
                                                       fundInfoListOrdered4[i].latestvalue,
                                                       fundInfoListOrdered4[i].managerperf.encode('utf-8'),
                                                       fundInfoListOrdered4[i].managerduration.encode('utf-8'))


#Parameters
#Map -- gp=gupiao, hh=hunhe, zs=zhishu, zq=zhaiquan
typeFilter = 'gp' # types allNum:2602,gpNum:469,hhNum:1174,zqNum:734,zsNum:344,bbNum:100,qdiiNum:94,etfNum:0,lofNum:147

#Get start and end date time
sDate = datetime.datetime.now() - datetime.timedelta(days = 365)
sTime = sDate.strftime("%Y-%m-%d")
eTime = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))#'2016-04-03'

num = 300 #Max number fund to load(10000 for all funds)
topNum = 30 #Top funds to print out
threadNum = topNum #Number for multi-thread
filecsv = 'funds.csv' #csv file name
savecsvfile = False #Whether save csv file or not
filters = (typeFilter, sTime, eTime, num)

#Main calls
print '-------Start Analysis-------'

#Retrieve fund info list
listcontent = getFundList(filters)
fundInfoList = parseFundList(listcontent, savecsvfile, filecsv)

#Analysis based on defined pattern
#pattern1(fundInfoList)
#pattern2(fundInfoList)
fundinfolist4 = pattern3(fundInfoList, threadNum*2)
pattern4(fundinfolist4, 10, threadNum) #pattern4 is based on pattern3

print '-------Analysis Completed-------'

