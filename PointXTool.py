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
    for value in datas.columns.values : 
        for value2 in datas.columns.values:
            DataResults[value+'/'+value2] = ((datas[value]/datas[value][0])/(datas[value2]/datas[value2][0])-1)*100
            
    return  DataResults        
        

if __name__ == "__main__":
    
    print "Begining ------>"
    Path = u"E:\\系统文档\\天软\\wind概念指数日收盘数据.xlsx"
    datas = pd.read_excel(Path)        
    
    sourceData = DataTORS(datas)
    
    graduation1 = 0.1  
    #graduation2 = 0.05
   
    now = datetime.datetime.now()     
    print now.strftime('%Y-%m-%d %H:%M:%S') +" Begin -------->"  
    #pool = Pool(processes = 3)  
    toDay = now.strftime('%Y%m%d')  
    Path = 'd:\\python\\'+toDay    
    
    sourceData.to_csv(Path+'\\soureData.csv',encoding='utf-8') 
 
    if os.path.exists(Path)  and os.access(Path, os.R_OK):
        print Path , ' is exist!'
    else:
        os.makedirs(Path)

    DownStocks = list()
    UpStocks = list()
    ErrorStocks = list()
    QianZaiStocks = list()
    FinalResults= pd.DataFrame()
    
    for cloumn in sourceData.columns.values : 
        tmpDataFrame = pd.DataFrame()
        tmpDataFrame['open'] = sourceData[cloumn] 
        tmpDataFrame['close'] = sourceData[cloumn] 
        tmpDataFrame['date'] = sourceData.index 

        tmpDataFrame['close']=tmpDataFrame['close'].apply(float) 
        tmpDataFrame['open']=tmpDataFrame['open'].apply(float) 
        tmpDataFrame['close'] = np.round(tmpDataFrame['close'],2)   
        tmpDataFrame['open'] = np.round(tmpDataFrame['open'],2)
        
#==============================================================================
#         tmpDataFrame2 = pd.DataFrame()
#         tmpDataFrame2['open'] = sourceData_closePrice[cloumn] 
#         tmpDataFrame2['close'] = sourceData_closePrice[cloumn] 
#         tmpDataFrame2['date'] = sourceData_closePrice.index 
#         
#         tmpDataFrame2['close']=tmpDataFrame2['close'].apply(float) 
#         tmpDataFrame2['open']=tmpDataFrame2['open'].apply(float)
#         tmpDataFrame2['close'] = np.round(tmpDataFrame2['close'],2)   
#         tmpDataFrame2['open'] = np.round(tmpDataFrame2['open'],2)        
#==============================================================================
        cloumns= cloumn.split('/')
        
        try :        
            #graduation2 = sourceData_atr['ATR_a'][cloumn] / 3 
            #print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') +" Begin -------->"  
            data1 = DealData(cloumn,tmpDataFrame,graduation1) 
            #print datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') +" End -------->"  
            #data2 = DealData(cloumn,tmpDataFrame2,graduation2)        
            
            #plotPointX(data1,data2,cloumn) 
            
#==============================================================================
#             maxLabel2 = data2[data2['X']==data2['X'].max()]['Label'].max()         
#             secondMaxLabel2 = data2[data2['X']==data2['X'].max()-2]['Label'].max()
#             minY2 = data2[data2['X']==data2['X'].max()]['Y'].min()
#             secondMinY2 = data2[data2['X']==data2['X'].max()-2]['Y'].min()
#             
#             maxY2 = data2[data2['X']==data2['X'].max()]['Y'].max()
#             secondMaxY2 = data2[data2['X']==data2['X'].max()-2]['Y'].max()
#             
#==============================================================================
            maxLabel1 = data1[data1['X']==data1['X'].max()]['Label'].max()         
            secondMaxLabel1 = data1[data1['X']==(data1['X'].max()-2)]['Label'].max()
                
            minY1 = data1[data1['X']==data1['X'].max()]['Y'].min()
            secondMinY1 = data1[data1['X']==data1['X'].max()-2]['Y'].min()
                
            maxY1 = data1[data1['X']==data1['X'].max()]['Y'].max()
            secondMaxY1 = data1[data1['X']==(data1['X'].max()-2)]['Y'].max()
                
                 
            if maxLabel1 == 1  and maxY1 >= secondMaxY1:
                tmpMap = pd.DataFrame({'SWHY':cloumn,'hangye':cloumns[0],'ck':cloumns[1],'Status':'XB'},index=['0']) 
                FinalResults = FinalResults.append(tmpMap) 
            elif maxLabel1 == 1  and maxY1 < secondMaxY1 :
                tmpMap = pd.DataFrame({'SWHY':cloumn,'hangye':cloumns[0],'ck':cloumns[1],'Status':'XW'},index=['0']) 
                FinalResults = FinalResults.append(tmpMap) 
            elif maxLabel1 == -1  and minY1 <= secondMinY1 :    
                tmpMap = pd.DataFrame({'SWHY':cloumn,'hangye':cloumns[0],'ck':cloumns[1],'Status':'OS'},index=['0']) 
                FinalResults = FinalResults.append(tmpMap) 
            elif maxLabel1 == -1  and minY1 > secondMinY1 :    
                tmpMap = pd.DataFrame({'SWHY':cloumn,'hangye':cloumns[0],'ck':cloumns[1],'Status':'OW'},index=['0']) 
                FinalResults = FinalResults.append(tmpMap) 
            
            
#==============================================================================
#             if secondMaxLabel2 == -1 and secondMaxLabel1==-1 and minY2 <= secondMinY2:
#                 DownStocks.append(cloumn) 
#             
#             if secondMaxLabel1 == 1 and  secondMaxLabel2== 1 and maxY2 >= secondMaxY2:
#                 UpStocks.append(cloumn)       
#                 
#             if secondMaxLabel1 == -1 and  secondMaxLabel2== 1 and maxY2 >= secondMaxY2:
#                 QianZaiStocks.append(cloumn)                   
#==============================================================================
                
        except Exception ,e:
            print e.message
            ErrorStocks.append(cloumn)
            
        #pool.apply_async(DealData,(cloumn,tmpDataFrame,graduation,))
        
        #DealData(cloumn,tmpDataFrame,graduation)
    
#==============================================================================
#     with open(Path+"\\result.txt",'w') as f: 
#         f.write(u'下跌股票 ： \n ')
#         for downstock in DownStocks :            
#             f.write(downstock+' ')
#         f.write(u'\n 上涨股票：\n')    
#         for upstock in UpStocks :            
#             
#             f.write(upstock+' ')
#         f.write(u'\n 异常股票：\n')    
#         for errorStock in ErrorStocks :            
#             f.write(errorStock+' ')   
#         f.write(u'\n 潜在股票：\n')    
#         for qianZaiStock in QianZaiStocks :            
#             f.write(qianZaiStock+' ')      
#=============================i
    results = pd.DataFrame()
    results2 = pd.DataFrame()
    for i in FinalResults['ck'].drop_duplicates():
        tmp = FinalResults[FinalResults['ck']==i].set_index('hangye')
        tmp = tmp.rename(columns={'Status':i})[i]
        
        tmpDF = pd.DataFrame(tmp)
        groupedTmp = tmpDF[i].dropna().groupby(tmpDF[i]).count()        
        groupedTmp.name =  groupedTmp.index.name        
        
        results=results.append(tmp)
        results2=results2.append(groupedTmp)

       
    results.to_excel(Path+"\\result.xlsx")        
    results2.to_excel(Path+"\\result2.xlsx")     

    #pool.close()    
       
    #pool.join()
    
    now = datetime.datetime.now() 
    print now.strftime('%Y-%m-%d %H:%M:%S') +" End-------->"
   # DealData('SH601318',sourceData,graduation) 
   