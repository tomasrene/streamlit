import pandas as pd
import numpy as np
from itertools import permutations
from itertools import combinations
from collections import Counter

#############################################################################
##########                     MAIN FUNCTION                       ##########
#############################################################################
def shapley_value(data):
    """
    Toma un dataframe con recorridos de usuarios que pueden terminar o no en conversion.
    A partir de eso, calcula las conversiones de cada canal segun el valor de Shapley.
   
    PARAMETERS
    ----------
    data: dataFrame or list
        Dataframe o list de usuarios, canales y conversion ordenados cronologicamente

    RETURN
    ------
    atribucion: dataFrame
        Los canales como indice y una columna con las conversiones de cada uno.
    """
    
    # chequear formato
    data = formatear(data)
    
    # calcular conversiones_totales
    conversiones_totales = sum(data.conversion)

    # obtener coaliciones posibles y gran coalicion de los n canales unicos
    coaliciones, gran_coalicion = obtener_coaliciones(data)
    
    # obtener caminos
    caminos = obtener_caminos_shapley(data)
    
    # agregar resultado al data frame de coaliciones
    coaliciones.update(caminos)
    
    # calcular el valor de shapley
    shapley_result = calcular_shapley(coaliciones,gran_coalicion)

    # dar formato
    shapley_result = pd.DataFrame(shapley_result, index = gran_coalicion)
    
    # atribuir conversiones totales segun valor de shapley
    atribucion = pd.DataFrame(round(shapley_result.sum()/sum(shapley_result.sum())*conversiones_totales,2),columns=['shapley'])
    
    return atribucion
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
def obtener_coaliciones(data):
    '''
    Pasando un data frame de recorridos, devuelve las coaliciones posibles entre los canales unicos y
    todas las permutaciones de la gran coalicion de los n canales unicos.
    '''
    # obtener canales unicos
    canales_unicos = list(sorted(set(data.canal)))
    
    # obtener las combinaciones posibles a partir de los canales unicos
    canales_combinados = ['>'.join(i) for i in combinar(canales_unicos)]
    
    # armar un diccionario con todas las coaliciones posibles
    coaliciones = {camino:0 for camino in canales_combinados}
    
    # armar la gran coalicion y sus permutaciones
    gran_coalicion = permutar([canales_unicos])    
        
    return coaliciones, gran_coalicion
#############################################################################

#############################################################################
def obtener_caminos_shapley(data):
    '''
    Toma un dataframe de sesiones, agrupa por usuario y aplica una funcion
    para obtener los caminos de canales unicos de cada uno hasta la conversion.
    '''
    # agrupar por usuario, aplicar funcion y desanidar las listas
    caminos = data.groupby('usuario').apply(funcion_list_shapley).dropna().explode()

    # agrupar y contar ocurrencias de cada camino
    caminos = dict(Counter([i[0] for i in caminos.tolist()]))
    
    return caminos
#############################################################################

#############################################################################
def funcion_list_shapley(data):
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

#############################################################################
def funcion_caracteristica(data):
    '''
    Toma un data frame de coaliciones y conversiones y lo escala utilizando la funcion
    caracteristica aplicada para Shapley value: el valor de una coalicion es la suma
    del valor de sus subsets.
    '''
    
    # guardar un original de base para los calculos
    base = data.copy()
    
    # iterar para cada camino
    for camino in data.keys():
        
        valor_camino = 0
        
        # iterar por cada canal
        for canal in combinar(camino.split(">")):
            
            # acumular el valor original
            valor_camino += base['>'.join(canal)]
        
        # reemplazar el valor en coaliciones
        data[camino] = valor_camino   
    
    return data
#############################################################################

#############################################################################
def calcular_shapley(coaliciones,gran_coalicion):
    '''
    Toma una lista de gran coaliciones y calcula el valor de Shapley para cada canal.
    '''
    def calcular(linea):
        # establer placeholders
        suma = 0
        canales = []
        devolver = {}

        # para cada canal de la gran coalicion
        for canal in list(linea):
            # acumular canales
            canales.append(canal)
            # restar valor acumulado
            valor = max(coaliciones['>'.join(sorted(canales))] - suma,0)
            # registrar valor en diccionario final
            devolver[canal] = valor
            # incrementar la suma acumulada
            suma += valor

        return devolver
    
    # calcular para cada linea de la gran coalicion
    shapley = list(map(calcular,gran_coalicion))
    
    return shapley
#############################################################################

#############################################################################
def combinar(lista):
    '''
    Pasando una lista de elementos, devuelve una lista exhaustiva con la combinacion de todos los elementos
    '''
    # ordenar
    lista = sorted(lista)
    
    # calcular el numero de elementos
    numero_de_elementos = len(lista)
    
    # crear un rango de 1 a n
    rango = range(1,numero_de_elementos+1)
    
    # hacer la combinatoria
    combinacion = [list(combinations(lista,i)) for i in rango]
    
    # desanidar las listas
    resultado = [tupla for sublist in combinacion for tupla in sublist]
    
    return resultado
#############################################################################

#############################################################################
def permutar(lista, orden_original = True):
    '''
    Pasando una lista de tuplas, devuelve una lista de las tuplas permutadas
    '''
    # generar las permutaciones
    permutaciones = [list(permutations(tupla)) for tupla in lista]
    
    # desanidar las listas
    resultado = [tupla for sublist in permutaciones for tupla in sublist]
    
    return resultado
#############################################################################