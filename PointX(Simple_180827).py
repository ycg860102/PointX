# -*- coding: utf-8 -*-
"""
Created on Fri Sep 15 13:03:07 2017

@author: yangchg

说明：选择出申万一级子行业的相对强弱，并分为XB：买入，XW买等待，OS卖出，OW卖等待四种状态。
    简洁版本

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

import sys
sys.path.append("D:\Program Files\Tinysoft\Analyse.NET") 
reload(sys)    
sys.setdefaultencoding('utf8')
import TSLPy2

def getGraduation(price):
    if price <=20 :
        return 0.25
    elif price <=50:
        return 0.5
    elif price <=100:
        return 1.0
    else:
        return 2.5

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


def DealDataHL2( titleName, sourceDatas,MinSize = 0.05 ):
    pass


     
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
   
def findZCZLLine(data1,N):
    #增加趋势线，1、找到4阶枢纽拐点，2，枢纽拐点往右新增一格，增加或减少一个graduation，直到最早一天数据
        groupedData1 = data1.groupby(by='X') 
        lenGroupedData1 = len(groupedData1) 
        lineDatas =[] 
        zhichengline = []  #支撑线--上涨趋势线 
        zuliline = []    #阻力线--下降趋势线 
        isFindMax=0
        isFindMin=0
        if lenGroupedData1>=2*N+1 :
            for i in range(lenGroupedData1-(2*N+1) ):
                
                #当没有找到拐点时，从分组的最新端往前移动，如果分组的最大值等于
                if isFindMax==0 and max(groupedData1.max()[lenGroupedData1-i-(2*N+1) :lenGroupedData1-i]['Y'] ) \
                ==groupedData1.max()['Y'][lenGroupedData1-i-(N+1):lenGroupedData1-i-N].values[0]:
                    #将graduation 设置为各组序列最大值的均值代入寻找graduation函数。
                    graduation1 = getGraduation(np.mean(groupedData1.max()[lenGroupedData1-i-(2*N+1) :lenGroupedData1-i]['Y'] ))
                
                    maxPointY = groupedData1.max()['Y'][lenGroupedData1-i-(N+1):lenGroupedData1-i-N].values[0]+graduation1
                    maxPointX = groupedData1.max()['Y'][lenGroupedData1-i-(N+1):lenGroupedData1-i-N].index.values[0]
                    #lineDataX = [maxPointX+j for j in range(lenGroupedData1-maxPointX+1)] 
                    lineDataX = [maxPointX, lenGroupedData1] 
                    #lineDataY = [maxPointY-j*graduation1 for j in range(lenGroupedData1-maxPointX+1)] 
                    lineDataY = [maxPointY ,maxPointY - (lenGroupedData1-maxPointX )*graduation1] 
                    zuliline=[lineDataX,lineDataY] 
                    isFindMax=1 
                
                if isFindMin==0 and min(groupedData1.min()[lenGroupedData1-i-(2*N+1):lenGroupedData1-i]['Y'] ) \
                ==groupedData1.min()['Y'][lenGroupedData1-i-(N+1):lenGroupedData1-i-N].values[0] :
                    #将graduation 设置为各组序列最小值的均值代入寻找graduation函数。
                    graduation1 = getGraduation(np.mean(groupedData1.min()[lenGroupedData1-i-(2*N+1) :lenGroupedData1-i]['Y'] ))
                
                    minPointY = groupedData1.min()['Y'][lenGroupedData1-i-(N+1):lenGroupedData1-i-N].values[0]-graduation1
                    minPointX = groupedData1.min()['Y'][lenGroupedData1-i-(N+1):lenGroupedData1-i-N].index.values[0]    
                    #lineDataX = [minPointX+j for j in range(lenGroupedData1-minPointX+1)]
                    lineDataX = [minPointX,lenGroupedData1]
                    #lineDataY = [minPointY+j*graduation1 for j in range(lenGroupedData1-minPointX+1)]
                    lineDataY = [minPointY,minPointY + (lenGroupedData1-minPointX)*graduation1]
                    zhichengline= [lineDataX,lineDataY]                        
                    isFindMin=1 
                if isFindMin ==1 and isFindMax==1 : 
                    break
        if len(zuliline):                    
            lineDatas.append(zuliline) 
            tmpStockLastPrice['zuliPrice']=[zuliline[-1][-1]] 
        if len(zhichengline): 
            lineDatas.append(zhichengline)
            tmpStockLastPrice['zhichengPrice']=[zhichengline[-1][-1]] 
        
        return lineDatas
   
   
if __name__ == "__main__":
    
    print "Begining ------>" 
    now = datetime.datetime.now()  

    toDay = now.strftime('%Y-%m-%d')
    #toDay = "2017-12-12"
    
    #下面的90，代表九十天前 365天为过去一年暑假
    begDay = now + datetime.timedelta(days=-365)
    #begDay='2017-05-10'
    #closeData = getCloseData("close",toDay)
    #填写需要计算的股票代码    
    
    #stockList =  ['600132.SH','000848.SZ'] 
    bk = u'上证50'
    stockList = TSLPy2.RemoteCallFunc('getbk',[bk],{})   
    stockList =  stockList[1]
    stockList = [ stock[2:8]+'.'+stock[0:2] for stock in stockList ] 
    #,'601318.SH','002883.SZ','600066.SH','603578.SH']     
    stockList =  ['600578.SH','600172.SH','000848.SZ','600993.SH','600446.SH'] 
    #stockList =  ['601328.SH','000001.SZ','600015.SH','000932.SZ','600782.SH','600282.SH','600022.SH','000959.SZ','600569.SH','600507.SH','000778.SZ','600126.SH','300003.SZ','002223.SZ','603658.SH','300463.SZ','300529.SZ','600529.SH','002022.SZ','601233.SH','603225.SH','600810.SH','002064.SZ','002206.SZ','300122.SZ','000661.SZ','002252.SZ','600161.SH','300294.SZ','300485.SZ','300009.SZ','600118.SH','300456.SZ','600138.SH','603869.SH','300178.SZ','000547.SZ','002482.SZ','300506.SZ','002713.SZ','600511.SH','000028.SZ','002589.SZ','603368.SH','002092.SZ','600409.SH','000683.SZ','603077.SH','000822.SZ','002648.SZ','600618.SH','600277.SH','600328.SH','601158.SH','000544.SZ','600820.SH','600326.SH','600512.SH','600502.SH','002460.SZ','000960.SZ','600392.SH','002716.SZ','600459.SH','600585.SH','600801.SH','000401.SZ','002233.SZ','600720.SH','000672.SZ','603986.SH','600667.SH','603501.SH','300373.SZ','002371.SZ','002049.SZ','600460.SH','601766.SH','000008.SZ','600970.SH','002051.SZ','000065.SZ','600496.SH','000636.SZ','603328.SH','002815.SZ','300476.SZ','600563.SH','002138.SZ','002463.SZ','600580.SH','000922.SZ','603988.SH','601966.SH','601058.SH','002068.SZ','300144.SZ','002310.SZ','300197.SZ','002717.SZ','300237.SZ','300349.SZ','300410.SZ','300114.SZ','002658.SZ','300572.SZ','300066.SZ'] 
    #N=2
    Nlist = [2,3,4,5]
    closeData = getStockListClosePrice(stockList,begDay,toDay,'close') 
    highData = getStockListClosePrice(stockList,begDay,toDay,'high') 
    lowData = getStockListClosePrice(stockList,begDay,toDay,'low') 
    openData = getStockListClosePrice(stockList,begDay,toDay,'open') 
    
   
    now = datetime.datetime.now()     
    print now.strftime('%Y-%m-%d %H:%M:%S') +" Begin -------->"  
    #pool = Pool(processes = 3)  
    toDay = now.strftime('%Y%m%d') 
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
    FinalResults= pd.DataFrame() 
    stockLastPrice = pd.DataFrame() 
    
    for cloumn in closeData.columns.values : 
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
        tmpDataFrame.fillna(method='pad')
        
        cloumns= cloumn.split('/')
        
        graduation1 =closeData[cloumn][0]/150    
        
        #最新价
        tmpStockLastPrice =pd.DataFrame() 
        tmpStockLastPrice['stockID']=cloumns
        tmpStockLastPrice['close']=[tmpDataFrame['close'][-1]]
        print tmpStockLastPrice
        
        try :        
            data1 = DealDataHL(cloumn,tmpDataFrame,graduation1) 
            
            lineDatas = []
            
            for N in Nlist:    
                lineDatas+=findZCZLLine(data1,N) 
                
            #lineDatas=findZCZLLine(data1,N) 
           
            #lineData = [[maxPointX,maxPointX+1],[maxPointY,maxPointY-graduation1]]
            #如果有趋势线，则画图程序调用趋势线函数
            if len(lineDatas)>0:
                PointX.plotPointX3(data1,lineDatas,Path,cloumns[0]) 
            else :
                PointX.plotPointX2(data1,Path,cloumns[0])  
            
            maxLabel1 = data1[data1['X']==data1['X'].max()]['Label'].max()         
            secondMaxLabel1 = data1[data1['X']==(data1['X'].max()-2)]['Label'].max()
                
            minY1 = data1[data1['X']==data1['X'].max()]['Y'].min()
            secondMinY1 = data1[data1['X']==data1['X'].max()-2]['Y'].min()
                
            maxY1 = data1[data1['X']==data1['X'].max()]['Y'].max()
            secondMaxY1 = data1[data1['X']==(data1['X'].max()-2)]['Y'].max()
            
            if maxLabel1 == 1 and maxY1 >secondMaxY1 :
                UpStocks.append(cloumn)
            elif  maxLabel1 == -1 and minY1 <secondMinY1:
                DownStocks.append(cloumn)
            else :
                QianZaiStocks.append(cloumn)
        except Exception ,e:
            print e
            print e.args
            ErrorStocks.append(cloumn)
    
    #stockLastPrice.to_excel(Path+'\\PointX_Simple_StockLastPrice.xlsx') 
    now = datetime.datetime.now() 
    print now.strftime('%Y-%m-%d %H:%M:%S') +" End-------->"
