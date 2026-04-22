#####  CANALCLIMA ENEL PROJECT DATABASES

#### Import libraries
import pyodbc
import time
import pandas as pd
import mysql.connector
from datetime import datetime
from datetime import timedelta
import calendar
import scipy.stats
from dateutil.relativedelta import relativedelta
import numpy as np
from statistics import mode
import statistics as st
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import scipy as sp
import math
import os
import locale

#### Fechas de evaluación para extremo graficas
TLimite = 3
mesEvaluado = 3
añoEvaluado = 2026
MesEvaluacion = 'MaxAnual' #poner numero de mes evaluado o 'MaxAnual'
locale.setlocale(locale.LC_ALL, 'es_ES')
nombreMes = calendar.month_name[mesEvaluado]
inicioMes=datetime(añoEvaluado, mesEvaluado, 1, 0, 0)
finMes=inicioMes + relativedelta(months=+1) + relativedelta(days=+1) - timedelta(minutes=1)
#fechas para extraer datos
inicio2024 = datetime(2024, 1, 1, 0, 0)
fechaSinMantenimiento2024 = datetime(2024, 2, 1, 0, 0)
fechaFin = inicioMes - timedelta(minutes=1)
datosEsperadosQ = (finMes-inicioMes).days * 96

######################## CREAR RUTAS PARA EXPORTAR ARCHIVOS
path_current = os.getcwd()
rutaSalida = path_current

#Crear carpeta del año para guardar los meses que van a tener tablas y graficos
if not os.path.exists(rutaSalida + "/" + str(añoEvaluado)):
    os.mkdir(rutaSalida + "/" + str(añoEvaluado))
else:
    pass
rutaSalida = rutaSalida + "/" + str(añoEvaluado)

#Crear carpeta del mes para guardar tablas y graficos
if not os.path.exists(rutaSalida + "/" + str(mesEvaluado) + ' ' + calendar.month_name[mesEvaluado]):
    os.mkdir(rutaSalida + "/" + str(mesEvaluado) + ' ' + calendar.month_name[mesEvaluado])
    os.mkdir(rutaSalida + "/" + str(mesEvaluado) + ' ' + calendar.month_name[mesEvaluado] + "/Tablas")
    os.mkdir(rutaSalida + "/" + str(mesEvaluado) + ' ' + calendar.month_name[mesEvaluado] + "/Graficas")
    # os.mkdir(rutaSalida + "/" + str(mesEvaluado) + ' ' + calendar.month_name[mesEvaluado] + "/GraficasDesde2024")
else:
    pass

# establecer la ruta de salida de los archivos dentro de la carpeta del mes evaluado
rutaSalida = rutaSalida + '/' + str(mesEvaluado) + " " + calendar.month_name[mesEvaluado]

# funcion para generar la consulta en texto
def textoSQL(idSensor, fechaIni, fechaFin):
    textoFecha = "(FechaHora>='" + fechaIni.strftime('%Y-%m-%d') + "' and FechaHora<'" + fechaFin.strftime('%Y-%m-%d') + "')"
    for i in idSensor:
        if idSensor.index(i) == 0:
            textoTemp = "(IdSensor="+i
            textoIdSensor = textoTemp
        else:
            textoTemp = " or IdSensor=" + i
            textoIdSensor = textoIdSensor + textoTemp
    textoIdSensor = textoIdSensor + ")"
    textoFuente = "SELECT * FROM [dbo].[Datosenrevision] where " # puede que se cambie de tabla. Si eso pasa toca cambiar esto. Antes se uso [Datosenrevision_Provisional]
    texto = textoFuente+textoIdSensor+" and "+ textoFecha
    return texto

# funcion para conectarse con servidor y sacar datos con la consulta de la funcion "textoSQL"
def sacarDatos(idSensor, fechaIni, fechaFin):
    # Carga de bases de datos desde SQL - Version actualizada (usuario y contraseña bien)
    conexion = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server}; SERVER=aplicaciones.canalclima.com,1845; DATABASE=ENEL; UID=santiago.quijano; PWD=contra2026*2; TrustServerCertificate=yes;')
     # conexion = pyodbc.connect('DRIVER={SQL Server}; SERVER=dbservcclima.cloudapp.net,1845; DATABASE=CCLIMATE; UID=santiago.quijano; PWD=contra2025*')
    # Creacion de cursor
    cursor = conexion.cursor()
    # Ejecuta sentencias SQL en el cursor y guardo consulta de Base de datos enel
    cursor.execute('use ENEL')
    # Imprime tablas en sql
    # cursor.tables(tableType='TABLE').fetchall()
    consulta = textoSQL(idSensor, fechaIni, fechaFin)
    cursor.execute(consulta)
    rows = cursor.fetchall()
    # Convertir los datos en una lista de diccionarios
    dict_list = []
    for row in rows:
        dict_list.append(dict(zip([column[0] for column in cursor.description], row)))
    # Convertir la lista de diccionarios en un DataFrame
    data = pd.DataFrame(dict_list)
    conexion.close()
    return data


# Extraer DataFrames desde sql
dataMes_PNyQ = sacarDatos(["0230", "0601", "0240", "0241"], inicioMes, finMes)
print("Se descargan datos del mes")
start = time.time()
dataDesde2024 = sacarDatos(["0230", "0601"], fechaSinMantenimiento2024, finMes)
end = time.time()
print("Se descargan datos desde 2024")
# Se crea csv con la informacion de precipitación, nivel y cuadal del mes evaluado
dataMes_PNyQ.to_csv(rutaSalida + '/Tablas/datosPQNMes.csv')

# Sacar datos historico de los csvs de mi compu (cuando los carguen todos ya no se va a usar esto
#dataDesdeSinMantenimiento.to_csv("""Historicos/nivel y caudal 2023-03 a 2024-02.csv""",sep=";",date_format='%d/%m/%Y %H:%M', decimal=',',index=False)
data2023_2024ConMantenimiento = pd.read_csv("""Historicos/nivel y caudal 2023-03 a 2024-02.csv""",sep=";",dtype={'IdSensor':str},parse_dates=["FechaHora"],date_format='%d/%m/%Y %H:%M', decimal=',')
bogotacsv = pd.read_csv("""Historicos/Bogota nivel y caudal.csv""",sep=";",dtype={'IdSensor':str},parse_dates=["FechaHora"],date_format='%d/%m/%Y %H:%M', decimal=',')
guaviocsv = pd.read_csv("""Historicos/Guavio nivel y caudal.csv""",sep=";",dtype={'IdSensor':str},parse_dates=["FechaHora"],date_format='%d/%m/%Y %H:%M', decimal=',')
quimbocsv = pd.read_csv("""Historicos/Quimbo-Betania nivel y caudal.csv""",sep=";",dtype={'IdSensor':str},parse_dates=["FechaHora"],date_format='%d/%m/%Y %H:%M', decimal=',') #, na_values='#N/D' opcion
print("Se leen archivos historicos")
# Cargar tablas para relacionar las tablas (codigos de sensores y de estaciones con los nombres largos y cuales años de algunas estaciones no se van a tener en cuenta)
codigosSensores = pd.read_csv("""TablasOrigenInfo/CodigoSensores.csv""",sep=";",dtype={'IdSensor':str})
codigosEstaciones = pd.read_csv("""TablasOrigenInfo/CodigoEstaciones.csv""",sep=";")
# en este archivo se indican cuales años de cuales estaciones no se van a tener en cuenta para realizar el proceso.
# Es muy importante ajsutarlo cada mes porque puede cambiar para el ultimo año. Principalmente importante en
cualesAnosQuitar = pd.read_csv("""TablasOrigenInfo/paraQuitarAños.csv""",sep=";")

""" Para sacar datos de guavio.
# sacar datos guavio
estacionesGuavio = [26005, 26001, 26006, 26004, 27002, 27003]
datosGuavio2024 = dataDesde2024[dataDesde2024["IdEstacion"].isin(estacionesGuavio)]
datosGuavio2024["Fecha"] = datosGuavio2024["FechaHora"].dt.date
datosBuenos = datosGuavio2024[datosGuavio2024["ValidacionFinal"].isin(["V","S"])]
valoresDiarioGuavio = pd.pivot_table(datosBuenos, values='Valor', index=['IdEstacion', 'Fecha'],  columns=['IdSensor'], aggfunc="mean")
diariosGuavio = valoresDiarioGuavio.reset_index()


for i in datosBuenos["IdEstacion"].unique():
    datosEstacion = datosBuenos[datosBuenos["IdEstacion"]==i]
    nombre=(codigosEstaciones['NombreEstacion'][codigosEstaciones['IdEstacion']==i]).values.tolist()
    for j in datosEstacion['IdSensor'].unique():
        datosGraficar = datosEstacion[datosEstacion["IdSensor"]==j]
        plt.figure(figsize = [8,6])
        if j =="0601":
            variable = "Caudal"
            unidad = "$m^3/s$"
        else:
            variable = "Nivel"
            unidad = "m"
        ax = plt.axes()
        plt.title(f'{nombre[0]} - {variable}', fontweight="bold")
        ax.plot(datosGraficar["Fecha"],datosGraficar["Valor"], label=variable, color="b", linewidth=0.6)
        ax.set_xlabel("Fecha", fontsize = 11)
        ax.set_ylabel(f'{variable} ({unidad})', fontsize = 11)
        ax.legend()
        plt_var = ax.get_figure()
        rutaImagenes = rutaSalida + "/GraficasDesde2024/"
        plt_var.savefig(rutaImagenes+nombre[0] + " " + variable + ".png", dpi = 300)
        plt.close()



for i in diariosGuavio["IdEstacion"].unique():
    datosEstacion = diariosGuavio[diariosGuavio["IdEstacion"]==i]
    nombre=(codigosEstaciones['NombreEstacion'][codigosEstaciones['IdEstacion']==i]).values.tolist()
    for j in ["0601","0230"]:
        plt.figure(figsize = [8,6])
        if j =="0601":
            variable = "Caudal"
            unidad = "$m^3/s$"
        else:
            variable = "Nivel"
            unidad = "m"
        ax = plt.axes()
        plt.title(f'{nombre[0]} - {variable}  diario', fontweight="bold")
        ax.plot(datosEstacion["Fecha"],datosEstacion[j], label=variable, color="b", linewidth=0.6)
        ax.set_xlabel("Fecha", fontsize = 11)
        ax.set_ylabel(f'{variable} ({unidad})', fontsize = 11)
        ax.legend()
        plt_var = ax.get_figure()
        rutaImagenes = rutaSalida + "/GraficasDesde2024/"
        plt_var.savefig(rutaImagenes+nombre[0] + " " +  variable + " diario.png", dpi = 300)
        plt.close()

datosGuavio2024[['FechaHora', 'IdEstacion', 'IdSensor', 'Valor', 'ValidacionFinal']].to_excel(rutaImagenes +'/DatosGuavio.xlsx',index=False)
diariosGuavio.to_excel(rutaImagenes +'/DatosGuavioDiario.xlsx', index=False)
"""

# Unir datos
historicos = pd.concat([bogotacsv, guaviocsv, quimbocsv, data2023_2024ConMantenimiento])
historicosSinDuplicados = historicos.drop_duplicates(subset=["FechaHora","IdEstacion","IdSensor"])
# no incluyo datos historicos posteriores a 2023-03-01 porque los saque de base de datos
historicosSinDuplicados = historicosSinDuplicados[historicosSinDuplicados['FechaHora'] < fechaSinMantenimiento2024.strftime('%Y-%m-%d')]
historicosBuenos = historicosSinDuplicados[(historicosSinDuplicados['ValidacionFinal'] == "V")]

datoscompletos = pd.concat([historicosBuenos, dataDesde2024])
datoscompletos['Año'] = datoscompletos['FechaHora'].dt.year
datoscompletos['Mes'] = datoscompletos['FechaHora'].dt.month
datoscompletos = datoscompletos[['IdEstacion','IdSensor','FechaHora','Valor','IdMetodoAdquisicion','ValidacionFinal','Año','Mes']]
# filtro para que solo trabaje con datos de caudal
datosCaudal = datoscompletos[datoscompletos['IdSensor'] == '0601'].reset_index()
datosCaudal = datosCaudal.drop(['index'],axis=1)
# quito columnas que no necesito y agrego columnas de año y mes
completosBuenos = datosCaudal[(datosCaudal['ValidacionFinal'] == "V") | (datosCaudal['ValidacionFinal'] == "S")]
datosMesCaudal = completosBuenos[(completosBuenos['FechaHora']>= inicioMes.strftime('%Y-%m-%d')) & (completosBuenos['FechaHora']< finMes.strftime('%Y-%m-%d'))].reset_index()
datosMesCaudal = datosMesCaudal.drop(['index'],axis=1)
#sacar estaciones con datos de caudal
estacionQ_ID = completosBuenos['IdEstacion'].unique()

#Para buscar datos de un periodo especifico
#fechaEspecifica = datetime(2024, 5, 1, 0, 0)
#fechaEspecificaFin = datetime(2024, 6, 1, 0, 0)
#datosQEspecificos = datoscompletos[(datoscompletos['IdEstacion'] == 36007) & (datoscompletos['FechaHora']>= fechaEspecifica.strftime('%Y-%m-%d')) & (datoscompletos['FechaHora']< fechaEspecificaFin.strftime('%Y-%m-%d'))].reset_index()
#datosQEspecificos.to_excel(rutaSalida + '/consulta.xlsx')

### Tal vez no sea necesario agregar mes y año podria filtrar siempre con datosCaudal[datosCaudal['FechaHora'].dt.month==3] pero puede que sea mas dificil de leer
## agrupa y lo deja en formato maso similar maximos=completosBuenos.groupby(['IdEstacion','Año','Mes'])['Valor'].max()
#Se crea tabla de maximo y la exporto a un excel
tablapivoteMax = pd.pivot_table(completosBuenos, values='Valor', index=['IdEstacion', 'Año'],  columns=['Mes'], aggfunc="max")
tablapivoteMax['MaxAnual'] = tablapivoteMax.max(axis=1)

with pd.ExcelWriter(rutaSalida + '/Tablas/maximosMesSeparados.xlsx') as writer:
    for i in estacionQ_ID:
        tablapivoteMax.loc[i].to_excel(writer, index = True, sheet_name=str(i))

###### Gumbel / encontrar parametros #######
###### Mu es location #######
###### sigma es scale #######

def mievfit(datosEv,alpha):
    shape, mu, sigma = stats.genextreme.fit(datosEv,f0=0)  # se debe dejar el shape(f0) = 0 para que sea la GEV sea distribución gumbel
    # c, loc, sscale = stats.genextreme.fit(datosEv)
    xrange= max(datosEv)-min(datosEv)
    maxDatos=min(datosEv)
    x0=-(datosEv-maxDatos)/xrange # uso min porque en matlab esta en negativo

    sigmahat= (6**0.5*st.stdev(x0))/math.pi # valores iniciales de sigma y mean
    wgtmeanUnc = sum(x0)/ len(x0)
    if likelihoodEquation(sigmahat, x0, wgtmeanUnc) > 0:
        upper=sigmahat
        lower=upper/2
        while likelihoodEquation(lower, x0, wgtmeanUnc) > 0:
            upper = lower
            lower = upper/2
    else:
        lower = sigmahat
        upper = lower*2
        while likelihoodEquation(upper, x0, wgtmeanUnc) < 0:
            lower = upper
            upper = lower*2

    bnds=[lower, upper] # bnds da el rango para buscar las soluciones en root_scalar
    solucion=sp.optimize.root_scalar(likelihoodEquation,bracket=bnds,args=(x0,wgtmeanUnc))  # busco las raices que solucionan funcion dentro del rando de solucion (bnds)
    sigmahat=solucion.root
    muhat=sigmahat*np.log(sum(np.exp(x0/sigmahat))/len(x0))
    parmhat=[-(xrange*muhat)+maxDatos, xrange*sigmahat] # esto ya lo habia sacado con genextreme.fit pero por replicar evfit tambien salio (mu es sigmhat[0] y sigma parmhat[1]
    ### crear matriz fisher tomado de evlike en matlab
    z=-(datosEv-mu)/sigma
    expz=np.exp(z)
    unc=np.ones_like(datosEv)
    nH11 =sum(expz)
    nH12 =sum((z+1)*expz-unc)
    nH22 =sum(z*(z+2)*expz-((2*z)+1))
    avar=((sigma**2)/(nH11*nH22-nH12*nH12))*np.array([[nH22, -nH12],[-nH12,nH11]])
    transfhat= [parmhat[0], np.log(parmhat[1])]
    se = np.sqrt(np.diagonal(avar))
    se[1]=se[1]/parmhat[1]
    porcen=alpha/2
    upperLowerMu=sp.stats.norm.ppf([porcen,1-porcen],loc=mu,scale=se[0])
    upperLowerSigma = np.exp(sp.stats.norm.ppf([porcen,1-porcen], loc=transfhat[1], scale=se[1]))
    dicGumbel = {"muMaxVero":mu, "sigmaMaxvero": sigma, "lowerICMu": upperLowerMu[0], "upperICMu": upperLowerMu[1],
                 "lowerICSigma": upperLowerSigma[0], "upperICSigma": upperLowerSigma[1],}
    return dicGumbel

def likelihoodEquation(sigma,x,xbarWgtUnc):
    w = np.exp(x/sigma)
    v = sigma+xbarWgtUnc - sum(x*w)/sum(w)
    return v

####### Sacar Parametros de las estaciones (mu, sigma y sus IC) y tambien el umbral de la serie parcial (minimo de los años que me interesan)
QUmbralLim = pd.Series(index=estacionQ_ID, name='LimiteQUmbral')
for i in estacionQ_ID:
    maxgumbel = tablapivoteMax.loc[i][MesEvaluacion].sort_values(ascending=False)
    maxGumbelNoNaN = maxgumbel.dropna()
    quitarEstacion = cualesAnosQuitar[cualesAnosQuitar['IdEstacion'] == i] # extraigo los datos que quiero del archivo de csv
    soloQMaxUtiles = maxGumbelNoNaN[~maxGumbelNoNaN.index.isin(quitarEstacion['AñoEliminar'])] # para dejar solo los años que se quieren. El cosito "~" cambia lo valores de True a False y al reves
    soloQMaxNumpy = soloQMaxUtiles.to_numpy()
    # sacar limite de umbrales
    QUmbralLim.loc[i] = soloQMaxNumpy[-1]
    if np.where(estacionQ_ID == i)[0][0] == 0:
        parametrosEstaciones = pd.DataFrame(mievfit(soloQMaxNumpy, 0.05), index=[i])
    else:
        parametrosEstaciones.loc[i] = mievfit(soloQMaxNumpy, 0.05)

######### Encontrar la combinación con los minimos y maximos para cada valor en
tRetorno_generado=np.concatenate((1.0001, np.arange(1.001, 1.499, 0.005), np.arange(1.5, 7.0, 0.05), np.arange(7, 100, 0.5), np.arange(100, 501, 2)),axis=None)
tRetorno_generado=np.round(tRetorno_generado,5)
GumbelProbaAcumul=1-1/tRetorno_generado
ubiTLimite=np.abs(tRetorno_generado-TLimite).argmin()

# se crea dataframe vacio para incluir la combinacion de parametros 100 combinaciones (10 opxiones de Sigma y 10 de mu)
tamañoDataFrame = 10
dfMuCombinacion = pd.DataFrame(index=range(tamañoDataFrame**2),columns=estacionQ_ID)
dfSigmaCombinacion = pd.DataFrame(index=range(tamañoDataFrame**2),columns=estacionQ_ID)

# Se crea lista con los mu y sigma en todas las posibilidades combinadas
for i in estacionQ_ID:
    muArray = np.linspace(parametrosEstaciones.loc[i]['lowerICMu'], parametrosEstaciones.loc[i]['upperICMu'], tamañoDataFrame)
    sigmaArray = np.linspace(parametrosEstaciones.loc[i]['lowerICSigma'], parametrosEstaciones.loc[i]['upperICSigma'], tamañoDataFrame)
    for j in range(len(muArray)):
        for k in range(len(sigmaArray)):
            fila = (j*len(muArray))+k
            dfMuCombinacion.loc[fila,i] = muArray[j]
            dfSigmaCombinacion.loc[fila,i] = sigmaArray[k]

# Genero los 4 dataframe que voy a usar para llenar con los caudales calculados con los intervalos de confianza
dfQMaxICGumbel = pd.DataFrame(index=tRetorno_generado,columns=estacionQ_ID)
dfUbiMaxICGumbel = pd.DataFrame(index=tRetorno_generado,columns=estacionQ_ID)
dfQMinICGumbel = pd.DataFrame(index=tRetorno_generado,columns=estacionQ_ID)
dfUbiMinICGumbel = pd.DataFrame(index=tRetorno_generado,columns=estacionQ_ID)

# ingreso los caudales a los dataframes del caudal max y la ubicación en la que es max (combinacion que da los max)
for i in estacionQ_ID:
    for j in GumbelProbaAcumul:
        mu = dfMuCombinacion[i]
        sigma = dfSigmaCombinacion[i]
        posiJ = np.where(GumbelProbaAcumul == j)[0][0]
        Tr_evaluado = tRetorno_generado[posiJ]
        dfQMaxICGumbel.loc[Tr_evaluado,i] = max(mu+sigma*(-np.log(-np.log(j))))
        serie = (mu + sigma * (-np.log(-np.log(j))))
        if serie.notna().any():
            dfUbiMaxICGumbel.loc[Tr_evaluado, i] = serie.idxmax()
        else:
            dfUbiMaxICGumbel.loc[Tr_evaluado, i] = np.nan  # o None
        #dfUbiMaxICGumbel.loc[Tr_evaluado,i] = (mu + sigma * (-np.log(-np.log(j)))).idxmax()

# ingreso los caudales a los dataframes del caudal min y ubicación en max (combinacion que da los min)
for i in estacionQ_ID:
    for j in GumbelProbaAcumul:
        mu = dfMuCombinacion[i]
        sigma = dfSigmaCombinacion[i]
        posiJ = np.where(GumbelProbaAcumul == j)[0][0]
        Tr_evaluado = tRetorno_generado[posiJ]
        dfQMinICGumbel.loc[Tr_evaluado,i] = min(mu + sigma * (-np.log(-np.log(j))))
        serie = (mu + sigma * (-np.log(-np.log(j))))
        if serie.notna().any():
            dfUbiMinICGumbel.loc[Tr_evaluado, i] = serie.idxmin()
        else:
            dfUbiMinICGumbel.loc[Tr_evaluado, i] = np.nan  # o None
        #dfUbiMinICGumbel.loc[Tr_evaluado,i] = (mu + sigma * (-np.log(-np.log(j)))).idxmin()

###### valores de maxima verosimilitud y encontrar el periodo de retorno de los datos del mes
# Se crea dataframes para los caudales calculados con los parametros de maxima verosimilitud
dfQMaxVero=pd.DataFrame(index=tRetorno_generado,columns=estacionQ_ID)
#Creo dataframe vacios del periodo de retorno y caudal de los datos medidos en el mes.
TMedidoEstaciones=pd.DataFrame(index=np.arange(datosEsperadosQ),columns=estacionQ_ID)
QMedidoEstaciones=pd.DataFrame(index=np.arange(datosEsperadosQ),columns=estacionQ_ID)

for i in estacionQ_ID:
    mu = parametrosEstaciones['muMaxVero'].loc[i]
    sigma = parametrosEstaciones['sigmaMaxvero'].loc[i]
    QMedido = (datosMesCaudal['Valor'][datosMesCaudal['IdEstacion'] == i])
    dfQMaxVero[i] = mu + sigma * (-np.log(-np.log(GumbelProbaAcumul))) # creo curva con los paremetros de maxima verosimilitud
    if len(QMedido)>0:
        QMedReset = QMedido.reset_index(drop=True)
        QMedidoEstaciones[i] = QMedReset#.values.tolist() # esto para evitar los problemas con los indices
        FMesMedido = np.exp(-np.exp(-(QMedido-mu)/sigma)).reset_index(drop=True)
        TMedidoEstaciones[i] = (1/(1-FMesMedido))#.values.tolist() # esto para evitar los problemas con los indices. Si usara los valores del dataframe causa problema el orden


###### Weibull de los datos Sacando los años que no quiero
maximosAnualesHis=tablapivoteMax[MesEvaluacion]
quitarAñosTuple = list(cualesAnosQuitar.itertuples(index=False, name=None))
maximosAnualesHisSinRaros = maximosAnualesHis[~maximosAnualesHis.index.isin(quitarAñosTuple)] # para dejar solo los años que se quieren. El cosito "~" cambia lo valores de True a False y al reves

for i in estacionQ_ID:
    N = len(maximosAnualesHisSinRaros[i])
    IdEstacion = np.linspace(i, i, N,dtype=int)
    mm = np.linspace(1, N, N)
    Femp = 1-(mm/(N+1))
    Temp = (1/(1-Femp))
    if np.where(estacionQ_ID==i)[0][0] == 0:
        dfTemp=pd.DataFrame(Temp, index=[IdEstacion])
    else:
        temporal = pd.DataFrame(Temp, index=[IdEstacion])
        dfTemp = pd.concat([dfTemp, temporal], ignore_index=True)

#### limites limite
TQLimExtremo=pd.DataFrame(index=estacionQ_ID,columns=["TExtremoICSup"])
#### percentil 95 y calculo de T para ese valor
percentil95 = pd.pivot_table(completosBuenos, values='Valor',  index=['IdEstacion'], aggfunc=[lambda x: np.percentile(x,95)])
tablaIntermedia = pd.concat([percentil95['<lambda>'], parametrosEstaciones[['muMaxVero', 'sigmaMaxvero']]], axis=1, join="inner")
tablaIntermedia.rename(columns={'Valor':'QPercentil95'},inplace=True)

F95 = np.exp(-np.exp(-(tablaIntermedia['QPercentil95'] - tablaIntermedia['muMaxVero']) / tablaIntermedia['sigmaMaxvero']))
T95 = pd.Series(1 / (1 - F95),name="T95")

### crear tabla 421
tabla421QInfIC = pd.Series(dfQMinICGumbel.iloc[ubiTLimite], name='LimiteQICinf')
tabla421QSupIC = pd.Series(dfQMaxICGumbel.iloc[ubiTLimite], name='LimiteQICsup')
tabla421QMaxVero = pd.Series(dfQMaxVero.iloc[ubiTLimite], name='LimiteQmaxVero')
nombresEstaciones = pd.Series(codigosEstaciones["NombreEstacion"].values,index=codigosEstaciones["IdEstacion"],name="Nombre Estacion")

## Crear tabla 422
QmaxMesMedido = pd.pivot_table(datosMesCaudal, values='Valor',  index=['IdEstacion'], aggfunc="max")
retornoMaxVeroQmax = pd.Series(index=estacionQ_ID, name="TRetQMaxVero")
retornoICInferQmax = pd.Series(index=estacionQ_ID, name="TRetQLimInf")

for i in QmaxMesMedido.index:
    mu = parametrosEstaciones['muMaxVero'].loc[i]
    sigma = parametrosEstaciones['sigmaMaxvero'].loc[i]
    FAcumula = np.exp(-np.exp(-(QmaxMesMedido.loc[i] - mu) / sigma))
    Tacumulado = (1 / (1 - FAcumula))['Valor']
    retornoMaxVeroQmax.at[i] = Tacumulado
    TmasCerca = abs(dfQMinICGumbel[i] - QmaxMesMedido['Valor'].loc[i]).idxmin()
    posiTmasCerca = dfUbiMinICGumbel[i].loc[TmasCerca]
    muTemp = dfMuCombinacion[i].iloc[posiTmasCerca]
    sigmaTemp =dfSigmaCombinacion[i].iloc[posiTmasCerca]
    Ftemporal = np.exp(-np.exp(-(QmaxMesMedido.loc[i] - muTemp) / sigmaTemp))
    Ttemporal = (1 / (1 - Ftemporal))['Valor']
    retornoICInferQmax.loc[i] = Ttemporal

QmaxMesMedido.rename({"Valor":"Q max mensual"},axis=1,inplace=True)

tabla421 = pd.concat([nombresEstaciones, QmaxMesMedido, tabla421QMaxVero, tabla421QInfIC, tablaIntermedia['QPercentil95'], T95, QUmbralLim], axis=1, join="inner")
tabla421.to_excel(rutaSalida +'/Tablas/tabla421.xlsx')

tabla422 = pd.concat([nombresEstaciones, QmaxMesMedido, retornoMaxVeroQmax, retornoICInferQmax, QUmbralLim], axis=1, join="inner")
tabla422.to_excel(rutaSalida +'/Tablas/tabla422.xlsx')

tabla241 = tabla421[['Nombre Estacion', 'Q max mensual', 'LimiteQICinf', 'LimiteQUmbral']].copy()
tabla241["criterio_Gumbel"] = np.where(tabla241['Q max mensual'] > tabla241['LimiteQICinf'],"Extremo","-")
tabla241["criterio_Serie_Parcial"] = np.where(tabla241['Q max mensual'] > tabla241['LimiteQUmbral'],"Extremo","-")
tabla241 = tabla241[['Nombre Estacion', 'Q max mensual', 'LimiteQICinf', 'criterio_Gumbel', 'LimiteQUmbral', 'criterio_Serie_Parcial']]
tabla241.to_excel(rutaSalida +'/Tablas/tabla241.xlsx')

for i in estacionQ_ID:
    Qlimite = dfQMinICGumbel.iloc[ubiTLimite][i]
    TmasCerca = abs(dfQMaxICGumbel[i]-Qlimite).idxmin() # posicion en Q del IC superior que es más cercana al Q limite
    ubiVarTemp = dfUbiMaxICGumbel[i].loc[TmasCerca]
    muTemp = dfMuCombinacion[i].iloc[ubiVarTemp]
    sigmaTemp =dfSigmaCombinacion[i].iloc[ubiVarTemp]
    Flimite = np.exp(-np.exp(-(Qlimite - muTemp) / sigmaTemp))
    TlimExtremo = (1 / (1 - Flimite))
    TQLimExtremo.loc[i] = TlimExtremo

if MesEvaluacion == 'MaxAnual':
    complementoNombre = 'Maximos anuales'
else:
    complementoNombre = 'Maximos historicos ' + nombreMes

### Graficar todos juntos
print("inicia creacion de graficas")
for i in estacionQ_ID:
    nombre=(codigosEstaciones['NombreEstacion'][codigosEstaciones['IdEstacion']==i]).values.tolist()
    plt.figure(figsize = [6.6, 4.8])
    listaExtremoX = [TQLimExtremo.loc[i].to_list()[0], TLimite, TLimite]
    listaExtremoY = [tabla421QInfIC[i], tabla421QInfIC[i], tabla421QSupIC[i]]
    ax = plt.axes()
    plt.suptitle(nombre[0] + " Q vs $T_r$ (evaluación " + nombreMes + ")", fontweight="bold")
    ax.set_title("Intervalo de confianza 95% - " + complementoNombre)
    ax.plot(dfQMinICGumbel.index,dfQMinICGumbel[i], label="IC límite inferior", color="b", linewidth=0.6)
    ax.plot(tRetorno_generado,dfQMaxVero[i], label="Gumbel", color="black", linewidth=0.6)
    ax.plot(dfQMaxICGumbel.index,dfQMaxICGumbel[i], label="IC límite superior", color="c", linewidth=0.6)
    ax.plot(listaExtremoX, listaExtremoY, color="purple", label="Q límite", linewidth=0.6)
    ax.scatter(TMedidoEstaciones[i],QMedidoEstaciones[i], label="Q medidos", color="red")
    ax.scatter(dfTemp.loc[i],maximosAnualesHisSinRaros[i].sort_values(ascending=False), label=complementoNombre, color="black")
    ax.semilogx()
    ax.set_xlabel("$T_r (años)$", fontsize = 12)
    ax.set_ylabel('$Q (m^{3}/s)$', fontsize = 12)
    ax.legend()
    ax.grid(True, which="both", linewidth=0.4)
    plt_var = ax.get_figure()
    rutaImagen = rutaSalida + "/Graficas/"
    plt_var.savefig(rutaImagen + nombre[0] + " " + nombreMes + " " + str(añoEvaluado) +" Gumbel Maximo Anual.png", dpi = 300)
    plt.close('all')
