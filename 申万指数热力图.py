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
import seaborn as sns
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

def makePath(Path):
    if os.path.exists(Path)  and os.access(Path, os.R_OK):
        print Path , ' is exist!' 
    else:
        os.makedirs(Path) 

def plotHeatFig(rankData,title):
    f, ax= plt.subplots(figsize = (14, 10))
    sns.heatmap(rankData,cmap='RdYlGn', linewidths = 0.05, ax = ax,annot=True )
    ax.set_title(title)
    f.savefig(title+".jpg", dpi=100, bbox_inches='tight')
    plt.close()
    
def makeHeatMaps(begD,endD):
    #输入股票列表，以及开始时间和结束时间，先提取收盘价信息，在计算涨跌幅，然后根据行业分组计算每日分组涨跌幅。
    #将行业分组数据每日排序，将排序结果进行画图
    stocks = TSLPy2.RemoteCallFunc('getStocksByDate',[begD],{}) 
    stocks = pd.DataFrame(stocks[1])
    stocks["SWNAME"] = stocks["SWNAME"].apply(lambda x:x.decode('gbk'))
    stockzf = utility.getStockListPriceTSL(list(stocks["stockID"]),begD,endD,'close') 
    stockzf = stockzf.pct_change().fillna(0) 
    rankData = stockzf.ix[1:,:].T.groupby(stocks.set_index('stockID')["SWNAME"]).mean().rank(ascending=False)
    title = u"{0}至{1}日 申万行业热力图".format(begD,endD)
    plotHeatFig(rankData,title)

if __name__ == "__main__":
    
    makeHeatMaps(20180901,20181018) 
    

    

    
