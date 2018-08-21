#!/usr/bin/python
# -*- coding: utf-8 -*- 
##############################
#Filename: Super-etfbuyer-v3.py
#Author:   Arnold Huang
#Email:    fugaohx@163.com
#Date:     2018.8.21
#Data file download path: https://rdl.oss-cn-hongkong.aliyuncs.com/dl/history.csv
#History:   2018.2.7  Initial Draft
#           2018.2.14 Initial Release V1.0
#           2018.3.11 V2.0 增加分红信息分析和复权净值处理
#           2018.8.21 V3.0 Add multithreading to download and analyze the funds more quickly.
##############################


import csv
import time
import datetime
import re
import requests
import simplejson
import random
import sys
import threading 

threads = []
bs_database=[]
fundCode_list=[]
reload(sys)
sys.setdefaultencoding('utf-8')

def read_csv_data(filename="history.csv"):
    with open(filename) as f:
        reader = csv.reader(f)
        keys = next(reader)
        for values in reader:
            record = dict(zip(keys,values ))
            bs_database.append(record)        
            fundCode = record["fundCode"]
            if fundCode not in fundCode_list:
                fundCode_list.append(fundCode)
    #fundCode_list.remove("100032")
    fundCode_list.remove("003376")
    fundCode_list.remove("001061")
    fundCode_list.remove("270048")
    fundCode_list.remove("050027")
    fundCode_list.remove("000216")
    fundCode_list.remove("501018")
    fundCode_list.remove("000614")
    fundCode_list.remove("000071")
    fundCode_list.remove("162411")
    fundCode_list.remove("160416")

def cal_time(date1,date2):
    date1 = time.strptime(date1,"%Y-%m-%d %H:%M:%S")
    date2 = time.strptime(date2,"%Y-%m-%d %H:%M:%S")
    date1 = datetime.datetime(date1[0], date1[1], date1[2], date1[3], date1[4], date1[5])
    date2 = datetime.datetime(date2[0], date2[1], date2[2], date2[3], date2[4], date2[5])
    return (date2-date1).days

def get_fhsp_data(fundCode, startdate):
    headers_data = {
         "Host" : "fund.eastmoney.com",
         "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:58.0) Gecko/20100101 Firefox/58.0",
         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
         "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
         "Accept-Encoding": "gzip, deflate",
         "Connection": "keep-alive",
         "Upgrade-Insecure-Requests": "1",
         "Cache-Control":"max-age=0",
    }

    url = "http://fund.eastmoney.com/f10/fhsp_"+fundCode+".html"
    return_data = requests.get(url, headers = headers_data)
    fhsp_pattern = re.compile(u"<td>(\d{4}-\d{2}-\d{2})</td><td>每份派现金(\d*\.\d{4})元</td>")
    tmp = fhsp_pattern.findall(return_data.text)

    retval=[]
    for i in range(0, len(tmp)):
        delta_days = cal_time(startdate,tmp[i][0]+" 15:00:00")
        if delta_days > 0 :
            retval.append(tmp[i])
    
    retval.reverse()
    return retval

def get_history_data(fundCode, startdate):
    headers_data = {
        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding" : "gzip, deflate, br",
            "Accept-Language" : "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
            "Connection" : "keep-alive",
            "Cache-Control" : "no-cache", 
            "Pragma" : "no-cache",
            "Upgrade-Insecure-Requests" : "1",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:58.0) Gecko/20100101 Firefox/58.0"
    }

    enddate = time.strftime('%Y-%m-%d',  time.localtime(time.time())) + " 15:00:00"
    startdate = startdate.split(" ")[0] + " 15:00:00"
    delta_days  = cal_time(startdate, enddate);

    url = "http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code="+fundCode+"&page=1&per="+str(delta_days)+"&sdate=" + startdate+ "&edate=" + enddate

    history_data = requests.get(url, headers = headers_data)
    html = history_data.text.split("<tr>")
    history = []
    history_pattern = re.compile(r"<td>(\d{4}-\d{2}-\d{2})</td><td class='tor bold'>(\d*.\d{4})</td>.*")
    	
    for i in range(2, len(html)):
        history.append( history_pattern.findall(html[i]) )

    return history 

def get_fund_today_price(fundCode, retry=10):
    headers_data = {
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q",
            "Accept-Encoding" : "gzip, deflate",
            "Accept-Language" : "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Cache-Control" : "max-age=0",
            "Connection" : "Keep-alive",
            "Host" : "fundgz.1234567.com.cn",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:58.0) Gecko/20100101 Firefox/58.0"
            }
    for retry_times in range(0, retry+1):
        try:
            random_value = random.sample(["0", "1", "2","3","4","5","6","7","8","9"],1)
            current_time = str(time.time()).replace('.','') + random_value[0]
            url = "http://fundgz.1234567.com.cn/js/%s.js?rt=%s" % (fundCode, current_time)
            return_data  = requests.get( url, headers= headers_data)
            raw_data     = re.findall("jsonpgz\((.*)\)", return_data.text)
            if len(raw_data) != 0 :
                break
            else:
                continue
        except:
            if retry_times < retry:
                time.sleep(1)
                continue
            else:
                print u"Network error!"
                sys.exit()
    data = simplejson.loads(raw_data[0])
    fundName = data["name"]
    currentPrice = data["gsz"]
    return fundName, currentPrice 

def get_nav_rate(buyrecord, fhsp_data, history_data):
    buy_date = buyrecord["navDate"]
    nav_rate = 1;

    for fhsp in fhsp_data:
        fhsp_date = fhsp[0]
        fhsp_money = float(fhsp[1])

        if cal_time(buy_date + " 15:00:00" ,  
            fhsp_date + " 15:00:00") > 0:
            #如果在购买日期之后找到分红信息，形成阶段性涨幅
            #寻找分红之日的净值信息

            for history in history_data:
                history_date = history[0][0]
                history_value = float(history[0][1])
                if history_date == fhsp_date:
                    #阶段性涨幅相乘即复权率
                    rate_in_this_phase =  (history_value + fhsp_money )/ history_value
                    nav_rate = nav_rate * rate_in_this_phase

    return float("%.4f" % nav_rate)

def analyze_fund(fundCode):
    buy_records = []
    sell_records = []
    suggest_records = []
    buy_count = 0
    sell_count = 0
    buyOrderCode = "022"
    sellOrderCode = "024"
    print "Analyzing %s... " % fundCode
    #Grep target fundcode
    for bs_record in bs_database:
        if (bs_record["fundCode"] == fundCode and bs_record["orderCode"] == buyOrderCode):
            cnt = bs_record["tradeUnit"]
            buy_count = buy_count + int(cnt)
            if (cnt == "1"):
                buy_records.append(bs_record)
            else:
                bs_record["tradeUnit"] = "1"
                for i in range(0, int(cnt)):
                    buy_records.append(bs_record)
             
    for bs_record in bs_database:
        if (bs_record["fundCode"] == fundCode and bs_record["orderCode"] == sellOrderCode):
            cnt = bs_record["tradeUnit"]
            sell_count = sell_count + int(cnt)


    buy_records.sort(key=lambda x:(x['navDate']))
	
    start_datetime = buy_records[0]['navDate'] + " 15:00:00"
    history_data = get_history_data(fundCode, start_datetime)
    fhsp_data = get_fhsp_data(fundCode, start_datetime)
	
    buy_records.sort(key=lambda x:(x['nav']))
    sell_records.sort(key=lambda x:(x['nav']))

    fundname, current_price = get_fund_today_price(fundCode)
 
    for i in range(0, sell_count):
        buy_records.pop()
    
    suggest_cnt = 0
    nav_records = []

    #####处理复权净值##################
  	
    for record in buy_records:
        nav_rate = get_nav_rate(record, fhsp_data, history_data)
        nav_record = {}
        nav_record["nav"] = float( "%.4f" % (float(record["nav"]) / nav_rate)) 
        nav_record["navDate"] = record["navDate"]
        nav_records.append(nav_record)

    #print nav_records
    #print current_price

    for record in nav_records:
        if record["nav"] > float(current_price):
            suggest_records.append(record)
            suggest_cnt = suggest_cnt +  1

    return fundname , current_price, suggest_cnt, suggest_records    

suggestion1=""
suggestion2=""
suggestion_lock=threading.Lock()


def check_one_fund(fundCode):
    global suggestion1
    global suggestion2
    global suggestion_lock
    fundname , current_price, suggest_cnt, suggest_records = analyze_fund(fundCode)
    suggestion_lock.acquire()
    if suggest_cnt == 0:
        suggestion1 += u"(%s) %s 不建议补仓\n" % (fundCode, fundname)
    else:
        suggestion2 += u"(%s) %s 基于空仓补仓%d份 当前价格 %s\n" % (fundCode, fundname, suggest_cnt, current_price)
        for item in suggest_records:
            suggestion2 += u"\t历史购买日期%s: 复权净值: %s\n" % (item["navDate"], item["nav"])
        suggestion2 += "=================================\n"
    suggestion_lock.release()



def analyze_all_funds():
    print u"严正声明!"
    print u"本程序是用于长赢计划中国A股部分的基于空仓状态下的补仓建议。您实际需要补仓的份数=空仓补仓份数-当前持仓份数"
    print u"此外，为了尽量获得准确的每日结算估值，请参考本程序在北京时间14：30到14:50之间的运行结果！如果需要补仓，给自己留足够的时间到交易软件购买基金。"
    print u"本程序的输出内容不构成任何的投资指导，股市有风险，入市需谨慎！风险自担！"
    print u"由此造成的补仓成本过高，本程序作者和网站负责人不承担任何责任！"

    
    for fundCode in fundCode_list:
        tid = threading.Thread(target=check_one_fund, args=(fundCode, ))       
        threads.append(tid)

    for t in threads:
        t.start()
 
    
    for t in threads:
        t.join()
        
    print suggestion1
    print suggestion2
    print u"严正声明!"
    print u"本程序是用于长赢计划中国A股部分的基于空仓状态下的补仓建议。您实际需要补仓的份数=空仓补仓份数-当前持仓份数"
    print u"此外，为了尽量获得准确的每日结算估值，请参考本程序在北京时间14：30到14:50之间的运行结果！如果需要补仓，给自己留足够的时间到交易软件购买基金。"
    print u"本程序的输出内容不构成任何的投资指导，股市有风险，入市需谨慎！风险自担！"
    print u"由此造成的补仓成本过高，本程序作者和网站负责人不承担任何责任！"


read_csv_data()
analyze_all_funds()
