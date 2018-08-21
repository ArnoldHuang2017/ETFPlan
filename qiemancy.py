#!/usr/bin/python -u
# -*- coding: UTF-8 -*- 
import requests
import simplejson
import sys
#import os
import hashlib
import random
import time
import re
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
'''
fundidlist = [
              '000216',\
              '162411',\
              '000478',\
              '050027',\
              '270048',\
              '003376',\
              '001052',\
              '110026',\
              '100032',\
              '502010',\
              '004752',\
              #'001061',\
              '001064',\
              '163114',\
              '000071',\
              '001051',\
              '000968',\
              '001180',\
              '160416',\
              '000051',\
              '003765',\
              '110031',\
             ]
#             
fundidlist = [u'001064', u'160119', u'110031', u'001180', u'000942', u'110026', u'090010', u'001133', u'004593', u'501029', u'202017', u'161118', u'001051', u'240014', u'202015', u'050024', u'000071', u'001460', u'110019', u'000834', u'001458', u'050025', u'001594', u'501050', u'004642', u'502010', u'003318', u'000968', u'000596']
'''
interval = 60
retry = 10
#
def get_x_sign(url, len = 32):
    random_value = random.sample(["0","1","2","3","4","5","6","7","8","9"], 1)
    curtime =  str(time.time()).replace('.', '') + random_value[0]
    target = str("%f")%(float(curtime)*1.01)
    target = target[0:13]
    sha256 = hashlib.sha256()
    sha256.update(target.encode('utf-8'))
    target_sha256 = sha256.hexdigest().upper()
    x_sign = curtime + target_sha256[0:len]
    #
    #time.sleep(0.01)
    #newtime =  str(time.time()).replace('.', '') + random_value[0]
    n = str(random.random()) + str(random.randint(1000,9999))
    userAgent = "5011866453736630323913253736"
    target = str(n) + curtime + url + userAgent
    sha256.update(target.encode('utf-8'))
    target_sha256 = sha256.hexdigest().upper()
    x_request_id = target_sha256[-20]
    return x_sign, x_request_id

#get all fund ids
def get_funds(retry = 10):
    headers = {"Accept" : "application/json",
        "Accept-Encoding" : "gzip, deflate, br",
        "Accept-Language" : "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        "Connection" : "keep-alive",
        "Host" : "qieman.com",
        "Referer" : "https://qieman.com/longwin/index",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36",
        "x-aid" : "GA1.2.999152452.1516692586",
        #"x-aid" : "GA1.2.999152452.1516692587",
       "x-request-id" : "",
        "x-sign" : "",
        }
    funds_pattern = re.compile('"fund":({.*?})')
    while retry > 0:
        retry -= 1
        headers["x-sign"], headers["x-request-id"] = get_x_sign(headers["Referer"])
        return_data = requests.get("https://qieman.com/pmdj/v2/long-win/plan", headers=headers, verify=False)
        fundlists = funds_pattern.findall(return_data.text)
        print fundlists
        funds = []
        for fund in fundlists:
            fund = simplejson.loads(fund)
            if len(fund['fundCode']) == 6: 
                funds.append(fund['fundCode'])
        if len(funds) == 0 and retry !=0:
            time.sleep(1)
            continue
        elif len(funds) == 0 and retry == 0:
            print u"无法获取基金列表，请重新运行程序！"
            sys.exit()
        else:
            break
    funds.remove('001061')
    funds.remove('000614')
    funds.remove('501018')
    return list(set(funds))
         
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
            return_data = requests.get("http://fundgz.1234567.com.cn/js/%s.js?rt=%s" %(fundid, curtime), headers=headers)
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
                print "\x1b[2J"
                print u"Network error!"
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

def show_data(fundidlist, interval = 60):
    print "\x1b[2J"
    print u"\x1b[1m\x1b[1;30H且慢长赢指数基金估值（数据源：天天基金网）\x1b[0m"
    print u"\x1b[1;36m\x1b[2;10H基金名称\x1b[0m"
    print u"\x1b[1;36m\x1b[2;32H基金代码\x1b[0m"
    print u"\x1b[1;36m\x1b[2;47H估值时间\x1b[0m"
    print u"\x1b[1;36m\x1b[2;63H单位净值\x1b[0m"
    print u"\x1b[1;36m\x1b[2;76H估值价格\x1b[0m"
    print u"\x1b[1;36m\x1b[2;90H涨跌幅\x1b[0m"
    #
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
            print "\x1b[0;34m\x1b[%d;1H %s\x1b[0m" %(line_num, data['name'])
            print u"\x1b[%d;65H\x1b[0;37m%2.4f\x1b[0m" %(line_num, float(data['dwjz']))
            curr_value[count] = float(data['gsz'])
            if curr_value[count] != old_value[count]:
                print u"\x1b[1;34m\x1b[%d;1H %s\x1b[0m" %(line_num, data['name'])
                print u"\x1b[0;34m\x1b[%d;33H%6s\x1b[0m" %(line_num, data['fundcode'])
                print u"\x1b[0;34m\x1b[%d;43H%16s\x1b[0m" %(line_num, date)
                old_value[count] = curr_value[count]
                if float(data['gszzl']) > 0: 
                    print u"\x1b[%d;78H\x1b[0;31m%2.4f\x1b[0m" %(line_num, curr_value[count])
                    print u"\x1b[%d;88H\x1b[0;31m%7.2f%s\x1b[0m" %(line_num, float(data['gszzl']), '%')
                elif float(data['gszzl']) < 0: 
                    print u"\x1b[%d;78H\x1b[0;32m%2.4f\x1b[0m" %(line_num, curr_value[count])
                    print u"\x1b[%d;88H\x1b[0;32m%7.2f%s\x1b[0m" %(line_num, float(data['gszzl']), '%')    
                else:
                    print u"\x1b[%d;78H\x1b[0;37m%2.4f\x1b[0m" %(line_num, curr_value[count])
                    print u"\x1b[%d;88H\x1b[0;37m%7.2f%s\x1b[0m" %(line_num, float(data['gszzl']), '%')
            if fundid == '163114':
                line_num += 1 
                mark = "----------------------------------------------------------------------------------------------"
                print u"\x1b[%d;1H %s" %(line_num, mark)
            line_num += 1 
            count += 1
        time.sleep(interval) 
    
if __name__ == "__main__":
    fundidlist = get_funds()
    try:
        show_data(fundidlist, interval)
    except KeyboardInterrupt:
        print "Cancelled!"
        sys.exit()    

            
