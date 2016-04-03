#encoding=utf8
# -*- coding: gb2312 -*-
import urllib2
import re
import csv
import string
import time
import BeautifulSoup

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
        self.weighted = ''
        self.managerperf = ''

#Get fund list per filter
def getFundList(filter):
    url = urlTemp % filter
    content = urllib2.urlopen(url).read()
    return content

#Parse fund list info from given content
def parseFundList(content):
    flist = re.findall(re_pat, content)
    print '%d funds for %s in total' % (len(flist),typeFilter)
    #saveAsCsv(flist, filecsv) # save all fund info to csv file

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
            fundInfoList.append(fund)

    #get overall data for all funds, all kinds
    #re_strforall = r'allNum:(.*),gpNum:(.*),hhNum:(.*),zqNum:(.*),zsNum:(.*),bbNum:(.*),qdiiNum:(.*),etfNum:(.*),lofNum:(.*)'
    #re_patforall = re.compile(re_strforall)
    index = string.index(content, 'allNum:')
    print content[index:-2]

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

#Check fund rank >=4
def isHighlyRanked(foudcode):
    rankUrlTemp = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=grade&code=%s&page=1&per=1'
    rankUrl = rankUrlTemp % foudcode
    content = urllib2.urlopen(rankUrl).read()
    if '\'4\'' in content or '\'5\'' in content:
        return True
    return False

#Analysis patterns
def pattern1():
    print 'Fund list 1: 净值最高'
    def passed1(fund):
        try:
            string.atof(fund.latestvalue)
            return True
        except:
            return False
    fundInfoList1 = filter(passed1, fundInfoList)
    fundInfoListOrdered1 = sorted(fundInfoList1,key=lambda fund:string.atof(fund.latestvalue), reverse=True)
    for i in range(0,topNum - 1):
        fundlinkTemp = 'http://fund.eastmoney.com/%s.html'
        fundlink = fundlinkTemp % fundInfoListOrdered1[i].fundcode
        print '   %s %s %.3f' % (fundlink , fundInfoListOrdered1[i].name, string.atof(fundInfoListOrdered1[i].latestvalue))

def pattern2():
    print 'Fund list 2: 最近3个月增长最快，并且成立两年以上'
    def passed2(fund):
        try:
            string.atof(fund.threemonthdelta)
            string.atof(fund.twoyeardelta)
            return True
        except:
            return False
    fundInfoList2 = filter(passed2, fundInfoList)
    fundInfoListOrdered2 = sorted(fundInfoList2, key=lambda fund:string.atof(fund.threemonthdelta),reverse=True)
    meetnum = 0
    for i in range(0, len(fundInfoListOrdered2)):
        fundlinkTemp = 'http://fund.eastmoney.com/%s.html'
        fundlink = fundlinkTemp % fundInfoListOrdered2[i].fundcode
        print '   %s %s 净值：%s 近三个月：%.3f 两年数据：%s' % (fundlink , fundInfoListOrdered2[i].name, fundInfoListOrdered2[i].latestvalue,
                                                    string.atof(fundInfoListOrdered2[i].threemonthdelta), fundInfoListOrdered2[i].twoyeardelta)
        meetnum +=1
        if meetnum == topNum:
            break

def pattern3():
    print 'Fund list 3: 权重 0.65*近半年 + 0.3*近一年 + 0.05*近两年, 且评级大于等于4星'
    weight= 0
    def passed3(fund):
        try:
            string.atof(fund.halfyeardelta)
            string.atof(fund.yeardelta)
            string.atof(fund.twoyeardelta)
            return True
        except:
            return False

    fundInfoList3 = filter(passed3, fundInfoList)
    for item in fundInfoList3:
        item.weighted = string.atof(item.halfyeardelta)* 0.65 + string.atof(item.yeardelta)*0.3 + string.atof(item.twoyeardelta)*0.05
        #for zq
        #item.weighted = string.atof(item.halfyeardelta)* 0.3 + string.atof(item.yeardelta)*0.4 + string.atof(item.twoyeardelta)*0.3
    fundInfoListOrdered3 = sorted(fundInfoList3, key=lambda fund:string.atof(fund.weighted),reverse=True)
    meetnum = 0
    fundInfoList4 = []
    for i in range(0, len(fundInfoListOrdered3)):
        fundlinkTemp = 'http://fund.eastmoney.com/%s.html'
        if isHighlyRanked(fundInfoListOrdered3[i].fundcode):
            fundInfoList4.append(fundInfoListOrdered3[i])
            fundlink = fundlinkTemp % fundInfoListOrdered3[i].fundcode
            print '   %s %s 净值：%s 权重：%s' % (fundlink , fundInfoListOrdered3[i].name,
                                            fundInfoListOrdered3[i].latestvalue, fundInfoListOrdered3[i].weighted)
            meetnum +=1
        if meetnum == topNum:
            break

    #Check fund manager perf
    print 'Fund list 4: 在3的基础上，排序当前基金经理业绩(待补充没有变换的情况，当前设定为0)'
    for funditem in fundInfoList4:
        jjjllinkTemp = 'http://fund.eastmoney.com/f10/jjjl_%s.html'
        jjjllink = jjjllinkTemp % funditem.fundcode
        try:
            soup = BeautifulSoup.BeautifulSOAP(urllib2.urlopen(jjjllink).read().decode('gb2312').encode('utf8'))
        except:
            soup = BeautifulSoup.BeautifulSOAP(urllib2.urlopen(jjjllink).read().decode('gbk').encode('utf8'))
        table = soup.find('table', attrs={'class':'w782 comm jlchg'})
        if len(table.contents[1].contents) > 0:
            funditem.managerperf = table.contents[1].contents[0].contents[4].contents[0][0:-1]
            #print table.contents[1].contents[0].contents[0].contents[0]
            #print table.contents[1].contents[0].contents[3].contents[0]
            #print table.contents[1].contents[0].contents[4].contents[0]
        else:
            try: # retry once
                soup = BeautifulSoup.BeautifulSOAP(urllib2.urlopen(jjjllink).read().decode('gb2312').encode('utf8'))
            except:
                soup = BeautifulSoup.BeautifulSOAP(urllib2.urlopen(jjjllink).read().decode('gbk').encode('utf8'))
            table = soup.find('table', attrs={'class':'w782 comm jlchg'})
            if len(table.contents[1].contents) > 0:
                funditem.managerperf = table.contents[1].contents[0].contents[4].contents[0][0:-1]
            else:
                funditem.managerperf = '0'

    fundInfoListOrdered4 = sorted(fundInfoList4, key=lambda fund:string.atof(fund.managerperf),reverse=True)
    meetnum = 0
    for i in range(0, len(fundInfoListOrdered4)):
        fundlinkTemp = 'http://fund.eastmoney.com/%s.html'
        if isHighlyRanked(fundInfoListOrdered4[i].fundcode):
            fundInfoList4.append(fundInfoListOrdered4[i])
            fundlink = fundlinkTemp % fundInfoListOrdered4[i].fundcode
            print '   %s %s 净值：%s 业绩：%s' % (fundlink , fundInfoListOrdered4[i].name,
                                            fundInfoListOrdered4[i].latestvalue, fundInfoListOrdered4[i].managerperf.encode('utf-8'))
            meetnum +=1
        if meetnum == topNum/2:
            break

#Parameters
typeFilter = 'hh' # types allNum:2602,gpNum:469,hhNum:1174,zqNum:734,zsNum:344,bbNum:100,qdiiNum:94,etfNum:0,lofNum:147
sTime = '2015-04-03'

now = int(time.time())
timeArray = time.localtime(now)
eTime = time.strftime("%Y-%m-%d", timeArray)#'2016-04-03'

num = 10000 #Max number fund to load(10000 for all funds)
topNum = 30 #Top funds to print out
filecsv = 'funds.csv'
filters = (typeFilter, sTime, eTime, num)
fundInfoList = []

#Main calls
print '-------Start Analysis-------'

listcontent = getFundList(filters)
parseFundList(listcontent)

#pattern1()
#pattern2()
pattern3()
print '-------Analysis Completed-------'

