# -*- coding: utf-8 -*-
"""
Created on Wed May 10 11:23:16 2017

@author: yangchg
说明：选择出申万一级子行业的相对强弱，
并分为XB：买入，XW买等待，OS卖出，OW卖等待四种状态。

"""


import pandas as pd
import numpy as np 
#import tushare as ts 
#import seaborn as sns
import matplotlib.pyplot as plt
import datetime

import os
from multiprocessing import Pool

import sys
sys.path.append("D:\Program Files\Tinysoft\Analyse.NET") 
reload(sys)    
sys.setdefaultencoding('utf8')
import TSLPy2

def getGraduation(price):
    price = abs(price)
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


def DealData( titleName, sourceDatas,MinSize = 0.05 ):
    
    #FinalData = list()     
    tmpDF = pd.DataFrame()    
    YouBiao = 1
    
    Flag = 0 #上涨表示1，下跌表示-1  
    tmpLen = 0
    
    #初始化第一天数据 
    if sourceDatas['close'][0] >= sourceDatas['open'][0] :
        Flag = 1 
        tmpLen = int( (sourceDatas['close'][0] - sourceDatas['open'][0]) / MinSize)
        
#        dataFrameList =  [ pd.DataFrame({'X':YouBiao,
#                                'Y':j*MinSize + sourceDatas['open'][0],
#                                'Label' : Flag,
#                                'date':sourceDatas['date'][0]},index=['0']) for j in xrange(tmpLen+1) ]        
#        tmp = pd.concat(dataFrameList) 
#        
#        tmpDF = tmpDF.append(tmp,ignore_index=True)
        
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
                                'Y':sourceDatas['open'][0] - j*MinSize,
                                'Label':Flag,
                                'date':sourceDatas['date'][0]},index=['0']) for j in xrange(tmpLen+1) ]        
        tmp = pd.concat(dataFrameList) 
        tmpDF = tmpDF.append(tmp,ignore_index=True)        
        
#        for j in xrange(tmpLen+1):
#            tmp = pd.DataFrame({'X':YouBiao,
#                                'Y':sourceDatas['open'][0] - j*MinSize,
#                                'Label':Flag,
#                                'date':sourceDatas['date'][0]},index=['0'])
#            tmpDF = tmpDF.append(tmp,ignore_index=True)       
    
    #从第二天开始循环处理
    for i,item in sourceDatas[1:].iterrows() : 
        
        tmpMax = tmpDF[tmpDF['X']==YouBiao]['Y'].max() 
        tmpMin = tmpDF[tmpDF['X']==YouBiao]['Y'].min()
        
        if Flag == 1 and item['close'] >= tmpMax:
            tmpLen = int( (item['close'] - tmpMax) / MinSize)
            
            dataFrameList =  [ pd.DataFrame({'X':YouBiao,
                                'Y':(1+j)*MinSize + tmpMax,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0']) for j in xrange(tmpLen) ]
                
            if len(dataFrameList)>0:            
                tmp = pd.concat(dataFrameList) 
                tmpDF = tmpDF.append(tmp,ignore_index=True)    

#            for j in xrange(tmpLen):
#                tmp = pd.DataFrame({'X':YouBiao,
#                                'Y':(1+j)*MinSize + tmpMax,
#                                'Label':Flag,
#                                'date':item['date']
#                                },index=['0'])
#                tmpDF = tmpDF.append(tmp,ignore_index=True)
#                
#                 
#            print i, 'dataFrameList',tmpDF    
            
        elif Flag == 1 and item['close'] < tmpMax:
             tmpLen = int((tmpMax - item['close']) / MinSize)

             if tmpLen >= 3 :
                 YouBiao+=1 #新开一列 
                 Flag=-1
                 
                 dataFrameList =  [ pd.DataFrame({'X':YouBiao,
                                'Y': tmpDF[tmpDF['X'] == YouBiao-1]['Y'].max() - (1+j)*MinSize,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0'])  for j in xrange(tmpLen) ]             
                 if len(dataFrameList)>0:            
                     tmp = pd.concat(dataFrameList) 
                     tmpDF = tmpDF.append(tmp,ignore_index=True) 
                 
#                 for j in xrange(tmpLen):
#                     tmp = pd.DataFrame({'X':YouBiao,
#                                'Y': tmpDF[tmpDF['X'] == YouBiao-1]['Y'].max() - (1+j)*MinSize,
#                                'Label':Flag,
#                                'date':item['date']
#                                },index=['0'])
#                     tmpDF= tmpDF.append(tmp,ignore_index=True) 
              
        elif Flag == -1 and item['close'] <= tmpMin:
             tmpLen = int(( tmpMin -item['close']) / MinSize)
             
             dataFrameList =  [  pd.DataFrame({'X':YouBiao,
                                'Y':tmpMin - (1+j)*MinSize ,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0'])  for j in xrange(tmpLen) ]             
             if len(dataFrameList)>0:            
                 tmp = pd.concat(dataFrameList) 
                 tmpDF = tmpDF.append(tmp,ignore_index=True)              
             
             
#             for j in xrange(tmpLen):
#                tmp = pd.DataFrame({'X':YouBiao,
#                                'Y':tmpMin - (1+j)*MinSize ,
#                                'Label':Flag,
#                                'date':item['date']
#                                },index=['0'])
#                tmpDF = tmpDF.append(tmp,ignore_index=True)
        elif Flag == -1 and item['close'] > tmpMin:  
              tmpLen = int((item['close'] - tmpMin) / MinSize)

              if tmpLen >= 3 :
                 YouBiao+=1  #新开一列 
                 Flag=1
                 
                 dataFrameList =  [ pd.DataFrame({'X':YouBiao,
                                'Y': tmpDF[tmpDF['X'] == YouBiao-1]['Y'].min() + (1+j)*MinSize,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0'])  for j in xrange(tmpLen) ]             
                 if len(dataFrameList)>0:            
                     tmp = pd.concat(dataFrameList) 
                     tmpDF = tmpDF.append(tmp,ignore_index=True)                    
                 
#                 for j in xrange(tmpLen):
#                     tmp = pd.DataFrame({'X':YouBiao,
#                                'Y': tmpDF[tmpDF['X'] == YouBiao-1]['Y'].min() + (1+j)*MinSize,
#                                'Label':Flag,
#                                'date':item['date']
#                                },index=['0'])
#                     tmpDF = tmpDF.append(tmp,ignore_index=True)   
                     
    return tmpDF 

def plotPointX3(data1,lineDatas,Path,titleName):
    print "begin plotPointX2!"
    #画散点图     
    plt.figure(figsize=(8,6))
    #下标
    #markers = ['o','p','D','s','h','*','v','<'] 
    #标记颜色    
    #colors =  ['b','g','r','y','c','k','m','b'] 
    #图标标题    
    plt.title(titleName)
    #开启网格
    plt.grid(True, linestyle = "--", color = "c", linewidth = "1" ,alpha=.3)
    
    x = data1[data1['Label']==1]['X'].values
    y = data1[data1['Label']==1]['Y'].values
    plt.scatter(x,y,s=60,marker='x',c='r',label='Up',alpha=.5)
    plt.legend(loc = 'upper left')
    
    x = data1[data1['Label']==-1]['X'].values
    y = data1[data1['Label']==-1]['Y'].values
    plt.scatter(x,y,s=60,marker='o',c='g',label='Down',alpha=.5)
    plt.legend(loc = 'upper left')    
    
    #画直线图
    for lineData in lineDatas:    
        
        plt.plot(lineData[0],lineData[1])

#==============================================================================
#         plt.annotate(r'$%.2f$' %y, xy=(float(lineData[0][0]), float(lineData[1][0])), xycoords='data', xytext=(+30, +30),
#             textcoords='offset points', fontsize=16,
#             arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
# 
#         plt.annotate(r'$%.2f$' %y, xy=(lineData[0][-1], lineData[1][-1]), xycoords='data', xytext=(+30, +30),
#             textcoords='offset points', fontsize=16,
#             arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))
#==============================================================================
        #print lineData[1][0] ,"type(lineData[1][0]): ",type(lineData[1][0])
        #所有点增加Y坐标标注
        for x,y in zip(lineData[0],lineData[1]):
             #print x ," Y :",y ," type(y): ",type(y)
             plt.annotate(r'$%.2f$' %y, xy=(x, y), xycoords='data', xytext=(+30, +30),
              textcoords='offset points', fontsize=16,
              arrowprops=dict(arrowstyle='->', connectionstyle="arc3,rad=.2"))

    
    #now = datetime.datetime.now()
    #toDay = now.strftime('%Y%m%d')  
    
    if os.path.exists(Path)  and os.access(Path, os.R_OK):
        print Path , ' is exist!'
    else:
        os.makedirs(Path)
    plt.savefig(Path + '\\'+titleName+'.PNG')
    plt.close()



def plotPointX2(data1,Path,titleName):
    print "begin plotPointX2!"
    #画散点图     
    plt.figure(figsize=(8,6))
    #下标
    #markers = ['o','p','D','s','h','*','v','<'] 
    #标记颜色    
    #colors =  ['b','g','r','y','c','k','m','b'] 
    #图标标题    
    plt.title(titleName)
    #开启网格
    plt.grid(True, linestyle = "--", color = "c", linewidth = "1" ,alpha=.3)
    
    
    x = data1[data1['Label']==1]['X'].values
    y = data1[data1['Label']==1]['Y'].values
    plt.scatter(x,y,s=60,marker='x',c='r',label='Up',alpha=.5)
    plt.legend(loc = 'upper left')
    
    x = data1[data1['Label']==-1]['X'].values
    y = data1[data1['Label']==-1]['Y'].values
    plt.scatter(x,y,s=60,marker='o',c='g',label='Down',alpha=.5)
    plt.legend(loc = 'upper left')    
    
    
    now = datetime.datetime.now()
    toDay = now.strftime('%Y%m%d')  
    
    if os.path.exists(Path)  and os.access(Path, os.R_OK):
        print Path , ' is exist!'
    else:
        os.makedirs(Path)
    plt.savefig(Path + '\\'+titleName+'.PNG')
    plt.close()

    #画散点图 
def plotPointX(data1,data2,Path,titleName):
    
    fig , (ax0,ax1 ) = plt.subplots(1,2, figsize=(16,12))
    
    #下标
    #markers = ['o','p','D','s','h','*','v','<'] 
    #标记颜色    
    #colors =  ['b','g','r','y','c','k','m','b'] 
    #图标标题    
    ax0.set_title(titleName+' hangye_roll')
    ax1.set_title(titleName+' gegu') 
    #开启网格
    ax0.grid(True, linestyle = "--", color = "c", linewidth = "1" ,alpha=.3)
    ax1.grid(True, linestyle = "--", color = "c", linewidth = "1" ,alpha=.3)
    
    x = data1[data1['Label']==1]['X'].values
    y = data1[data1['Label']==1]['Y'].values
    ax0.scatter(x,y,s=60,marker='x',c='r',label='Up',alpha=.5)
    ax0.legend(loc = 'upper left')
    
    x = data1[data1['Label']==-1]['X'].values
    y = data1[data1['Label']==-1]['Y'].values
    ax0.scatter(x,y,s=60,marker='o',c='g',label='Down',alpha=.5)
    ax0.legend(loc = 'upper left')    
    
    x2 = data2[data2['Label']==1]['X'].values
    y2 = data2[data2['Label']==1]['Y'].values
    ax1.scatter(x2,y2,s=60,marker='x',c='r',label='Up',alpha=.5)
    ax1.legend(loc = 'upper left')
    
    x2 = data2[data2['Label']==-1]['X'].values
    y2 = data2[data2['Label']==-1]['Y'].values
    ax1.scatter(x2,y2,s=60,marker='o',c='g',label='Down',alpha=.5)
    ax1.legend(loc = 'upper left') 
    
    if os.path.exists(Path)  and os.access(Path, os.R_OK):
        print Path , ' is exist!'
    else:
        os.makedirs(Path)
    plt.savefig(Path + '\\'+titleName+'.PNG')
    plt.close()
    #plt.show()
    #return data1   
    
def DataTORS(datas):

    #print datas.index 
    DataResults = pd.DataFrame()
    col = list(datas.columns.values)
    for value in datas.columns.values : 
        col.remove(value) 
        for value2 in col: 
            DataResults[value+'_'+value2] = ((datas[value]/datas[value][0])/(datas[value2]/datas[value2][0])-1)*100
            
    return DataResults        
        

def dealAndPlot(closeData,Path,Nlist = [1,]):
    """
        接收参数，股票收盘价序列和选择几节枢纽拐点
    """
    DownStocks = list() 
    UpStocks = list() 
    ErrorStocks = list() 
    QianZaiStocks = list() 
    noDireStocks = list()
    #FinalResults= pd.DataFrame() 
    #stockLastPrice = pd.DataFrame() 
    
    for cloumn in closeData.columns.values : 
        isFindZC = 0 
        isFindZL = 0
        
        tmpDataFrame = pd.DataFrame() 
        tmpDataFrame['low'] = closeData[cloumn] 
        tmpDataFrame['close'] = closeData[cloumn] 
        tmpDataFrame['high'] = closeData[cloumn] 
        tmpDataFrame['open'] = closeData[cloumn] 
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
        tmpDataFrame.dropna(inplace=True)
        
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
                    ZCline = findZCZLLine(data1,N,isFindMax=1,isFindMin=0,startXtoEnd=startXtoEnd)
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
                plotPointX3(data1,lineDatas,Path+tmpPath,cloumn) 
            else :
                plotPointX2(data1,Path+tmpPath,cloumn) 
                
        except Exception ,e:
            print e.args
            ErrorStocks.append(cloumn) 
    results = pd.DataFrame([UpStocks,DownStocks,noDireStocks,QianZaiStocks],\
                           index=[u'上涨',u'下跌','支撑阻力均有','无支撑和阻力']).T
    
    results.to_excel(Path+'\\results.xlsx')  
    return results

