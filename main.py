
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Develop tools for analyzing the performance of trading activity                            -- #
# -- script: main.py : python script with the main functionality                                         -- #
# -- author: andreajimenezorozco, jofefloga                                                              -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/andreajimenezorozco/MyST_LAB3_1                                      -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

#%% Libraries
from functions import *

#%% Part1

#Read historic
data = f_leer_archivo()

#Pip size example
USDJPY_pipsize = f_pip_size('USDJPY')

#Adding time columns
data2 = f_columnas_tiempos(data)

#Adding pips columns
data3 = f_columnas_pips(data2)

#Getting a dict with 
data4 = f_estadisticas_ba(data3)
df1 = data4.get('df_1_tabla')
df2 = data4.get('df_2_ranking')

#%% Full Aanalysis Part1
data, data2, data3, data4, df1, df2 = Full_Part1()

#%% Part2

#%% Part3

#%%Part4


















