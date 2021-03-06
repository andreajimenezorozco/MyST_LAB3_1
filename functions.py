
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

import os
import glob
import datetime
from datetime import timedelta
from datetime import datetime


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

def f_evolucion_capital(param_data):
    param_data['close_time'] = [i.strftime('%Y-%m-%d') for i in param_data['close_time']]
    param_data['close_time_'] = pd.to_datetime(param_data['close_time'])
    df = pd.DataFrame({'close_time_': pd.date_range(start='2/19/2021', end='3/5/2021')})
    df = pd.merge(df, param_data.loc[:, ('close_time_', 'Profit')], how='left', on='close_time_')
    df = df.fillna(0)
    df = df.set_index('close_time_')
    df = df.resample('D').sum()
    df["profit_acm_d"] = df["Profit"].cumsum()
    df["cap_acum"] = df["profit_acm_d"] + 1000000

    return df


def f_estadisticas_mad(rf, df):
    # Sharpe Original
    rp = np.log(df.cap_acum) - np.log(df.cap_acum.shift(1))
    rp = rp.fillna(0)
    sdp = rp.std()
    rp_mean = rp.mean()
    rf = (rf / 252)
    sharpe_original = (rp_mean - rf) / sdp

    # Sharpe Ratio Actualizado
    #path = 'files'
    #file = glob.glob(os.path.join(path, "*.csv"))
    benchmark = pd.read_csv('files/SP500.csv')['Close']
    #benchmark = benchmark['Close']
    rp_benchmark = np.log(benchmark) - np.log(benchmark.shift(1))
    rp_benchmark = rp_benchmark.fillna(0)
    rp = rp.reset_index()
    rp_rb = rp.join(rp_benchmark)
    rp_rb['Rp-Rb'] = rp_rb['cap_acum'] - rp_rb['Close']
    std_sra = rp_rb['Rp-Rb'].std()
    r_trader = rp_rb['cap_acum'].mean()
    r_benchmark = rp_rb['Close'].mean()
    sharpe_actualizado = (r_trader - r_benchmark) / std_sra

    min_ = df.cap_acum.min()
    max_ = df.cap_acum.max()

    # Drawdown
    drawdown_cap = df.profit_acm_d.min()
    date_drawdown = (df.loc[df.profit_acm_d == drawdown_cap].index.values[0])
    date_drawdown = np.datetime_as_string(date_drawdown, unit='D')
    temp = 0
    peak = 0
    du = 0
    b = df.profit_acm_d
    for i in range(len(b)):
        if b[i] < b[i - 1] and b[i] < peak:
            peak = b[i]
            temp = 0

        elif b[i] > b[i - 1]:
            temp = b[i]

        if temp - peak > du:
            du = temp - peak
    # DrawUp
    temp = 0
    peak = 0
    dd = 0
    for i in range(len(b)):
        if b[i] > b[i - 1] and b[i] > peak:
            peak = b[i]
            temp = 0

        elif b[i] < b[i - 1]:
            temp = b[i]

        if temp - peak < dd:
            dd = temp - peak
    
    
    
    drawup_cap = du
    date_drawup = np.datetime_as_string(df.loc[df.cap_acum == min_].index.values[0], unit='D')

    data = [
        ['sharpe_original', 'Cantidad', sharpe_original, "Sharpe Ratio Fórmula Original"],
        ['sharpe_actualizado', 'Cantidad', sharpe_actualizado, "Sharpe Ratio Fórmula Actualizado"],
        ['drawdown_capi', 'Fecha Final', dd, "Máxima pérdida flotante registrada"],
        ['drawup_capi', 'Fecha Final', drawup_cap, "Máxima ganancia flotante registrada"],
        ['drawdown_capi', 'Fecha Inicial', date_drawdown, "Fecha inicial del DrawDown de Capital"],
        ['drawdown_capi', 'Fecha Final', date_drawdown, "Fecha final del DrawDown de Capital"],
        ['drawup_capi', 'Fecha Inicial', date_drawup, "Fecha inicial del DrawUp de Capital"],
        ['drawup_capi', 'Fecha Final', date_drawup, "Fecha final del DrawUp de Capital"]]

    df = pd.DataFrame(data, columns=['metrica', ' ', 'Valor', 'Descripción'])

    return df

def draw(values, method):
    nuevo, init, fin = [], [], []
    value_list = values["profit_acm_d"].tolist()
    for cont in range(0, len(value_list)):
        param = value_list[cont]
        rest_list = value_list[cont + 1:]
        for elemento in rest_list:
            if method == "down":
                nuevo.append(param - elemento)
                init.append(param)
                fin.append(elemento)
            if method == "up":
                nuevo.append(elemento - param)
                init.append(param)
                fin.append(elemento)
    x1 = max(nuevo)
    ind = nuevo.index(x1)
    x2 = values.index[values['profit_acm_d'] == init[ind]].tolist()[0]
    x3 = values.index[values['profit_acm_d'] == fin[ind]].tolist()[0]
    return x1, x2, x3


#%% Functions Part3

def f_columnas_pips_v2(param_data):
    param_data['float_pips'] = [(param_data['float_price'].iloc[i]-param_data['Price'].iloc[i])*f_pip_size(param_data['Symbol'].iloc[i])
                              if param_data['Type'].iloc[i]=='buy'
                              else (param_data['Price'].iloc[i]-param_data['float_price'].iloc[i])*f_pip_size(param_data['Symbol'].iloc[i])
                              for i in range(len(param_data))]
    return param_data


def f_be_de_parte1(param_data):
    # Filtrado de operaciones ganadoras (operaciones ancla)
    param_data['capital_acm'] = param_data['profit_acm'] + 100000
    ganadoras = param_data[param_data.Profit > 0]
    ganadoras = ganadoras.reset_index(drop=True)
    ganadoras["Ratio"] = (ganadoras["Profit"] / abs(ganadoras["profit_acm"]))
    df_anclas = ganadoras.loc[:, ['close_time', "open_time", 'Type', "Symbol",
                                  'Profit', "profit_acm", "capital_acm", "Ratio", "Time", "Time.1", "Price", "Volume"]]
    df_anclas = df_anclas.reset_index(drop=True)

    # Criterio de selección de operaciones abiertas por cada ancla
    ocurrencias = []
    file_list = []
    for x in df_anclas.index:
        df = param_data[(param_data.open_time <= df_anclas["close_time"][x]) &
                        (param_data.close_time > df_anclas["close_time"][x])].loc[:,
             ['Type', 'Symbol', 'Volume', 'Profit', "Price", "pips"]]
        df['close_time_ancla'] = pd.Timestamp(df_anclas['close_time'][x])
        file_list.append(df)
        ocurrencias.append(len(df))
    all_df = pd.concat(file_list, ignore_index=True)

    # Descarga de precios para cada operación abierta
    float_price = []
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        quit()
    for i in range(len(all_df)):
        utc_from = datetime(all_df['close_time_ancla'][i].year,
                            all_df['close_time_ancla'][i].month,
                            all_df['close_time_ancla'][i].day)
        utc_to = utc_from + timedelta(1)
        symbol = all_df['Symbol'][i]
        ticks = mt5.copy_ticks_range(symbol, utc_from, utc_to, mt5.COPY_TICKS_ALL)
        ticks_frame = pd.DataFrame(ticks)
        ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')
        tick_time = next(x for x in ticks_frame['time'] if x >= all_df['close_time_ancla'][i])
        price = ticks_frame.loc[ticks_frame['time'] == tick_time]
        if all_df["Type"][i] == "buy":
            price = price["bid"].mean()
        else:
            price = price["ask"].mean()
        float_price.append(price)
        float_prices = pd.DataFrame(columns=['float_price'], data=float_price)

    all_df = all_df.join(float_prices)

    all_df = f_columnas_pips_v2(all_df)
    all_df["float_P&L"] = (all_df["Profit"] / all_df["pips"]) * all_df["float_pips"]
    all_df = all_df[all_df['float_P&L'] < 0].reset_index(drop=True)

    return all_df, df_anclas

def f_be_de_parte2(ocurrencias,df_anclas):

    dict_ = {'ocurrencias':{'Cantidad':len(ocurrencias)}}
    status_quo = []
    aversion_perdida = []
    for i in ocurrencias.index:
        inst = df_anclas[df_anclas['close_time']==ocurrencias['close_time_ancla'][i]]
        dict_['ocurrencias'][f'ocurrencia_{i+1}'] = {'timestamp':ocurrencias['close_time_ancla'][i],
                                                   'operaciones':{
                                                       'ganadoras':{'instrumento':inst['Symbol'].iloc[0],
                                                                    'volumen':inst['Volume'].iloc[0],
                                                                    'sentido':inst['Type'].iloc[0],
                                                                    'profit_ganadora':round(inst['Profit'].iloc[0],2)},
                                                       'perdedoras':{'instrumento':ocurrencias['Symbol'][i],
                                                                    'volumen':ocurrencias['Volume'][i],
                                                                    'sentido':ocurrencias['Type'][i],
                                                                    'profit_perdedora':round(ocurrencias['float_P&L'][i],2)}
                                                   },
                                                   'ratio_cp_profit_acm':round(abs(ocurrencias['float_P&L'][i]/inst['profit_acm'].iloc[0]),2),
                                                   'ratio_cg_profit_acm':round(abs(inst['Profit'].iloc[0]/inst['profit_acm'].iloc[0]),2),
                                                   'ratio_cp_cg':round(abs(ocurrencias['float_P&L'][i]/inst['Profit'].iloc[0]),2)
                                                  }
        if abs(ocurrencias['float_P&L'][i]/inst['profit_acm'].iloc[0])<abs(inst['Profit'].iloc[0]/inst['profit_acm'].iloc[0]):
            status_quo.append(1)
        else:
            status_quo.append(0)

        if abs(ocurrencias['float_P&L'][i]/inst['Profit'].iloc[0])>2:
            aversion_perdida.append(1)
        else:
            aversion_perdida.append(0)

    sensibilidad_decreciente = 0
    if df_anclas['profit_acm'].iloc[0]<df_anclas['profit_acm'].iloc[-1]:
        sensibilidad_decreciente += 1

    if df_anclas['Profit'].iloc[-1] > df_anclas['Profit'].iloc[0] and ocurrencias['float_P&L'].iloc[-1] > ocurrencias['float_P&L'].iloc[0]:
        sensibilidad_decreciente += 1

    ult_ocurrencia = len(ocurrencias)-1
    if dict_['ocurrencias'][f'ocurrencia_{ult_ocurrencia}']['ratio_cp_cg'] > 2:
        sensibilidad_decreciente += 1

    if sensibilidad_decreciente >= 2:
        sens_ans = 'Si'
    else:
        sens_ans = 'No'



    dict_['resultados'] = {
        'dataframe': pd.DataFrame({'ocurrencias':len(ocurrencias),
                                   'status_quo':str(round(100*np.array(status_quo).mean(),2))+'%',
                                   'aversion_perdida':str(round(100*np.array(aversion_perdida).mean(),2))+'%',
                                   'sensibilidad_decreciente':[sens_ans]})
    }
    return dict_









