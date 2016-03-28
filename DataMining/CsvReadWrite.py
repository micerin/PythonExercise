import csv
import string

IOPSkeywords = 'IOPS='
QueueDepthkeywords = 'QueueDepth='
BlockSizekeywords = 'Block Size:'
Quantilekeywords = 'Quant'
StartTimekeywords = 'StartTime='
EndTimekeywords = 'EndTime='
SubDirkeywords = 'SubDirectory='
csvfiletowrite = open('result3.csv','wb')
spamwriter = csv.writer(csvfiletowrite, delimiter=',', quotechar='|')#, quoting=csv.QUOTE_MINIMAL)

def GetQuantiles(quantile):
    returnItems = []
    items0 = string.split(quantile, ':')
    for item in items0:
        if ']' in item:
            returnItems.append(string.split(item, ']')[0])
    return returnItems

#quantile
with open('result.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    result=[]

    for row in spamreader:
        #print len(row)
        for item in row:
            if Quantilekeywords in item:
                quantiles = GetQuantiles(item)
                for quantile in quantiles:
                    result.append(quantile)
            if IOPSkeywords in item:
                result.append(string.strip(item)[5:])
            if SubDirkeywords in item:
                result.append(item[13:])
            if EndTimekeywords in item:
                result.append(item[8:])
            if StartTimekeywords in item:
                result.append(item[10:])
        if len(result) == 18: #group by group
            print ' '.join(result)
            spamwriter.writerow(result)
            result=[]

''' #only for QD, blockSize and IOPS

#fieldnames = ['QueueDepth', 'BlockSize', 'IOPS']
#spamwriter = csv.DictWriter(csvfiletowrite, fieldnames=fieldnames)
#spamwriter.writeheader()

with open('result.csv', 'rb') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    result=[]

    for row in spamreader:
        #print len(row)
        for item in row:
            if QueueDepthkeywords in item:
                result.append(string.strip(item))
            if BlockSizekeywords in item:
                result.append(string.strip(item).replace(' ','').replace(':','='))
            if IOPSkeywords in item:
                result.append(string.strip(item))
        if len(result) == 3:
            print ' '.join(result)
            spamwriter.writerow(result)
            result=[]
'''

csvfiletowrite.close()