import urllib.request
import urllib
import re
import os
import json

BASE_ROOT_PATH = os.path.join(os.path.expanduser("~"), 'NETEASE')
IMAGE_DOMAIN = "http://cms-bucket.ws.126.net"
VIDEO_DOMAIN = "http://flv3.bn.netease.com"
# 每日一图
BLACK_LIST = ['gentie','6b7ba6538c1a40ca81fa9ba663109bdf','208593901848466580359f2a6f976ea6','e1e18616b8e24e6f906e786271f8e5dc','69c458f6fc5f46149584f4500e974afd']

# 封装获取网页所有信息的函数
def getHtml(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
    req = urllib.request.Request(url=url, headers=headers)
    html = urllib.request.urlopen(req).read().decode('utf-8')
    return html

# 封装获取满足正则表达式的图片地址
def getImg(postid, html):
    # reg = r'http://cms-bucket\.ws\.126\.net/.+?\.(?:gif|jpeg|jpg|png)'
    # imgre = re.compile(reg)
    # imglist = re.findall(imgre, html)
    imglist = []
    imgDic = json.loads(html).get(postid).get('img')
    for img in imgDic:
        path = img.get('src')
        inBlack = False
        for bl in BLACK_LIST:
            if bl in str(path):
                inBlack = True
                break
        if not inBlack:
            imglist.append(path)
    return imglist

# 封装获取满足正则表达式的视频地址
def getVideo(postid, html):
    # reg = r'http://flv3\.bn\.netease\.com/videolib1/.+?\.mp4'
    # videore = re.compile(reg)
    # videolist = re.findall(videore, html)
    videolist =[]
    videoDic = json.loads(html).get(postid).get('video')
    for video in videoDic:
        videoUrl = {}
        videoUrl['url'] = video.get('mp4_url')
        videoUrl['name'] = video.get('alt')
        videolist.append(videoUrl)

    return videolist

# 封装获取满足正则表达式的文章地址
def getDoc(html):
    reg = r'http://3g\.163\.com/.+?\.html'
    docre = re.compile(reg)
    doclist = re.findall(docre, html)
    return doclist

def callbackfunc(blocknum, blocksize, totalsize):
    '''回调函数
    @blocknum: 已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
    '''
    percent = 100.0 * blocknum * blocksize / totalsize
    if percent > 100:
        percent = 100
    print("%.2f%%"% percent)

def mkPath(url):
    basename = os.path.dirname(url)
    if basename.startswith(IMAGE_DOMAIN):
        dir = basename.split(IMAGE_DOMAIN)[1]
    elif basename.startswith(VIDEO_DOMAIN):
        dir = "/Video"
    else:
        dir = ""
    path = BASE_ROOT_PATH + dir
    if not os.path.exists(path):
        os.makedirs(path)
    return path

#轻松一刻专题爬取图片和视频
moment = getHtml("http://c.m.163.com/nc/special/S1426236075742.html")
#获取所有文章列表
for doc in getDoc(moment):
    postid = os.path.basename(doc)[0:len(os.path.basename(doc))-5]
    # 可以指定截止文章id，目前是2020.02.16
    if postid == "F5F12CBC000181BR":
        break
    html = getHtml("http://c.m.163.com/nc/article/preload/" + postid + "/full.html")
    # 下载照片
    try:
        for imgurl in getImg(postid,html):
            filepath = mkPath(imgurl) + "/" + os.path.basename(imgurl)
            if not os.path.exists(filepath) :
                urllib.request.urlretrieve(imgurl, filepath, callbackfunc)

        for video in getVideo(postid,html):
            filepath = mkPath(video.get('url')) + "/" + video.get('name') + ".mp4"
            if not os.path.exists(filepath):
                urllib.request.urlretrieve(video.get('url'), filepath, callbackfunc)

    except:
        print("some problem!")

print('finish!')