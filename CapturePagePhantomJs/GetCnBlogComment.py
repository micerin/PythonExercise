import urllib2
import urllib
import json

def getCommentsHtml(index):
    url = "http://www.cnblogs.com/mvc/blog/GetComments.aspx"
    params = {
        "postId":"5226546",
        "blogApp":"hearzeus",
        "pageIndex":`index`,
        'anchorCommentId':`0`,
        '_=':'1456908852216'
    }
    url_params = urllib.urlencode(params)
    content = json.loads(urllib2.urlopen(url,data=url_params).read())['commentsHtml']
    return content

getCommentsHtml(1)