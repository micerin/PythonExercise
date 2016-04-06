import string

def GetMaxMFromN(data, m):
    max = -100000
    maxindex = -1
    for i in range(0, len(data)-m):
        sum0 = Sum(data, i, m)
        if sum0 > max:
            max = sum0
            maxindex = i
    return max, maxindex

def GetMinMFromN(data, m):
    min = 100000
    minindex = -1
    for i in range(0, len(data)-m):
        sum0 = Sum(data, i, m)
        if sum0 < min:
            min = sum0
            minindex = i
    if min == 0:
        min = 100000
    return min, len(data)-minindex-1

def Sum(data, index, m):
    sum = 0
    if (index + m) > len(data):
        return 'invalid'
    for i in range(index, index+m):
        if data[len(data) - i -1].dayincrease != '' and data[len(data) - i -1].dayincrease != ' ':
            sum += string.atof(data[len(data) - i -1].dayincrease)
    return sum
