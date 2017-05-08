# -*- coding: utf-8 -*-
"""
Created on 5 7 11:23:16 2017
describe 
@author: yangchg
"""

#%pylab inline
import pandas as pd
import numpy as np 
import tushare as ts 
#import seaborn as sns
import matplotlib.pyplot as plt

#from math import isnan

def DealData(titleName, sourceDatas,MinSize = 0.05 ):
    
    #results = list();
    #filelen = len(filenames)
    
    #下标
    #markers = ['o','p','D','s','h','*','v','<']  
    #标记颜色    
    #colors =  ['b','g','r','y','c','k','m','b']       
    
    sourceDatas['close']=sourceDatas['close'].apply(float) 
    sourceDatas['open']=sourceDatas['open'].apply(float)
    sourceDatas['high']=sourceDatas['high'].apply(float)
    sourceDatas['low']=sourceDatas['low'].apply(float)   
    sourceDatas['volume']=sourceDatas['volume'].apply(float)
    
    sourceDatas['close'] = np.round(sourceDatas['close'],1)   
    sourceDatas['open'] = np.round(sourceDatas['open'],1)
    
    #FinalData = list()     
    tmpDF = pd.DataFrame()    
    YouBiao = 1
    
    Flag = 0 #上涨表示1，下跌表示-1  
    tmpLen = 0
    
    
    #print len(sourceDatas)
    #print sourceDatas['close'][0] ,'  ', sourceDatas['open'][0] 
    #print (sourceDatas['open'][0] - sourceDatas['close'][0])
    #print int((sourceDatas['open'][0] - sourceDatas['close'][0])/MinSize)
    #初始化第一天数据 
    if sourceDatas['close'][0] >= sourceDatas['open'][0] :
        Flag = 1 
        
        tmpLen = int( (sourceDatas['close'][0] - sourceDatas['open'][0]) / MinSize)
        
        for j in range(tmpLen+1):
            tmp = pd.DataFrame({'X':YouBiao,
                                'Y':j*MinSize + sourceDatas['open'][0],
                                'Label' : Flag,
                                'date':sourceDatas['date'][0]},index=['0'])
            tmpDF = tmpDF.append(tmp,ignore_index=True)
    else:
        Flag = -1  
        tmpLen = int( (sourceDatas['open'][0] - sourceDatas['close'][0]) / MinSize )
        
        for j in range(tmpLen+1):
            tmp = pd.DataFrame({'X':YouBiao,
                                'Y':sourceDatas['open'][0] - j*MinSize,
                                'Label':Flag,
                                'date':sourceDatas['date'][0]},index=['0'])
            tmpDF = tmpDF.append(tmp,ignore_index=True)       
    
    #从第二天开始循环处理
    for i,item in sourceDatas[1:].iterrows() : 
        
        tmpMax = tmpDF[tmpDF['X']==YouBiao]['Y'].max() 
        tmpMin = tmpDF[tmpDF['X']==YouBiao]['Y'].min()
        
        if Flag == 1 and item['close'] >= tmpMax:
            tmpLen = int( (item['close'] - tmpMax) / MinSize)

            for j in range(tmpLen):
                tmp = pd.DataFrame({'X':YouBiao,
                                'Y':(1+j)*MinSize + tmpMax,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0'])
                tmpDF = tmpDF.append(tmp,ignore_index=True)
        elif Flag == 1 and item['close'] < tmpMax:
             tmpLen = int((tmpMax - item['close']) / MinSize)

             if tmpLen > 3 :
                 YouBiao+=1 #新开一列 
                 Flag=-1
                 for j in range(tmpLen):
                     tmp = pd.DataFrame({'X':YouBiao,
                                'Y': tmpDF[tmpDF['X'] == YouBiao-1]['Y'].max() - (1+j)*MinSize,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0'])
                     tmpDF= tmpDF.append(tmp,ignore_index=True) 
              
                     
        elif Flag == -1 and item['close'] <= tmpMin:
             tmpLen = int(( tmpMin -item['close']) / MinSize)

             for j in range(tmpLen):
                tmp = pd.DataFrame({'X':YouBiao,
                                'Y':tmpMin - (1+j)*MinSize ,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0'])
                tmpDF = tmpDF.append(tmp,ignore_index=True)
        elif Flag == -1 and item['close'] > tmpMin:  
              tmpLen = int((item['close'] - tmpMin) / MinSize)

              if tmpLen > 3 :
                 YouBiao+=1  #新开一列 
                 Flag=1
                 for j in range(tmpLen):
                     tmp = pd.DataFrame({'X':YouBiao,
                                'Y': tmpDF[tmpDF['X'] == YouBiao-1]['Y'].min() + (1+j)*MinSize,
                                'Label':Flag,
                                'date':item['date']
                                },index=['0'])
                     tmpDF = tmpDF.append(tmp,ignore_index=True)
    
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
    
    
    
    x = tmpDF[tmpDF['Label']==1]['X'].values
    y = tmpDF[tmpDF['Label']==1]['Y'].values
    plt.scatter(x,y,s=60,marker='x',c='r',label='Up',alpha=.5)
    plt.legend(loc = 'upper right')
    
    x = tmpDF[tmpDF['Label']==-1]['X'].values
    y = tmpDF[tmpDF['Label']==-1]['Y'].values
    plt.scatter(x,y,s=60,marker='o',c='g',label='Down',alpha=.5)
    plt.legend(loc = 'upper right')    
    
    return tmpDF
    #plt.savefig(titleName)
        
    
if __name__ == "__main__":
    N=8
    #循环处理path目录下所有文件
    path = u'E:\系统文档\天软\MinusClose' 
    #filenames = os.listdir(path)     
    #fileLens = len(filenames) 
    
    StockID = '000300'
    graduation = 0.1
    
    #sourceData = ts.get_k_data(StockID,start='2017-02-01',end='2017-05-03')
    sourceData = ts.get_k_data(StockID,start='2017-01-01',end='2017-05-03',index=True)
    
    sourceData['date2']=sourceData['date']
    sourceData=sourceData.set_index('date2')
    
    tmp = DealData(StockID,sourceData,graduation)  
         
    plt.show()
