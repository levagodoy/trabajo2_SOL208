import pandas as pd
import os
import xml.etree.ElementTree as ET
import zipfile
import colorsys
import random

"""
Algoritmo de carga y guardado fue hecho por completo por Gemini 3.1 Pro Preview,
y modificado por nosotros para que cumpla con los requesitos de nuestro trabajo
"""

# 1. Cargar y parsear el KML
def transformar_kml(path_mapa: str):
    tree = ET.parse(path_mapa)
    root = tree.getroot()

    # Definir el espacio de nombres (namespace) estándar de KML
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    datos = []

    for folder in root.findall('.//kml:Folder', ns):
        nombre_carpeta = folder.find('kml:name', ns).text
        
        if nombre_carpeta in ['Estrato A', 'Estrato B']:
            for placemark in folder.findall('kml:Placemark', ns):
                id_punto = placemark.find('kml:name', ns).text
                
                # NUEVO: Extraer la descripción original (Dirección exacta)
                desc_node = placemark.find('kml:description', ns)
                # A veces la descripción puede estar vacía, usamos un if para evitar errores
                descripcion_original = desc_node.text if desc_node is not None else "Sin descripción"
                
                coord_str = placemark.find('.//kml:coordinates', ns).text.strip()
                lon, lat, *alt = coord_str.split(',')
                
                datos.append({
                    'Folio': id_punto,
                    'Estrato': nombre_carpeta,
                    'Latitud': float(lat),
                    'Longitud': float(lon),
                    'Descripcion_Original': descripcion_original # Guardamos la dirección aquí
                })

    df = pd.DataFrame(datos)
    return(df)

def guardar_kmz(df: pd.DataFrame):
    # 5. Generar el nuevo archivo KML (Estilos integrados directamente)
    kml_lineas = []

    kml_lineas.append('<?xml version="1.0" encoding="UTF-8"?>')
    kml_lineas.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    kml_lineas.append('  <Document>')
    kml_lineas.append('    <name>Zonas de Trabajo - Encuestadores</name>')
    kml_lineas.append('    <Folder>')
    kml_lineas.append('      <name>Rutas Consolidadas</name>')

    # --- PREPARAR LA PALETA DE 33 COLORES ---
    colores_kml = []
    golden_ratio = 0.618033988749895
    h = 0.1 

    # Ya sabemos que son exactamente 33 zonas, pre-calculamos la paleta
    for i in range(33): 
        h += golden_ratio
        h %= 1.0
        s = 0.5 + (i % 2) * 0.5
        v = 0.6 + (i % 3) * 0.2
        
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        hex_kml = f"ff{int(b*255):02x}{int(g*255):02x}{int(r*255):02x}"
        colores_kml.append(hex_kml)

    # Desordenar para evitar que zonas pegadas tengan colores parecidos
    random.seed(42)
    random.shuffle(colores_kml)

    # --- ITERAR SOBRE TODA LA MUESTRA (Añadiendo el estilo repetido) ---
    for index, fila in df.iterrows():
        cluster_id = fila["Cluster"]
        color_asignado = colores_kml[cluster_id]
        
        kml_lineas.append('      <Placemark>')
        kml_lineas.append(f'        <name>{fila["Folio"]}</name>')
        
        # LA DESCRIPCIÓN AHORA TIENE LOS NOMBRES REALES DE LOS ALUMNOS
        descripcion_rica = (
            f"<b>Dirección:</b> {fila['Descripcion_Original']}<br><br>"
            f"<b>Equipo Asignado:</b> {fila['Nombre_Completo']}<br>"
            f"<b>Grupo Original:</b> {fila['Grupo']}<br>"
            f"<b>Pareja N°:</b> {fila['ID_Pareja']}<br>"
            f"<b>Zona de Trabajo:</b> {cluster_id + 1}<br>"
            f"<b>Perfil:</b> {fila['Estrato']}"
        )
        kml_lineas.append(f'        <description><![CDATA[{descripcion_rica}]]></description>')        
        # ESTILO INLINE
        kml_lineas.append('        <Style>')
        kml_lineas.append('          <IconStyle>')
        kml_lineas.append(f'            <color>{color_asignado}</color>')
        kml_lineas.append('            <scale>1.1</scale>')
        kml_lineas.append('            <Icon>')
        kml_lineas.append('              <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>')
        kml_lineas.append('            </Icon>')
        kml_lineas.append('            <hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/>')
        kml_lineas.append('          </IconStyle>')
        kml_lineas.append('        </Style>')
        
        kml_lineas.append('        <Point>')
        kml_lineas.append(f'          <coordinates>{fila["Longitud"]},{fila["Latitud"]},0</coordinates>')
        kml_lineas.append('        </Point>')
        kml_lineas.append('      </Placemark>')

    kml_lineas.append('    </Folder>')
    kml_lineas.append('  </Document>')
    kml_lineas.append('</kml>')

    # --- COMPRIMIR A KMZ ---
    kml_content = '\n'.join(kml_lineas)
    nombre_archivo_kmz = 'Mapa_Clusters_Encuestadores.kmz'

    with zipfile.ZipFile(nombre_archivo_kmz, 'w', zipfile.ZIP_DEFLATED) as kmz:
        kmz.writestr('doc.kml', kml_content)

    print(f"\n¡Éxito! El archivo '{nombre_archivo_kmz}' está listo con los estilos inyectados punto por punto.")

def exportar_rutas_kml_por_pareja(df_enrutado, base_dir="Parejas"):
    """
    Toma el DataFrame enrutado y genera un archivo KML con la línea de ruta 
    para cada pareja, guardándolo en la estructura: Parejas/{ID_Pareja}/
    """
    parejas_unicas = sorted(df_enrutado['ID_Pareja'].unique())
    
    for pareja in parejas_unicas:
        # 1. Crear la estructura de carpetas: Parejas/{ID_Pareja}/
        carpeta_pareja = os.path.join(base_dir, str(pareja))
        os.makedirs(carpeta_pareja, exist_ok=True)
        
        # 2. Filtrar y ordenar las direcciones de esta pareja
        df_pareja = df_enrutado[df_enrutado['ID_Pareja'] == pareja].copy()
        df_pareja = df_pareja.sort_values('Orden_Visita')
        
        # 3. Construir el KML
        kml_lineas = []
        kml_lineas.append('<?xml version="1.0" encoding="UTF-8"?>')
        kml_lineas.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
        kml_lineas.append('  <Document>')
        kml_lineas.append(f'    <name>Ruta de Trabajo - Pareja {pareja}</name>')
        
        # --- PASO A: Crear los marcadores (Puntos) ---
        for _, fila in df_pareja.iterrows():
            kml_lineas.append('    <Placemark>')
            kml_lineas.append(f'      <name>Paso {fila["Orden_Visita"]}: {fila["Folio"]}</name>')
            
            descripcion = f"Dirección: {fila.get('Descripcion_Original', 'Sin info')}<br>Perfil: {fila['Estrato']}"
            kml_lineas.append(f'      <description><![CDATA[{descripcion}]]></description>')
            
            kml_lineas.append('      <Point>')
            kml_lineas.append(f'        <coordinates>{fila["Longitud"]},{fila["Latitud"]},0</coordinates>')
            kml_lineas.append('      </Point>')
            kml_lineas.append('    </Placemark>')
            
        # --- PASO B: Crear la Línea de Ruta (LineString) ---
        kml_lineas.append('    <Placemark>')
        kml_lineas.append('      <name>Línea de Navegación</name>')
        kml_lineas.append('      <Style>')
        kml_lineas.append('        <LineStyle>')
        kml_lineas.append('          <color>ff0000ff</color>') # Color rojo (AABBGGRR)
        kml_lineas.append('          <width>4</width>')
        kml_lineas.append('        </LineStyle>')
        kml_lineas.append('      </Style>')
        kml_lineas.append('      <LineString>')
        kml_lineas.append('        <tessellate>1</tessellate>')
        kml_lineas.append('        <coordinates>')
        
        for _, fila in df_pareja.iterrows():
            kml_lineas.append(f'          {fila["Longitud"]},{fila["Latitud"]},0')
            
        kml_lineas.append('        </coordinates>')
        kml_lineas.append('      </LineString>')
        kml_lineas.append('    </Placemark>')
        
        kml_lineas.append('  </Document>')
        kml_lineas.append('</kml>')
        
        # 4. Guardar el archivo dentro de la subcarpeta de la pareja
        nombre_archivo = os.path.join(carpeta_pareja, 'Ruta_Asignada.kml')
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write('\n'.join(kml_lineas))
            
    print(f"¡Éxito! Se exportaron las rutas para {len(parejas_unicas)} parejas en la carpeta '{base_dir}/'.")