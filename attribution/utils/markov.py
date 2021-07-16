
import pandas as pd
import numpy as np

#############################################################################
##########                     MAIN FUNCTION                       ##########
#############################################################################
def markov_chain(data, attributes = True):
    '''
    Toma un dataframe con recorridos de usuarios que pueden terminar o no en conversion.
    A partir de eso, calcula un modelo de markov de orden 1 para atribuir las conversiones.
    
    PARAMETROS
    ----------
    data: dataFrame or list
        Dataframe o list de usuarios, canales y conversion ordenados cronologicamente
    
    attributes: bool, default = True
        True para retornar los valores absolutos de las conversiones, False para el proporcional
    
    RETURN
    ------
    removal_effect: dict
        Diccionario con los canales como keys y los valores como valor absoluto o proporcion
    
    '''
    # validar input
    data = formatear(data)

    # obtener caminos formateados para Markov
    caminos = obtener_caminos_markov(data)
    
    # obtener matriz de transicion de probabilidades
    matriz = calcular_matriz_transicion(caminos)
    
    # obtener el diciconario del removal effect de cada canal
    removal_effect = calcular_removal_effect(matriz)
        
    # atribuir segun los parametros de la funcion
    if attributes:
        removal_effect.update((x, y*np.sum(data['conversion'].tolist())) for x, y in removal_effect.items())
    
    # redondear valores
    removal_effect = {k:round(v,4) for k,v in removal_effect.items()}
    
    # pasar a data frame
    atribucion = pd.DataFrame.from_dict(removal_effect,orient='index',columns=["markov"])
    
    return atribucion
#############################################################################

#############################################################################
def formatear(data):
    """
    Valida el tipo de datos y asigna nombres a las columnas. Devuelve un dataframe.

    """
    
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
def obtener_caminos_markov(data):
    '''
    Toma un dataframe de sesiones, agrupa por usuario y aplica una funcion
    para obtener los caminos de cada uno hasta la conversion incluyendo los que no convierten
    y sin eliminar canales repetidos.
    '''    
    def funcion_list_markov(data):
        '''
        Toma un data frame por usuario, crea contenedores y va iterando almacenando los canales 
        que llevan a la conversion, agregando al final los canales que llevan a la no conversion
        '''
        # crear contenedores
        final = []
        caminos = []

        # iterar sobre las sesiones
        for i in data.itertuples():
            caminos.append(i.canal)

            # si hay conversion, agregar los canales anteriores
            if i.conversion == 1:
                final.append([">".join(caminos),1])
                # resetear
                caminos = []
        # agregar canales sobrantes si los hay
        if len(caminos)>0:
            final.append([">".join(caminos),0])

        return final
    
    # aplicar la funcion a cada usuario
    caminos = data.groupby('usuario',observed=True).apply(funcion_list_markov).explode().tolist()
    
    return caminos
#############################################################################

#############################################################################
def calcular_matriz_transicion(data):
    '''
    Toma un dataset de caminos y lo convierte en una matriz de transiciones entre canales para calcular Markov.
    Incluye como canal (start) al inicio de cada recorrido y (null) o (conversion) segun el resultado.    
    '''
    # agregar estados iniciales y finales
    recorridos = ["(start)>"+i[0]+">(conversion)" if i[1] == 1 else "(start)>"+i[0]+">(null)" for i in data]
    
    # armar las transiciones con pares de canales
    transiciones = list(map(lambda x:list(zip(x[:],x[1:])),[i.split(">") for i in recorridos]))
    
    # darle formato de inicio y fin
    transiciones_formato = pd.DataFrame([j for i in transiciones for j in i],columns=['start','end'])
    
    # armar la matriz normalizada con las transiciones
    matriz = pd.crosstab(index=transiciones_formato['start'],columns=transiciones_formato['end'], normalize = 'index', dropna = False)
    
    # chequear si falta alguna columna y agregarla
    for columna in ['(conversion)','(null)']:
        if columna not in matriz.columns:
            matriz.insert(0,columna,np.zeros(matriz.shape[0]))
    
    # agregar start como posible final
    matriz.insert(0,'(start)',np.zeros(matriz.shape[0]))
    
    return matriz
#############################################################################

#############################################################################
def calcular_markov(data):
    '''
    Toma una matriz de transiciones entre los canales (con null, start y conversion) y devuelve la tasa de
    conversion partienda del estado start.
    '''
    # armar matriz de convergencia (columnas finales)
    removal_to_conv = data[['(null)','(conversion)']]
    
    # armar matriz de canales (filas de canales)
    removal_to_non_conv = data.drop(['(conversion)','(null)'],axis=1)
    
    # calcular la inversa de (I - canales)
    removal_inv_diff = np.linalg.inv(np.identity(len(removal_to_non_conv.columns)) - np.asarray(removal_to_non_conv))
    
    # calcular producto matricial de la inversa y la de convergencia
    removal_dot_prod = np.dot(removal_inv_diff, np.asarray(removal_to_conv))
        
    # devolver la probabilidad de conversion del inicio en start
    cvr = pd.DataFrame(removal_dot_prod,index=removal_to_conv.index)[[1]].loc['(start)'].values[0]
    
    return cvr
#############################################################################

#############################################################################
def calcular_removal_effect(data):
    '''
    Toma una matriz de transiciones entre los canales (con null, start y conversion) y calcula el removal effect
    de cada uno de los canales.
    
    Para eso, itera sobre los canales (sin start, conversion y null) y calcula la tasa de conversion general. 
    Luego, borra la fila del canal, asigna sus probabilidades de transicion a null y recalcula la
    tasa de conversion.
    
    Devuelve la proporcion normalizada en que disminuye la tasa de conversion original.
    
    '''
    # calcular conversion general y guardar
    cr_general = calcular_markov(data)
    
    # crear un diccionario para almacenar removal effect de cada canal
    removal_effect = {}
    
    # iterar sobre canales validos
    for channel in data.columns:
        if channel not in ['(start)','(conversion)','(null)']:
            
            # borrar linea y columna del canal
            matriz_canal = data.drop(channel, axis=1).drop(channel, axis=0)
            
            # reasignar probabilidad a nulo
            for column in matriz_canal.columns:
                if column not in ['(conversion)','(null)']:
                    faltante = float(1) - np.sum(list(matriz_canal.loc[column]))
                    if faltante != 0:
                        matriz_canal.loc[column]['(null)'] = faltante
            
            # calcular la conversion
            cr_canal = calcular_markov(matriz_canal)
           
            # calcular la variacion de la conversion
            removal_effect_canal = 1 - cr_canal / cr_general
            
            # guardar en diccionario
            removal_effect[channel] = removal_effect_canal
    
    # calcular valor total
    suma = np.sum(list(removal_effect.values()))
    
    # normalizar
    removal_effect_normalizado = {key: (value / suma) for key, value in removal_effect.items()}

    # devolver diccionario
    return removal_effect_normalizado
#############################################################################