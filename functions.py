
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: Develop tools for analyzing the performance of trading activity                            -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: andreajimenezorozco, jofefloga                                                              -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/andreajimenezorozco/MyST_LAB3_1                                      -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
#%% Libraries

#Time and changes in time
from datetime import datetime, timedelta

#For input and passwords
from getpass import getpass

#MetaTrader5
import MetaTrader5 as mt5

#Math, Numbers, DataFrames, and Statistics
import pandas as pd
import numpy as np
import statistics


#%% Functions Part1
def f_leer_archivo():
    Accounts = pd.read_excel('files/Accounts.xlsx')
    Names = list(Accounts['Name'])
    print('Los nombres son:',Names)
    Name = input('Ingrese nombre del integrante a analizar: ')
    
    if Name in Names:
        user = Accounts[Accounts['Name']==Name]
        try:
            userid = int(user['Account_ID'].values[0])
            userpass = str(user['Password'].values[0])
            a = mt5.initialize(login=userid, server='MetaQuotes-Demo',password=userpass)
        except:
            try:
                userid = int(input('Ingrese su usuario en mt5: '))
                userpass = str(getpass('Ingrese su contraseña: '))
                a = mt5.initialize(login=userid, server='MetaQuotes-Demo',password=userpass)
            except:
                return print('La acción no fue válida, verifique sus datos')
        #Initialize MT5
        
        if a:
            print('Se inició con éxito la cuenta')
            pos = mt5.history_deals_get(datetime(2020,1,1),datetime.now())
            key = pos[0]._asdict().keys()
            orders = pd.DataFrame(list(pos),columns=key)
            
            Dates = pd.DataFrame({'Position':orders['position_id'].unique()})
            opentime = []
            closetime = []
            price_o = []
            price_c = []
            for i in orders['position_id'].unique():
                dates = np.array(orders['time'][orders['position_id']==i])
                prices = np.array(orders['price'][orders['position_id']==i])
                if len(dates)==2:
                    opentime.append(dates[0])
                    closetime.append(dates[1])
                    price_o.append(prices[0])
                    price_c.append(prices[1])
                else:
                    opentime.append(dates[0])
                    closetime.append(0)
                    price_o.append(prices[0])
                    price_c.append(prices[-1])

            Dates['Time'] = opentime
            Dates['Symbol'] = [np.array(orders['symbol'][orders['position_id']==i])[0] for i in orders['position_id'].unique()]
            type_op = [np.array(orders['type'][orders['position_id']==i])[0] for i in orders['position_id'].unique()]
            Dates['Type'] = ['buy' if i == 0 else 'sell' for i in type_op]
            Dates['Volume'] = [np.array(orders['volume'][orders['position_id']==i])[0] for i in orders['position_id'].unique()]
            Dates['Price'] = price_o
            Dates['Time.1'] = closetime
            Dates['Price.1'] = price_c
            Dates['Commission'] = [np.array(orders['commission'][orders['position_id']==i])[-1] for i in orders['position_id'].unique()]
            Dates['Swap'] = [np.array(orders['swap'][orders['position_id']==i])[-1] for i in orders['position_id'].unique()]
            Dates['Profit'] = [np.array(orders['profit'][orders['position_id']==i])[-1] for i in orders['position_id'].unique()]
            Dates = Dates[Dates['Time.1']!=0]
            return Dates.sort_values(by='Time.1',ascending=True).reset_index(drop=True)
            
        else:
            print('No se pudo acceder a la cuenta')
    else:
        print('El nombre no fue válido, intente de nuevo')
        
        
def f_pip_size(param_ins):
    try:
        mt5.initialize(login=41671538, server='MetaQuotes-Demo',password='pcdt7hng')
        pip_size = int(0.1/mt5.symbol_info(param_ins)._asdict().get('trade_tick_size'))
        return pip_size
    except:
        return print('Ticker no válido')
    
    
def f_columnas_tiempos(param_data):
    param_data['open_time'] = [datetime.fromtimestamp(i) for i in param_data['Time']]
    param_data['close_time'] = [datetime.fromtimestamp(i) for i in param_data['Time.1']]
    param_data['time'] = (param_data['close_time']-param_data['open_time']).apply(timedelta.total_seconds,1)
    return param_data


def f_columnas_pips(param_data):
    
    param_data['pips'] = [(param_data['Price.1'].iloc[i]-param_data['Price'].iloc[i])*f_pip_size(param_data['Symbol'].iloc[i]) 
                          if param_data['Type'].iloc[i]=='buy' 
                          else (param_data['Price'].iloc[i]-param_data['Price.1'].iloc[i])*f_pip_size(param_data['Symbol'].iloc[i]) 
                          for i in range(len(param_data))]
    param_data['pips_acm'] = param_data['pips'].cumsum()
    param_data['profit_acm'] = param_data['Profit'].cumsum()
    return param_data


def f_estadisticas_ba(param_data):
    Ops_totales = len(param_data)
    Ganadoras = len(param_data[param_data['Profit']>=0])
    Ganadoras_c = len(param_data[(param_data['Profit']>=0) & (param_data['Type']=='buy')])
    Ganadoras_v = len(param_data[(param_data['Profit']>=0) & (param_data['Type']!='buy')])
    Perdedoras = len(param_data[param_data['Profit']<0])
    Perdedoras_c = len(param_data[(param_data['Profit']<0) & (param_data['Type']=='buy')])
    Perdedoras_v = len(param_data[(param_data['Profit']<0) & (param_data['Type']!='buy')])
    Mediana_profit = statistics.median(param_data.sort_values(by='Profit')['Profit'])
    Mediana_pips = statistics.median(param_data.sort_values(by='pips')['pips'])
    r_efectividad = Ganadoras/Ops_totales
    r_proporcion = Ganadoras/Perdedoras
    r_efectividad_c = Ganadoras_c/Ops_totales
    r_efectividad_v = Ganadoras_v/Ops_totales
    
    valor = [Ops_totales,Ganadoras,Ganadoras_c,Ganadoras_v,Perdedoras,Perdedoras_c,Perdedoras_v,Mediana_profit,
             Mediana_pips,r_efectividad,r_proporcion,r_efectividad_c,r_efectividad_v]
    df_1_tabla = pd.DataFrame({'medida':['Ops totales','Ganadoras','Ganadoras_c','Ganadoras_v','Perdedoras',
                                         'Perdedoras_c','Perdedoras_v','Mediana(Profit)','Mediana(Pips)',
                                         'r_efectividad','r_proporcion','r_efectividad_c','r_efectividad_v'],
                               'valor':np.round(valor,2),
                               'descripcion':['Operaciones totales','Operaciones ganadoras',
                                              'Operaciones ganadoras de compra','Operaciones ganadoras de venta',
                                              'Operaciones perdedoras','Operaciones perdedoras de compra',
                                              'Operaciones perdedoras de venta','Mediana de profit de operaciones',
                                              'Mediana de pips de operaciones','Ganadoras Totales/Operaciones Totales',
                                              'Ganadoras Totales/Perdedoras Totales',
                                              'Ganadoras Compras/Operaciones Totales',
                                              'Ganadoras Ventas/Operaciones Totales']})
    symbols = param_data['Symbol'].unique()
    df_2_ranking = pd.DataFrame({'symbol':param_data['Symbol'].unique(),
                                 'rank (%)':100*np.round([len(param_data[(param_data['Profit']>0) & 
                                                        (param_data['Symbol']==symbols[i])])/
                                         len(param_data[param_data['Symbol']==symbols[i]]) 
                                         for i in range(len(symbols))],2)
                                })
   
    df_2_ranking = df_2_ranking.sort_values(by='rank (%)',ascending=False).reset_index(drop=True)
    
    return {'df_1_tabla':df_1_tabla,'df_2_ranking':df_2_ranking}


def Full_Part1():
    #Read historic
    data = f_leer_archivo()
    if str(type(data)) == "<class 'pandas.core.frame.DataFrame'>":
        #Adding time columns
        data2 = f_columnas_tiempos(data)
        
        #Adding pips columns 
        data3 = f_columnas_pips(data2)
        
        #Getting a dict with 
        data4 = f_estadisticas_ba(data3)
        df1 = data4.get('df_1_tabla')
        df2 = data4.get('df_2_ranking')
        print('Primer análisis realizado con éxito')
        return data, data2, data3, data4, df1, df2
    else:
        return 0,0,0,0,0,0
#%% Functions Part2



#%% Functions Part3


    
#%% Functions Part4











