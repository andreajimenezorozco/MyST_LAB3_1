
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

#Getting a dict with stadistics and ranking
data4 = f_estadisticas_ba(data3)
df1_est_ba = data4.get('df_1_tabla')
df2_ranking = data4.get('df_2_ranking')

#%% Full Aanalysis Part1
data, data2, data3, data4, df1_est_ba, df2_ranking = Full_Part1()

#%% Part2

#Capital evolucion
df_capital = f_evolucion_capital(data3)

#%% Full Aanalysis Part2
mad = f_estadisticas_mad(0.001, df_capital)

#%% Part3

#df needed for diccionary
ocurrencias, df_anclas = f_be_de_parte1(data3)
diccionario = f_be_de_parte2(ocurrencias,df_anclas)
df_resultados = diccionario['resultados']['dataframe']

















