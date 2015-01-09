#!python
# -*- coding: utf-8 -*-


import base64
import zlib
from Crypto.Cipher import AES
import cookielib, urllib2, urllib
import copy
import json
import time
import traceback

"""
1001 getaccountinfo
1005 Get mine number
1007 list backpack
1009 use backpack item(id)


2003 Get mine info
2004 digmine (x, y)
2005 getminemap 
2006 getgatherlist
2007 gather (x, y)
2016 Get mine task list
2017 Add mine task, (id = 10001 ~ 10009)
2018 Finish mine task, (id)

5002 team and general info
5007 collect reward

6001 get arena list
6006 get arena reward (type=1, 4, 9)
6007 arena battle (id)

7001 list food
7002 use food (foodid)

"""


allconfigs = ["字体配置","事件表","升级经验表","招募","冒险地点","商城","武具强化","食物","被动技能",
              "英雄技能","怪物组","英雄勇者","奖励事件掉落组","额外成功率价格","TIP配置","矿脉属性","宿命武具",
              "徽记","尘土徽记和宿命武具获得","货币表","道具表","切磋竞技场战斗场景表","升级经验战力结算","宿命锻造",
              "新手_新手值","动作和特效表_角色特效","系统配置表","转生价格","合作技能","游戏功能开启表","魂晶兑换",
              "国王订单","自动挖矿","游戏故事配置","Q点购买表","活动时间表","每日充值活动","累计充值活动",
              "每日消费活动","累计消费活动","目标活动招募","目标活动血钻招募","目标活动击杀巨魔","目标活动击杀BOSS",
              "特殊事件","道具兑换活动","活动道具","商店配置","公告系统","秘术之门","杂项","区域配置","争霸战奖励表"]


#urllib2.install_opener(urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1)))
proxy_handler = urllib2.ProxyHandler({})
opener = urllib2.build_opener(proxy_handler)
urllib2.install_opener(opener)

cj = cookielib.MozillaCookieJar()
cj.load("wakuang.cookie")

def decode(encrypted):
    encrypted = base64.b64decode(encrypted)
    cipher = AES.new("qdfgtyjltgfresdf", AES.MODE_CBC, "sftjkiuyhyujkiol" )
    encrypted = cipher.decrypt(encrypted)
    encrypted = base64.b64decode(encrypted)
    clear = zlib.decompress(encrypted, -15)
    return clear
    
def getConfig(name):
    url = "http://ks1mxwk.conf.u77.com/getconfig.ashx?name=%s&v=1.0.23&t=1"%(urllib.quote(name))
    encrypted = urllib2.urlopen(url).read()
    clear = decode(encrypted)
    return json.loads(clear)
    
def search(strtofind, prefix, postfix):
    start = strtofind.find(prefix)
    if start == -1:
        return ""
    start = start + len(prefix)
    end = strtofind.find(postfix, start)
    if end == -1:
        return ""
    return strtofind[start:end]

def Login(username, password):
    global userid
    global sid
    global gameserver
    
    req = urllib2.Request("http://youxi.kdslife.com/youxi/play/wakuang/")
    req.add_header("Referer", "http://passport.pchome.net/login.php?action=login&goto=http://youxi.kdslife.com/youxi/play/wakuang/")
    req.add_header("User-agent", "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)")
    print req.get_full_url()
    cj.add_cookie_header(req)
    res = urllib2.urlopen(req)
    data = res.read()
    nexturl = search(data, '<iframe src="', '"')
    
    if nexturl == "":
        req = urllib2.Request("http://passport.pchome.net/login.php?action=login&goto=http://youxi.kdslife.com/youxi/play/wakuang/", 
                          "username="+username+"&password="+password)
        req.add_header("Referer", "http://passport.pchome.net/login.php?action=login&goto=http://youxi.kdslife.com/youxi/play/wakuang/")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        req.add_header("User-agent", "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)")        
        print req.get_full_url()
        res = urllib2.urlopen(req)
        res.read()
        
        cj.clear()
        cj.extract_cookies(res, req)
        for cookie in cj:
            c = copy.deepcopy(cookie)
            c.domain = ".kdslife.com"
            cj.set_cookie(c)
        print cj
        cj.save("wakuang.cookie")
        
        req = urllib2.Request("http://youxi.kdslife.com/youxi/play/wakuang/")
        req.add_header("Referer", "http://passport.pchome.net/login.php?action=login&goto=http://youxi.kdslife.com/youxi/play/wakuang/")
        req.add_header("User-agent", "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)")
        cj.add_cookie_header(req)
        print req.get_full_url()
        res = urllib2.urlopen(req)
        data = res.read()
        nexturl = search(data, '<iframe src="', '"')
    

    req = urllib2.Request(nexturl)
    print req.get_full_url()
    res = urllib2.urlopen(req)
    data = res.read()
    
    sid = search(data, "var sid='", "'")
    userid = search(data, "LoadGame(0,", ")")
    gameserver = search(nexturl, "http://", "/")
    gameserver = "http://" + gameserver + "/service/main.ashx"
    

def gamecmd(cmd, params={}):
    global userid
    global sid
    global gameserver
    params["userid"] = userid
    params["sid"] = sid
    params["t"] = cmd
    print "Request: " + str(params)
    res = urllib2.urlopen(gameserver, urllib.urlencode(params))
    data = res.read()
    print "Response: " + str(data)
    return json.loads(data)


def process_arena():
    arenalist =  gamecmd("6001")
    data = arenalist["data"]
    arenacount = data["arenacount"]
    enemylist = data["list"]
    
    for enemy in enemylist:
        if enemy["iswin"] == 0 and arenacount < 10:
            result = gamecmd("6007", {"id":enemy["id"]})
            enemy["iswin"] = result["data"]["iswin"]
            arenacount = arenacount + 1
            time.sleep(1)
    for enemy in enemylist:
        if enemy["iswin"] == 0 and arenacount < 10:
            result = gamecmd("6007", {"id":enemy["id"]})
            enemy["iswin"] = result["data"]["iswin"]
            arenacount = arenacount + 1
            time.sleep(1)
    
    arenalist =  gamecmd("6001")
    data = arenalist["data"]
    totalwin = 0
    for enemy in enemylist:
        if enemy["iswin"] == 1:
            totalwin += 1
    
    if data["arenabox3isget"]==0 and totalwin>=9:
        gamecmd("6006", {"type":9})
    if data["arenabox2isget"]==0 and totalwin>=4:
        gamecmd("6006", {"type":4})
    if data["arenabox1isget"]==0 and totalwin>=1:
        gamecmd("6006", {"type":1})



def process_backpack():
    info = gamecmd("5002")
    boxcount = info["data"]["boxcount"]
    if boxcount>0:
        gamecmd("5007")
    
    backpack = gamecmd("1007")
    itemlist = backpack["data"]["list"]
    for item in itemlist:
        if item["itemid"]//1000000 in (1, 3, 4, 6, 7, 8):
            gamecmd("1009", {"id":item["id"]})
            time.sleep(1)
    
def process_mine(minetype):
    gatherlist = gamecmd("2006")
    for gather in gatherlist["data"]:
        if(gather["time"] >= gather["needtime"]):
            gamecmd("2007", {"x":gather["x"], "y":gather["y"]})
    
    info = gamecmd("2003")
    minecount = info["data"]["szg"]
    minelist = gamecmd("2016")
    for mine in minelist["data"]:
        if mine["sid"] != 0:
            if "time" in mine and mine["time"] == 0:
                gamecmd("2018", {"id":mine["id"]})
            
    minelist = gamecmd("2016")
    for mine in minelist["data"]:
        if mine["sid"] == 0 and minecount >= 20:
            gamecmd("2017", {"id":minetype})

def process_food():
    info = gamecmd("5002")
    fullrate = info["data"]["bzd"]
    if fullrate < 18000:
        foodlist = gamecmd("7001")
        for food in foodlist["data"]:
            if food["count"] > 0:
                gamecmd("7002", {"foodid":food["foodid"]})
                break
while True:
    try:
        Login("xxxxxxxxx", "xxxxxxxx")
        print "gameserver:" + gameserver
        print "sid:" + sid
        print "userid:" + userid
        process_arena()
        process_backpack()
        process_mine("10004")
        process_food()
    except Exception as e:
        traceback.print_exc()
    time.sleep(600)
