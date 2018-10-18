# -*- coding: utf-8 -*-
"""
Created on Mon Oct 08 10:46:20 2018

@author: yangchg
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

def sigmoid(x):
    return 1.0/(1.0 + np.math.pow(np.e,-x))

x = pd.Series(np.arange(-10,10,0.1))
y = x.apply(sigmoid)

plt.plot(x,y)