# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 09:03:07 2018

@author: yangchg

说明:根据股票收盘价绘制点叉图。
    1、找到最近状态符合买入模式和卖出模式的点；
    2、如果属于卖出模式，找出最近的一阶下降枢纽拐点，并绘制阻力线；
    3、如果属于买入模式，找出最近的一阶上涨拐点，并绘制支撑线。
    4、判断当前价格是否已经跌破支撑或者突破阻力，如果符合条件，则不用绘制支撑或者阻力线。
    5、根据压力支撑线判断空头和多头状态：
        ①如果有支撑线，没有阻力线，则目前状态属于多头状态；
        ②如果有阻力线，没有支撑线，则处于空头状态；
        ③既有阻力又有支撑，则处于震荡整理阶段                        

    20180921 修改获取股价信息为通过天软获取

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
reload(sys)    
sys.setdefaultencoding('utf8')
import TSLPy2

def getGraduation(price):
    if price <=5 :
        return 0.06
    elif price <=10 :
        return 0.125
    elif price <=20 :
        return 0.25
    elif price <=50:
        return 0.5
    elif price <=100:
        return 1.0
    elif price<=200:
        return 2.5
    elif price<=1000:
        return 5
    else:
        return 20

def DealDataHL( titleName, sourceDatas,MinSize = 0.05 ):
    #函数说明：如果上涨阶段，反转的条件有两种： 1、最高价没有创新高，则当天最高价比前一列最高价低三个维度 
    #         如果下跌阶段，反转的条件有两种： 1、最低价没有创新低，当天最低价比前一列的最低价高三个维度  
    tmpDF = pd.DataFrame()    
    YouBiao = 1
    
    Flag = 0 #上涨表示1，下跌表示-1  
    tmpLen = 0

    MinSize = getGraduation(sourceDatas['close'][0])

    #初始化第一天数据    
    if sourceDatas['close'][0] >= sourceDatas['open'][0] :
        Flag = 1 
        tmpLen = int( (sourceDatas['close'][0] - sourceDatas['open'][0]) / MinSize)
        
        for j in xrange(tmpLen+1):
            tmp = pd.DataFrame({'X':YouBiao,
                                'Y':j*MinSize + sourceDatas['open'][0],
                                'Label' : Flag,
                                'date':sourceDatas['date'][0]},index=['0'])
            tmpDF = tmpDF.append(tmp,ignore_index=True)
    else:
        Flag = -1  
        tmpLen = int( (sourceDatas['open'][0] - sourceDatas['close'][0]) / MinSize )
        
        dataFrameList =  [ pd.DataFrame({'X':YouBiao,
                                'Y':sourceDatas['close'][0] - j*MinSize,
                                'Label':Flag,
                                'date':sourceDatas['date'][0]},index=['0']) for j in xrange(tmpLen+1) ]        
        tmp = pd.concat(dataFrameList) 
        tmpDF = tmpDF.append(tmp,ignore_index=True)        
             
    #从第二天开始循环处理
    for i,item in sourceDatas[1:].iterrows() : 
        
        MinSize = getGraduation(item['close'])  
        
        tmpMax = tmpDF[tmpDF['X']==YouBiao]['Y'].max() 
        tmpMin = tmpDF[tmpDF['X']==YouBiao]['Y'].min()
        
        if Flag == 1 and item['high'] >= tmpMax:
            
            tmpLen = int( (item['high'] - tmpMax) / MinSize) 
            #tmpLen2 = int( (item['high'] - item['close']) / MinSize) 
            
            dataFrameList = [ pd.DataFrame({'X':YouBiao,
                                'Y':(1+j)*MinSize + tmpMax,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0']) for j in xrange(tmpLen) ]
                
            if len(dataFrameList)>0:            
                tmp = pd.concat(dataFrameList) 
                tmpDF = tmpDF.append(tmp,ignore_index=True)
            """    
            if i==sourceDatas[-1:].index.values[0] and tmpLen2>=3 :
                YouBiao+=1 #新开一列 
                Flag=-1
                dataFrameList =  [ pd.DataFrame({'X':YouBiao,
                                'Y': tmpDF[tmpDF['X'] == YouBiao-1]['Y'].max() - (1+j)*MinSize,
                                'Label':Flag,
                                'date':item['date'] 
                                },index=['0'])  for j in xrange(tmpLen2) ]             
                if len(dataFrameList)>0 :            
                     tmp = pd.concat(dataFrameList) 
                     tmpDF = tmpDF.append(tmp,ignore_index=True) 
            """
            
        elif Flag == 1 and item['high'] < tmpMax: 
             #tmpLen = int((tmpMax - item['high']) / MinSize) 
             tmpLen2 = int( ( tmpMax - item['low'] ) / MinSize) 
                     
             if tmpLen2>=3 : 
                YouBiao+=1 #新开一列 
                Flag=-1
                dataFrameList =  [ pd.DataFrame({'X':YouBiao,
                                'Y': tmpDF[tmpDF['X'] == YouBiao-1]['Y'].max() - (1+j)*MinSize,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0'])  for j in xrange(tmpLen2) ]             
                if len(dataFrameList)>0 :            
                     tmp = pd.concat(dataFrameList) 
                     tmpDF = tmpDF.append(tmp,ignore_index=True)     
              
        elif Flag == -1 and item['low'] <= tmpMin:
             tmpLen = int(( tmpMin -item['low']) / MinSize)
             #tmpLen2 = int((item['close'] - item['low']) / MinSize) 
            
             dataFrameList =  [  pd.DataFrame({'X':YouBiao,
                                'Y':tmpMin - (1+j)*MinSize ,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0'])  for j in xrange(tmpLen) ]             
             if len(dataFrameList)>0:            
                 tmp = pd.concat(dataFrameList) 
                 tmpDF = tmpDF.append(tmp,ignore_index=True)              
             """    
             if  i==sourceDatas[-1:].index.values[0] and tmpLen2 >=3 : 
                 YouBiao+=1  #新开一列  
                 Flag=1
                 dataFrameList =  [ pd.DataFrame({'X':YouBiao,
                                'Y': tmpDF[tmpDF['X'] == YouBiao-1]['Y'].min() + (1+j)*MinSize,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0'])  for j in xrange(tmpLen2) ]     
                                
                 if len(dataFrameList)>0:
                     tmp = pd.concat(dataFrameList) 
                     tmpDF = tmpDF.append(tmp,ignore_index=True) 
             """
        elif Flag == -1 and item['low'] > tmpMin:  
              #tmpLen = int((item['low'] - tmpMin) / MinSize) 
              tmpLen2 = int((item['high'] - tmpMin) / MinSize)
                      
              if tmpLen2 >=3 : 
                 YouBiao+=1  #新开一列  
                 Flag=1
                 dataFrameList =  [ pd.DataFrame({'X':YouBiao,
                                'Y': tmpDF[tmpDF['X'] == YouBiao-1]['Y'].min() + (1+j)*MinSize,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0'])  for j in xrange(tmpLen2) ]     
                                
                 if len(dataFrameList)>0:
                     tmp = pd.concat(dataFrameList) 
                     tmpDF = tmpDF.append(tmp,ignore_index=True)           
    return tmpDF    
     
def getCloseData(arg="close",endDay="2017-09-21"):
    
    wp.w.start()
    concepts = wp.w.wset("SectorConstituent",u"date=20170726;sector=WIND概念板块指数") 
    df = wp.w.wsd(concepts.Data[1], arg, "2017-01-01", endDay, "Fill=Previous;Currency=CNY;PriceAdj=F")
    df2array = np.array(df.Data)
    return pd.DataFrame(df2array.T,index=df.Times,columns=df.Codes) 

def getStockListClosePrice(Stocklist,begDay,endDay,args):
    wp.w.start()
    
    df = wp.w.wsd(Stocklist, args, begDay, endDay, "Fill=Previous;Currency=CNY;PriceAdj=F")
    df2array = np.array(df.Data)
    return pd.DataFrame(df2array.T,index=df.Times,columns=df.Codes)


def getStockListPriceTSL(Stocklist,begDay,endDay,args) :
    prices= TSLPy2.RemoteCallFunc('getStocksPrice',[Stocklist,begDay,endDay,args],{})   
    prices = prices[1]
    return pd.DataFrame(prices).T 
   
def findZCZLLine(data1,N,isFindMax=0,isFindMin=0,startXtoEnd=0):
    #增加趋势线，1、找到4阶枢纽拐点，2，枢纽拐点往右新增一格，增加或减少一个graduation，直到最早一天数据
    
    data2 = data1[data1["X"]<=(data1['X'].max()-startXtoEnd)]
    groupedData1 = data2.groupby(by='X') 
    lenGroupedData1 = len(groupedData1) 
    
    lineDatas =[] 
    zhichengline = []  #支撑线--上涨趋势线 
    zuliline = []    #阻力线--下降趋势线 
    if lenGroupedData1>=2*N+1 :
        for i in range(lenGroupedData1-(2*N+1)  ):
            #当没有找到拐点时，从分组的最新端往前移动，如果分组的最大值等于
            if isFindMax==0 and max(groupedData1.max()[lenGroupedData1-i-(2*N+1) :lenGroupedData1-i]['Y'] ) \
            ==groupedData1.max()['Y'][lenGroupedData1-i-(N+1):lenGroupedData1-i-N].values[0]:
                #将graduation 设置为各组序列最大值的均值代入寻找graduation函数。
                graduation1 = getGraduation(np.mean(groupedData1.max()[lenGroupedData1-i-(2*N+1) :lenGroupedData1-i]['Y'] ))
            
                maxPointY = groupedData1.max()['Y'][lenGroupedData1-i-(N+1):lenGroupedData1-i-N].values[0]+graduation1
                maxPointX = groupedData1.max()['Y'][lenGroupedData1-i-(N+1):lenGroupedData1-i-N].index.values[0]
                lineDataX = [maxPointX, data1['X'].max()] 
                detaGra = data1.groupby(by='X').max().apply(lambda x : getGraduation(x.Y),axis=1)[maxPointX:].sum()
                lineDataY = [maxPointY ,maxPointY - detaGra]
                zuliline=[lineDataX,lineDataY]
                if data1.Y.iloc[-1] > maxPointY - detaGra :
                    zuliline=[]
                isFindMax=1 
                
            
            if isFindMin==0 and min(groupedData1.min()[lenGroupedData1-i-(2*N+1):lenGroupedData1-i]['Y'] ) \
            ==groupedData1.min()['Y'][lenGroupedData1-i-(N+1):lenGroupedData1-i-N].values[0] :
                #将graduation 设置为各组序列最小值的均值代入寻找graduation函数。
                graduation1 = getGraduation(np.mean(groupedData1.min()[lenGroupedData1-i-(2*N+1) :lenGroupedData1-i]['Y'] ))
                minPointY = groupedData1.min()['Y'][lenGroupedData1-i-(N+1):lenGroupedData1-i-N].values[0]-graduation1
                minPointX = groupedData1.min()['Y'][lenGroupedData1-i-(N+1):lenGroupedData1-i-N].index.values[0]    
                lineDataX = [minPointX,data1['X'].max()]
                detaGra = data1.groupby(by='X').min().apply(lambda x : getGraduation(x.Y),axis=1)[minPointX:].sum()
                lineDataY = [minPointY,minPointY + detaGra] 
                zhichengline= [lineDataX,lineDataY]   
                if data1.Y.iloc[-1] < minPointY + detaGra :
                    zhichengline=[]                     
                isFindMin=1 
            if isFindMin ==1 and isFindMax==1 : 
                break
    if len(zuliline):                    
        lineDatas.append(zuliline) 
        
    if len(zhichengline): 
        lineDatas.append(zhichengline)
         
    return lineDatas
   
   
if __name__ == "__main__":
    
    print "Begining ------>" 
    engine = create_engine('mysql://root:root@127.0.0.1/dwlh?charset=utf8')#用sqlalchemy创建引擎  
    now = datetime.datetime.now()  

    toDay = now.strftime('%Y%m%d')
    #toDay = "2017-12-12"
    
    #下面的90，代表九十天前 365天为过去一年暑假
    begDay = now + datetime.timedelta(days=-365)
    begDay = begDay.strftime('%Y%m%d')
    #begDay='2017-05-10'
    #closeData = getCloseData("close",toDay)
    #填写需要计算的股票代码    
    
    #stockList =  ['600132.SH','000848.SZ'] 
    #bk = u'沪深300'
    bk = u'中证800'
    stockList = TSLPy2.RemoteCallFunc('getbk',[bk],{})   
    stockList =  stockList[1]

    #stockList = [ stock[2:8]+'.'+stock[0:2] for stock in stockList ] 
    #,'601318.SH','002883.SZ','600066.SH','603578.SH']     
    #stockList =  ['600578.SH','600172.SH','000848.SZ','600993.SH','600446.SH','600519.SH']
    stockList =  ['SH000001','SH000300','SZ399006','SH000016','SZ399673']
    #stockList =  ['601328.SH','000001.SZ','600015.SH','000932.SZ','600782.SH','600282.SH','600022.SH','000959.SZ','600569.SH','600507.SH','000778.SZ','600126.SH','300003.SZ','002223.SZ','603658.SH','300463.SZ','300529.SZ','600529.SH','002022.SZ','601233.SH','603225.SH','600810.SH','002064.SZ','002206.SZ','300122.SZ','000661.SZ','002252.SZ','600161.SH','300294.SZ','300485.SZ','300009.SZ','600118.SH','300456.SZ','600138.SH','603869.SH','300178.SZ','000547.SZ','002482.SZ','300506.SZ','002713.SZ','600511.SH','000028.SZ','002589.SZ','603368.SH','002092.SZ','600409.SH','000683.SZ','603077.SH','000822.SZ','002648.SZ','600618.SH','600277.SH','600328.SH','601158.SH','000544.SZ','600820.SH','600326.SH','600512.SH','600502.SH','002460.SZ','000960.SZ','600392.SH','002716.SZ','600459.SH','600585.SH','600801.SH','000401.SZ','002233.SZ','600720.SH','000672.SZ','603986.SH','600667.SH','603501.SH','300373.SZ','002371.SZ','002049.SZ','600460.SH','601766.SH','000008.SZ','600970.SH','002051.SZ','000065.SZ','600496.SH','000636.SZ','603328.SH','002815.SZ','300476.SZ','600563.SH','002138.SZ','002463.SZ','600580.SH','000922.SZ','603988.SH','601966.SH','601058.SH','002068.SZ','300144.SZ','002310.SZ','300197.SZ','002717.SZ','300237.SZ','300349.SZ','300410.SZ','300114.SZ','002658.SZ','300572.SZ','300066.SZ'] 
    #N=2
    Nlist = [1,]
    closeData = getStockListPriceTSL(stockList,int(begDay),int(toDay),'close') 
    highData = getStockListPriceTSL(stockList,int(begDay),int(toDay),'high') 
    lowData = getStockListPriceTSL(stockList,int(begDay),int(toDay),'low') 
    openData = getStockListPriceTSL(stockList,int(begDay),int(toDay),'open') 
    
    now = datetime.datetime.now()     
    print now.strftime('%Y-%m-%d %H:%M:%S') +" Begin -------->"  
    #pool = Pool(processes = 3)  
    
    #toDay="20170926"
    Path = 'd:\\python\\ConceptWIND\\'+toDay    

    if os.path.exists(Path)  and os.access(Path, os.R_OK):
        print Path , ' is exist!' 
    else:
        os.makedirs(Path) 
        
    DownStocks = list() 
    UpStocks = list() 
    ErrorStocks = list() 
    QianZaiStocks = list() 
    noDireStocks = list()
    FinalResults= pd.DataFrame() 
    stockLastPrice = pd.DataFrame() 

    
    for cloumn in closeData.columns.values : 
        isFindZC = 0 
        isFindZL = 0
        
        tmpDataFrame = pd.DataFrame()
        tmpDataFrame['low'] = lowData[cloumn] 
        tmpDataFrame['close'] = closeData[cloumn] 
        tmpDataFrame['high'] = highData[cloumn] 
        tmpDataFrame['open'] = openData[cloumn] 
        tmpDataFrame['date'] = closeData.index 

        tmpDataFrame['close']=tmpDataFrame['close'].apply(float) 
        tmpDataFrame['low']=tmpDataFrame['low'].apply(float) 
        tmpDataFrame['high']=tmpDataFrame['high'].apply(float)
        tmpDataFrame['open']=tmpDataFrame['open'].apply(float)
        tmpDataFrame['close'] = np.round(tmpDataFrame['close'],2)   
        tmpDataFrame['low'] = np.round(tmpDataFrame['low'],2) 
        tmpDataFrame['high'] = np.round(tmpDataFrame['high'],2) 
        tmpDataFrame['open'] = np.round(tmpDataFrame['open'],2) 
        
        tmpDataFrame.replace(0,np.nan,inplace=True)
        tmpDataFrame.fillna(method='pad',inplace=True)
        
        cloumns= cloumn.split('/')
        
        graduation1 =closeData[cloumn][0]/150    
        
        try :        
            data1 = DealDataHL(cloumn,tmpDataFrame,graduation1) 
            
            lineDatas = []
            for N in Nlist:    
                data1Xmax = data1[data1['Label']==1].groupby('X').max()
                startXList = list(data1Xmax[data1Xmax['Y']>data1Xmax.shift(1)['Y']].index)
                for startX in startXList[-2:]:
                    #寻找支撑线
                    startXtoEnd = data1['X'].max() - startX
                    ZCline =findZCZLLine(data1,N,isFindMax=1,isFindMin=0,startXtoEnd=startXtoEnd)
                    if len(ZCline)>0 :
                        isFindZC += 1
                        lineDatas+=ZCline
                
                data1Omin = data1[data1['Label']==-1].groupby('X').min()
                startXList = list(data1Omin[data1Omin['Y']<data1Omin.shift(1)['Y']].index)
                for startX in startXList[-2:]:
                    #寻找阻力线
                    startXtoEnd = data1['X'].max() - startX
                    ZLline = findZCZLLine(data1,N,isFindMax=0,isFindMin=1,startXtoEnd=startXtoEnd) 
                    if len(ZLline)>0 :
                        isFindZL += 1
                        lineDatas+=ZLline
            
            if isFindZC >= 1 and isFindZL==0 :
                UpStocks.append(cloumn)
                tmpPath = u'\\支撑线'
            elif isFindZC == 0 and isFindZL>=1:
                DownStocks.append(cloumn)
                tmpPath = u'\\阻力线'
            elif isFindZC >= 1 and isFindZL>=1:
                noDireStocks.append(cloumn)
                tmpPath = u'\\均有'
            else :
                QianZaiStocks.append(cloumn)
                tmpPath = u'\\均无'
                
            if os.path.exists(Path+tmpPath)  and os.access(Path+tmpPath, os.R_OK):
                print Path , ' is exist!' 
            else:
                os.makedirs(Path+tmpPath)                 
                
            #如果有趋势线，则画图程序调用趋势线函数
            if len(lineDatas)>0:
                PointX.plotPointX3(data1,lineDatas,Path+tmpPath,cloumns[0]) 
            else :
                PointX.plotPointX2(data1,Path+tmpPath,cloumns[0]) 
                
# =============================================================================
#             if len(data1.index):
#                 data1[u"日期"] = toDay
#                 data1[u"股票代码"] = cloumn
#                 data1.to_sql('OXdataDetails',engine,if_exists='append') 
#             if len(lineDatas)>0:
#                 lines = []
#                 for idx, lineData in enumerate(lineDatas) :
#                     line = pd.DataFrame(lineData,index=['X','Y']).T
#                     line['ID'] = idx
#                     lines.append(line)
#                 lineData = pd.concat(lines)    
#                 lineData[u"日期"] = toDay
#                 lineData[u"股票代码"] = cloumn
#                 lineData.to_sql('OXLineDatas',engine,if_exists='append') 
# =============================================================================
                
        except Exception ,e:
            print e.args
            ErrorStocks.append(cloumn) 
    results = pd.DataFrame([UpStocks,DownStocks,noDireStocks,QianZaiStocks],\
                           index=[u'上涨',u'下跌','支撑阻力均有','无支撑和阻力']).T
    results[u"日期"] = toDay
    results.to_excel(Path+'\\results.xlsx') 
    if len(results.index) :
        results.to_sql('OXResults',engine,if_exists='append') #存入数据库，这句有时候运行一次报错，运行第二次就不报错了，不知道为什么  

    #stockLastPrice.to_excel(Path+'\\PointX_Simple_StockLastPrice.xlsx') 
    now = datetime.datetime.now() 
    print now.strftime('%Y-%m-%d %H:%M:%S') +" End-------->"
