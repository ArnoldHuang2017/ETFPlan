#!/usr/bin/python
# -*- coding: UTF-8 -*- 
import requests
import simplejson
import sys
#import os
import hashlib
import random
import time
import re
import sys
#
FUNDS = {
u"000922.SH" : u"100032",
u"CSPSADRP.CI" : u"501029",
u"000016.SH" : u"110003",
u"000989.SH" : u"001133",
u"000905.SH" : u"161017",
u"000827.SH" : u"001064",
u"000300.SH" : u"000311",
u"399330.SZ" : u"110019",
u"399005.SZ" : u"161118",
u"000991.SH" : u"001180",
u"000993.SH" : u"000942",
u"399006.SZ" : u"110026",

u"HSCEI.HI" : u"110031",
u"000903.SH" : u"240014",
u"HSI.HI" : u"000071",
u"399001.SZ" : u"202017",
u"399932.SZ" : u"000248",

u"SPX.GI": u"050025",
u"NDX.GI": u"000834",

u"399986.CSI": u"001594",
u"950090.SH": u"501050",
u"399975.CSI": u"160633",
u"930782.CSI": u"003318",
u"399812.SZ": u"000968",
u"000852.SH": u"003646",
u"399971.SZ": u"004752",
u"399967.SZ": u"000596",
}
 
def get_x_sign():
    random_value = random.randint(100,999)
    curtime = str(time.time())[0:10] + str(random_value)
    target = str("%f")%(float(curtime)*1.01)
    target = target[0:13]
    sha256 = hashlib.sha256()
    sha256.update(target.encode('utf-8'))
    target_sha256 = sha256.hexdigest().upper()
    x_sign = curtime + target_sha256[0:32]
    return x_sign

def get_indexs(retry= 10):
    indexs = []
    def get_data():
        headers = {"Accept" : "application/json",
            "Accept-Encoding" : "gzip, deflate, br",
            "Accept-Language" : "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
            "Connection" : "keep-alive",
            "Cache-Control" : "no-cache",
            "Host" : "qieman.com",
            "Pragma" : "no-cache",
            "Referer" : "https://qieman.com/idx-eval",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
            "x-sign" : "",
            }
        headers["x-sign"] = get_x_sign()
        url = "https://qieman.com/pmdj/v2/idx-eval/latest"
        return_data = requests.get(url, headers=headers, verify=False)  
        index_pattern = re.compile(r'({"indexCode":.*?})') 
        indexlists = index_pattern.findall(return_data.text)
        data = []
        for index in indexlists:
            myindex = simplejson.loads(index)
            data.append(myindex)
        return data

    while retry > 0:
        retry -= 1
        if len(indexs) == 0 and retry !=0:
            indexs = get_data()
            retry -= 1
        elif len(indexs) == 0 and retry == 0:
            return None
        else:
            break
    return indexs
    '''
    index dict example:
    index = {
            u'pb': 0.94, 
            u'indexName': u'\u6052\u751f\u56fd\u4f01', 
            u'peHigh': 21.37, 
            u'indexCode': u'HSCEI.HI', 
            u'roe': 0.1124, 
            u'peLow': 5.55, 
            u'pePercentile': 0.5346, 
            u'score': 75, 
            u'source': 0, #在页面上的排名
            u'pe': 8.38, 
            u'date': 1506528000000, 
            u'group': u'LOW' #LOW：可买 MID：观察 HIGH：不建议 NA：没有百分位的
            }
    '''

def get_data(fundid, retry = 10):
    headers = {
        "Accept" : "*/*", 
        "Accept-Encoding" : "gzip, deflate",
        "Accept-Language" : "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        "Cache-Control" : "no-cache",
        "Connection" : "keep-alive",
        "Host" : "fundgz.1234567.com.cn",
        "Pragma" : "no-cache",
        "Referer" : "",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
    }
    headers["Referer"] = "http://fund.eastmoney.com/%s.html" %fundid
    for retry_times in range(0, retry+1):
        #print "\x1b[1;1H%d" %retry
        try:
            random_value = random.sample(["0","1","2","3","4","5","6","7","8","9"], 1)
            curtime =  str(time.time()).replace('.', '') + random_value[0]    
            return_data = requests.get("http://fundgz.1234567.com.cn/js/%s.js?rt=%s" %(fundid, curtime), headers=headers, verify=False)
            raw_data = re.findall('jsonpgz\((.*)\)', return_data.text)
            if len(raw_data) < 1:
                continue
            else:
                break
        except:
            if retry_times < retry:
                time.sleep(1)
                continue
            else:
                print("\x1b[2J")
                print(u"Network error!")
                sys.exit()      
    data = simplejson.loads(raw_data[0])
    '''
    data = {u'fundcode': u'000478', 
            u'name': u'\u5efa\u4fe1\u4e2d\u8bc1500\u6307\u6570\u589e\u5f3a', #名称
            u'dwjz': u'2.4543', #当前净值
            u'rzzl': u'-1.0403', #当前增长率
            u'gsz': u'2.4611', #估算净值
            u'gszzl': u'0.14', #估算增长率
            u'jzrq': u'2017-11-01', #净值日期
            u'gztime': u'2017-11-02 14:52' #估值时间
    }
    '''
    return data

def show_data(indexs, interval = 60):
    print("\x1b[2J")
    print(u"\x1b[1m\x1b[1;38H且慢估值投资基金估值（数据源：天天基金网）\x1b[0m")
    print(u"\x1b[1;36m\x1b[2;10H基金名称\x1b[0m")
    print(u"\x1b[1;36m\x1b[2;32H基金代码\x1b[0m")
    print(u"\x1b[1;36m\x1b[2;47H估值时间\x1b[0m")
    print(u"\x1b[1;36m\x1b[2;63H单位净值\x1b[0m")
    print(u"\x1b[1;36m\x1b[2;76H估值价格\x1b[0m")
    print(u"\x1b[1;36m\x1b[2;90H涨跌幅\x1b[0m")
    print(u"\x1b[1;36m\x1b[2;100H估值区间\x1b[0m")
    #
    fundidlist = []
    fundgroup = {}
    for index in indexs:
        fundid = FUNDS[index["indexCode"]]
        fundidlist.append(fundid)
        fundgroup[fundid] = index[u'group']
    codesnum = len(fundidlist)
    old_value = [0]*codesnum
    curr_value = [0]*codesnum
    #
    while(1):
        line_num = 3
        count = 0
        for fundid in fundidlist:
            data = get_data(fundid)
            '''
            {u'gztime': u'2017-11-03 04:00', u'name': u'\u534e\u5b9d\u6807\u666e\u77f3\u6cb9\u6307\u6570', u'gsz': u'0.5839', u'jzrq': u'2017-11-01', u'dwjz': u'0.5820', u'fundcode': u'162411', u'gszzl': u'0.33'}
            fundname = data['name']
            funddm = data['fundcode']
            fundgz = float(data['gsz'])
            fundjz = float(data['dwjz'])
            fundzzl = float(data['rzzl'])
            fundgszzl = float(data['gszzl'])
            date = data['gztime']
            '''
            date = data['gztime']
            print("\x1b[0;34m\x1b[%d;1H %s\x1b[0m" %(line_num, data['name']))
            print(u"\x1b[%d;65H\x1b[0;37m%2.4f\x1b[0m" %(line_num, float(data['dwjz'])))
            curr_value[count] = float(data['gsz'])
            if curr_value[count] != old_value[count]:
                print(u"\x1b[1;34m\x1b[%d;1H %s\x1b[0m" %(line_num, data['name']))
                print(u"\x1b[0;34m\x1b[%d;33H%6s\x1b[0m" %(line_num, data['fundcode']))
                print(u"\x1b[0;34m\x1b[%d;43H%16s\x1b[0m" %(line_num, date))
                old_value[count] = curr_value[count]
                if float(data['gszzl']) > 0: 
                    print(u"\x1b[%d;78H\x1b[0;31m%2.4f\x1b[0m" %(line_num, curr_value[count]))
                    print(u"\x1b[%d;88H\x1b[0;31m%7.2f%s\x1b[0m" %(line_num, float(data['gszzl']), '%'))
                elif float(data['gszzl']) < 0: 
                    print(u"\x1b[%d;78H\x1b[0;32m%2.4f\x1b[0m" %(line_num, curr_value[count]))
                    print(u"\x1b[%d;88H\x1b[0;32m%7.2f%s\x1b[0m" %(line_num, float(data['gszzl']), '%')) 
                else:
                    print(u"\x1b[%d;78H\x1b[0;37m%2.4f\x1b[0m" %(line_num, curr_value[count]))
                    print(u"\x1b[%d;88H\x1b[0;37m%7.2f%s\x1b[0m" %(line_num, float(data['gszzl']), '%'))
            if fundgroup[fundid] == u'LOW':
                print(u"\x1b[%d;100H\x1b[0;32m 可买" %line_num)
            elif fundgroup[fundid] == u'MID':
                print(u"\x1b[%d;100H\x1b[0;33m 观望" %line_num)
            elif fundgroup[fundid] == u'HIGH':
                print(u"\x1b[%d;100H\x1b[0;31m 不建议" %line_num)
            else:
                print(u"\x1b[%d;100H\x1b[0;34m NA" %line_num)
            line_num += 1 
            count += 1
        time.sleep(interval) 

if __name__ == "__main__":  
    indexs = get_indexs()
    try:
        show_data(indexs)
    except KeyboardInterrupt:
        print("Cancelled!")
        sys.exit()    


