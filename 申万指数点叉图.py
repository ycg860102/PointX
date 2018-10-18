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
    f.savefig(u'申万行业热力图.jpg', dpi=100, bbox_inches='tight')
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
    
    makeHeatMaps(20180701,20181018)
    
    #获取调仓周期，周期分为月度和周度可以选择
    now = datetime.datetime.now()  
    toDay = now.strftime('%Y%m%d')
    
    
    
    begd=TSLPy2.EncodeDate(2018,9,1)
    endd=TSLPy2.EncodeDate(2018,10,17)
    adjustPeriods = utility.getAdjustPeriods(begd,endd,u"月线")
    
    Path = datetime.datetime.now().strftime("%Y-%m-%d")
    makePath(Path)
    
    swhyzflist = []    
    for i in adjustPeriods.index[:-1]: 
        adjustDay = adjustPeriods.ix[i,"date"] 
        nextAdjustDay = adjustPeriods.ix[i,"nextAdjustDay"]   
        adjustDay = adjustDay.replace('-','')
        nextAdjustDay = nextAdjustDay.replace('-','')
        #调用天软接口，获取股票及所属行业信息
        stocks = TSLPy2.RemoteCallFunc('getStocksByDate',[int(adjustDay)],{}) 
        stocks = pd.DataFrame(stocks[1])
        stocks["SWNAME"] = stocks["SWNAME"].apply(lambda x:x.decode('gbk'))
        #调用天软接口，传入股票代码，获取股票在调仓期间涨跌情况
        stockzf = utility.getStockListPriceTSL(list(stocks["stockID"]),int(adjustDay),int(nextAdjustDay),'close') 
        stockzf = stockzf.pct_change().fillna(0) 
        #对涨跌情况进行处理，获取股票期间净值情况
        stockProdDatas = (stockzf.ix[1:,:]+1).cumprod().T 
        #对股票增加所属行业情况
        #stockProdDatas["SWNAME"] = stockProdDatas.index.map(stocks.set_index('stockID')["SWNAME"])
        #按照股票所属行业分组，求均值得到指数净值，再讲净值反推计算涨跌幅
        swhyzf = stockProdDatas.groupby(stocks.set_index('stockID')["SWNAME"]).mean().T.reindex(stockzf.index).fillna(1).pct_change().dropna()
        #将每一期数据放入列表中
        swhyzflist.append(swhyzf)
    #合并每一期分组涨跌数据
    swhyzfALL = pd.concat(swhyzflist)
    #通过分组涨跌情况，计算净值
    swhyNetValues = (swhyzfALL[stocks["SWNAME"].drop_duplicates()]+1).cumprod()*1000
    #增加起始日期数据，并设置为1000
    swhyNetValues = swhyNetValues.reindex(swhyNetValues.index.insert(0,adjustPeriods.ix[0,0]),fill_value=1000) 
    
    Nlist = [1,]
    #PointX.dealAndPlot(swhyNetValues,Path,Nlist)
    
    #计算行业相对强弱点叉图
    datas = PointX.DataTORS(swhyNetValues) 
    #新建行业强弱路径
    Path+=u'/行业RS'
    makePath(Path)
    #处理数据，并对数据进行画图
    results = PointX.dealAndPlot(datas,Path,Nlist) 
    
    sz = results[u'上涨'].dropna() 
    xd = results[u'下跌'].dropna() 
    szlist = list()
    szlist.append(sz.apply(lambda x :x.split('_')[0]))
    szlist.append(xd.apply(lambda x :x.split('_')[1]))
    
    xdlist = list()
    xdlist.append(sz.apply(lambda x :x.split('_')[1]))
    xdlist.append(xd.apply(lambda x :x.split('_')[0]))
    pd.concat(szlist).value_counts().to_excel(Path+u"/上涨行业汇总统计.xlsx")
    pd.concat(xdlist).value_counts().to_excel(Path+u"/下跌行业汇总统计.xlsx")
    

    
