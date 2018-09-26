# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 16:02:00 2018

@author: yangchg

    1、通过天软调取申万各行业市值前20%的股票组成组合。
    2、每月调仓一次，然后计算当月组合净值涨跌。
    3、将每月涨跌汇总，得到净值序列

"""
import pandas as pd
import numpy as np 
#import tushare as ts 
#import seaborn as sns
import matplotlib.pyplot as plt 
import datetime

from math import isnan 
import os
from multiprocessing import Pool
import WindPy as wp 
import PointXTool as PointX
from sqlalchemy import create_engine 

import sys
sys.path.append("D:\Program Files\Tinysoft\Analyse.NET") 
sys.path.append("D:\FactorDataBase\TF")
reload(sys)    
sys.setdefaultencoding('utf8')
import TSLPy2
import utility

if __name__ == "__main__":
    #获取调仓周期，周期分为月度和周度可以选择
    begd=TSLPy2.EncodeDate(2018,8,1)
    endd=TSLPy2.EncodeDate(2018,9,7)
    adjustPeriods = utility.getAdjustPeriods(begd,endd,u"月线")
    
    Path = datetime.datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(Path)  and os.access(Path, os.R_OK):
        print Path , ' is exist!' 
    else:
        os.makedirs(Path) 
        
    for i in adjustPeriods.index[:-1]: 
        adjustDay = adjustPeriods.ix[i,"date"] 
        nextAdjustDay = adjustPeriods.ix[i,"nextAdjustDay"]   
        adjustDay = adjustDay.replace('-','')
        nextAdjustDay = nextAdjustDay.replace('-','')
        stocks = TSLPy2.RemoteCallFunc('getStocksByDate',[int(adjustDay)],{}) 
        stocks = pd.DataFrame(stocks[1])
        stocks["SWNAME"] = stocks["SWNAME"].apply(lambda x:x.decode('gbk'))
        stockzf = utility.getStockListPriceTSL(list(stocks["stockID"]),int(adjustDay),int(nextAdjustDay),'stockzf') 
        
        