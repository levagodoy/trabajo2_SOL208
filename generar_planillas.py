import os
import pandas as pd
from generate_pdf import markdown_to_pdf

def generar_todas_las_planillas(df_enrutado: pd.DataFrame, df_reservas: pd.DataFrame, base_dir: str = "Parejas", dir_md: str = "planillas_temp", generar_pdfs: bool = True):
    """
    Genera las 33 planillas en formato Markdown y PDF para cada pareja.
    
    Parámetros:
    - df_enrutado: DataFrame que contiene las direcciones principales (10 por pareja) ya ordenadas.
    - df_reservas: DataFrame que contiene las direcciones de reserva (3 por clúster).
    - base_dir: Carpeta base donde se crearán las subcarpetas por cada pareja para los PDFs.
    - dir_md: Carpeta donde se guardarán los archivos Markdown temporales.
    """
    os.makedirs(dir_md, exist_ok=True)
    
    # Obtenemos los ID únicos de todas las parejas
    parejas = df_enrutado['ID_Pareja'].unique()
    
    for id_pareja in parejas:
        # Filtramos los datos de esta pareja en particular
        df_pareja = df_enrutado[df_enrutado['ID_Pareja'] == id_pareja]
        
        # Extraemos la información general (Nombres y Cluster) usando la primera fila
        primera_fila = df_pareja.iloc[0]
        nombres = primera_fila['Nombres_Completos']
        cluster_id = primera_fila['Cluster']
        
        # Filtramos las direcciones de reserva asociadas al clúster de esta pareja
        df_reserva_pareja = df_reservas[df_reservas['Cluster'] == cluster_id]
        
        # Obtener ruta absoluta del logo
        logo_path = os.path.abspath("logo.png")
        
        # Construcción dinámica del contenido Markdown basado en template.md
        lineas_md = []
        lineas_md.append('<div class="header">')
        lineas_md.append(f'  <img src="file://{logo_path}" style="height: 60px;" alt="Logo UC"/>')
        lineas_md.append('  <div>')
        lineas_md.append(f'    <span style="font-weight: normal;">Encuestadores: {nombres}<br>ID de Pareja: {id_pareja}</span>')
        lineas_md.append('  </div>')
        lineas_md.append('</div>')
        lineas_md.append('')
        
        # Tabla principal de direcciones ordenadas
        lineas_md.append('| Folio / Dirección Asignada | ¿Se realizó la visita? | Motivo de No Realización / Observaciones |')
        lineas_md.append('| :--- | :---: | :--- |')
        
        for _, row in df_pareja.iterrows():
            folio = row['Folio']
            direccion = row['Descripcion_Original']
            # Añadimos <br><br> para que el alto de la fila coincida con el estilo del template
            lineas_md.append(f'| **Folio {folio}**: {direccion} <br><br> | ( ✓ ) &nbsp;&nbsp;&nbsp;&nbsp; ( X ) | |')
            
        lineas_md.append('')
        lineas_md.append('<h3>Direcciones de Reserva</h3>')
        lineas_md.append('')
        
        # Tabla de direcciones de reserva
        lineas_md.append('| Folio / Dirección de Reserva | ¿Se realizó la visita? | Motivo de No Realización / Observaciones |')
        lineas_md.append('| :--- | :---: | :--- |')
        
        for _, row in df_reserva_pareja.iterrows():
            folio = row['Folio']
            direccion = row['Descripcion_Original']
            lineas_md.append(f'| **Folio {folio}**: {direccion} <br><br> | ( ✓ ) &nbsp;&nbsp;&nbsp;&nbsp; ( X ) | |')
            
        # Creamos la carpeta específica para esta pareja (solo para los PDF finales)
        carpeta_pareja = os.path.join(base_dir, str(id_pareja))
        if generar_pdfs:
            os.makedirs(carpeta_pareja, exist_ok=True)
        
        # Guardamos el archivo Markdown
        nombre_archivo_md = os.path.join(dir_md, f'planilla_pareja_{id_pareja}.md')
        with open(nombre_archivo_md, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lineas_md))
            
        # Opcional: convertir a PDF
        if generar_pdfs:
            nombre_archivo_pdf = os.path.join(carpeta_pareja, f'planilla_pareja_{id_pareja}.pdf')
            markdown_to_pdf(nombre_archivo_md, nombre_archivo_pdf)
            
    print(f"✅ Se han generado {len(parejas)} planillas. PDFs guardados en '{base_dir}/<ID_Pareja>/' y MDs en '{dir_md}/'.")
