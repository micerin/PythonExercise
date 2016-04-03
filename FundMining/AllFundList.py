#encoding=utf8
import urllib2
import urllib
import json
import re
import csv
import string
import time

urlTemp = 'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=%s&rs=&gs=0&sc=zzf&st=desc&sd=%s&ed=%s&qdii=&tabSubtype=,,,,,&pi=1&pn=%s&dx=1'
re_strforfund = r'(\"[^\"]+\"[,]?)'
re_pat = re.compile(re_strforfund)

# class for fund
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

            '''
            fundcodelist.append(isplits[0][1:])
            namelist.append(isplits[1])
            latestvalue.append(isplits[4])
            overallvalue.append(isplits[5])
            latestdelta.append(isplits[6])
            weekdelta.append(isplits[7])
            monthdelta.append(isplits[8])
            threemonthdelta.append(isplits[9])
            sixmonthdelta.append(isplits[10])
            yeardelta.append(isplits[11])
            twoyeardelta.append(isplits[12])
            threeyeahdelta.append(isplits[13])
            thisyeardelta.append(isplits[14])
            fromstartup.append(isplits[15])
            starttime.append(isplits[16])
            '''

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
            #fundcodelist.append(isplits[0])
        for sitem in isplits:
            if sitem !='"': #sitem != '' and
                result.append(sitem)

        spamwriter.writerow(result)
        result = []
    csvfiletowrite.close()

#Parameters
typeFilter = 'hh' # types allNum:2602,gpNum:469,hhNum:1174,zqNum:734,zsNum:344,bbNum:100,qdiiNum:94,etfNum:0,lofNum:147
sTime = '2015-04-03'

now = int(time.time())
timeArray = time.localtime(now)
eTime = time.strftime("%Y-%m-%d", timeArray)#'2016-04-03'

num = 10000 #Max number fund to load(10000 for all funds)
filecsv = 'funds.csv'
filters = (typeFilter, sTime, eTime, num)
'''
fundcodelist = [] #store fund code
namelist = []
latestvalue = []
overallvalue = []
latestdelta = []
weekdelta = []
monthdelta = []
threemonthdelta = []
sixmonthdelta = []
yeardelta = []
twoyeardelta = []
threeyeahdelta = []
thisyeardelta = []
fromstartup = []
starttime = []
'''

fundInfoList = []

#Main calls
listcontent = getFundList(filters)
parseFundList(listcontent)

#analyze and filter
print 'Fund list 1:'




print 'completed'

