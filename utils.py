import pandas as pd
from scipy.spatial import distance


def ordenar_ruta(df_cluster):
    """
    Este algoritmo recibe un DF de un solo clúster. En el, iniciará en el punto más sureño suyo, e irá
    iterativamente buscando el próximo punto más cercano y visitándolo
    """
    df_cluster = df_cluster.copy().reset_index(drop=True)
    
    idx_actual = df_cluster["Latitud"].idxmin() #Partimos siempre desde la casa más al sur del cluster
    
    ruta_indices = []
    visitados = set()
    
    while len(visitados) < len(df_cluster): #Hasta que no hayamos visitado todos los nodos:
        ruta_indices.append(idx_actual)
        visitados.add(idx_actual)
        
        punto_actual = (df_cluster.loc[idx_actual, "Latitud"], df_cluster.loc[idx_actual, "Longitud"])
        
        distancia_minima = float("inf")
        siguiente_idx = None
        
        for i in df_cluster.index: 
            """
            Dentro de todos los nodos, buscamos de los que aún no visitamos,
            cual es el que está más cerca de nuestro nodo actual.
            """
            if i not in visitados:
                punto_candidato = (df_cluster.loc[i, "Latitud"], df_cluster.loc[i, "Longitud"])
                dist = distance.euclidean(punto_actual, punto_candidato)
                
                if dist < distancia_minima:
                    distancia_minima = dist
                    siguiente_idx = i
        
        #Si es que encontramos un nodo (osea que aún quedaban) lo visitamos
        if siguiente_idx is not None:
            idx_actual = siguiente_idx

    #re-ordena la tabla original en base a la ruta encontrada
    df_ordenado = df_cluster.loc[ruta_indices].reset_index(drop=True)
    df_ordenado["Orden_Visita"] = range(1, len(df_cluster) + 1) #Guardamos de todas maneras indices que indican el orden a visitar
    
    return df_ordenado