# ATRIBUCION
En la carpeta utils estan los scripts para correr las librerias para calcular la atribucion segun los metodos tradicionales.

En todos los casos la funcion principal a utilizar es main. Toma como input una lista o dataframe de touchpoints de usuario ordenados cronologicamente con usuario, touchpoint y conversion (boolean) y devuelve un dataFrame con la atribucion segun el metodo elegido.

## MARKOV
Calcula un modelo de Markov de orden 1 segun la implementacion de Anderl et. al. (2016) del removal effect.

## SHAPLEY
Calcula el valor de Shapley para los canales que intervienen en los caminos de conversion. La ecuacion caracteristica toma como valor de cada coalicion el de la suma de sus subcoaliciones.

## HEURISTICOS
Calcula la atribucion segun los modelos first, last y linear.