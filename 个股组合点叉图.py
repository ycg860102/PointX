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
    now = datetime.datetime.now()  
    toDay = now.strftime('%Y%m%d')
    
    begd=20180101
    endd=20181011
    #adjustPeriods = utility.getAdjustPeriods(begd,endd,u"月线")
    
    Path = datetime.datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(Path)  and os.access(Path, os.R_OK):
        print Path , ' is exist!' 
    else:
        os.makedirs(Path) 
    
    stocks = pd.read_excel(u'个股组合.xlsx')
    #调用天软接口，传入股票代码，获取股票在调仓期间涨跌情况
    stockclose = utility.getStockListPriceTSL(list(stocks["stockID"]),int(begd),int(endd),'close') 

    Nlist = [1,]
    #计算个股点叉图
    PointX.dealAndPlot(stockclose,Path,Nlist)

    
    
