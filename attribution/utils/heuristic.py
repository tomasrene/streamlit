import pandas as pd
import numpy as np
from collections import Counter

#############################################################################
##########                     MAIN FUNCTION                       ##########
#############################################################################
def main(data):
    '''
    DESCRIPCION
    Toma un dataframe con recorridos de usuarios que pueden terminar o no en conversion.
    A partir de eso, atribuye las conversiones segun modelos heuristicos: first, last, linear.

    PARAMETROS
    
    
    RETURN
    - first_conversion: diccionario con las conversiones por canal segun first click
    - last_conversion: diccionario con las conversiones por canal segun last click
        
    REQUIRIMIENTOS
    - Tipo list o dataframe
    - Ordenado cronologicamente
    - 3 columnas en orden: usuario, canal y conversion (booleano)
    
    '''
    # validar input
    data = formatear(data)
    
    # obtener tuplas de caminos con conversion
    caminos = obtener_caminos(data)
    
    # separar los canales de los caminos
    data_total = [[k.split(">"),v] for k,v in caminos.items()]
    
    # guardar el canal que corresponda
    data_first = [[i[0][0],i[1]] for i in data_total]
    data_last = [[i[0][-1],i[1]] for i in data_total]
    data_linear = [[canal,i[1]/len(i[0])] for i in data_total for canal in i[0]]
       
    # calcular las conversiones segun cada modelo
    first = pd.DataFrame(data_first,columns=['canal','first']).groupby('canal').sum()
    last = pd.DataFrame(data_last,columns=['canal','last']).groupby('canal').sum()
    linear = pd.DataFrame(data_linear, columns=['canal','linear']).groupby('canal').sum()
        
    return first, last, linear
#############################################################################

#############################################################################
def formatear(data):
    '''
    Toma el dataset (lista o dataframe), valida los tipos de datos y transforma el tipo y nombre de las columnas
    para optimizar el procesamiento
    '''
    
    # definir el nombre de las columnas
    columnas = ['usuario','canal','conversion']
    
    # formatear los datos segun el tipo
    if isinstance(data,list):
        data = pd.DataFrame(data,columns=columnas)
    if isinstance(data,pd.DataFrame):
        data.columns = columnas
    else:
        print("Error en el formato")
        
    # pasar usuario a numerico
    data['usuario'] = pd.factorize(data['usuario'])[0]
    
    return data
#############################################################################

#############################################################################
def obtener_caminos(data):
    '''
    Toma un dataframe de sesiones, agrupa por usuario y aplica una funcion
    para obtener los caminos de canales unicos de cada uno hasta la conversion.
    '''
    # agrupar por usuario, aplicar funcion y desanidar las listas
    caminos = data.groupby('usuario').apply(funcion_list).dropna().explode()

    # agrupar y contar ocurrencias de cada camino
    caminos = dict(Counter([i[0] for i in caminos.tolist()]))
    
    return caminos
#############################################################################

#############################################################################
def funcion_list(data):
    '''
    Toma un data frame de caminos por cada usuario. Los procesa para devolver caminos con formato Shapley.
    Si no hay conversion, retorna. Agrupa canales unicos, ordenados y por cada conversion.
    '''
    # retornar si no hay conversion
    if data.conversion.sum() == 0:
        return np.nan
    
    # crear contenedores
    final = []
    caminos = []
    
    # iterar sobre las sesiones
    for i in data.itertuples():
        caminos.append(i.canal)
        
        # si hay conversion, agregar los canales unicos anteriores y ordenados
        if i.conversion == 1:
            final.append(['>'.join(sorted(set(caminos)))])
            
            # resetear
            caminos = []
    
    return final
#############################################################################
