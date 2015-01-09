#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import zlib
from Crypto.Cipher import AES
import urllib2
import urllib
import json

allconfigs = ["字体配置","事件表","升级经验表","招募","冒险地点","商城","武具强化","食物","被动技能",
              "英雄技能","怪物组","英雄勇者","奖励事件掉落组","额外成功率价格","TIP配置","矿脉属性","宿命武具",
              "徽记","尘土徽记和宿命武具获得","货币表","道具表","切磋竞技场战斗场景表","升级经验战力结算","宿命锻造",
              "新手_新手值","动作和特效表_角色特效","系统配置表","转生价格","合作技能","游戏功能开启表","魂晶兑换",
              "国王订单","自动挖矿","游戏故事配置","Q点购买表","活动时间表","每日充值活动","累计充值活动",
              "每日消费活动","累计消费活动","目标活动招募","目标活动血钻招募","目标活动击杀巨魔","目标活动击杀BOSS",
              "特殊事件","道具兑换活动","活动道具","商店配置","公告系统","秘术之门","杂项","区域配置","争霸战奖励表"]

def decode(encrypted):
    encrypted = base64.b64decode(encrypted)
    cipher = AES.new("qdfgtyjltgfresdf", AES.MODE_CBC, "sftjkiuyhyujkiol" )
    encrypted = cipher.decrypt(encrypted)
    encrypted = base64.b64decode(encrypted)
    clear = zlib.decompress(encrypted, -15)
    return clear

def download(config):
    url = "http://ks1mxwk.conf.u77.com/getconfig.ashx?name=%s&v=1.0.23&t=1"%(urllib.quote(config))
    encrypted = urllib2.urlopen(url).read()
    clear = decode(encrypted)
    clear = json.dumps(json.loads(clear), indent=2, ensure_ascii=False, sort_keys=True)

    cfgfile = open("braverist/%s.json"%(config.decode('utf-8').encode('gb2312')), "wb")
    cfgfile.write(clear)
    cfgfile.close()

for config in allconfigs:
    download(config)
