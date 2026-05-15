import markdown
import os
import subprocess

def markdown_to_pdf(md_file, pdf_file):
    # Leer el archivo Markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convertir Markdown a HTML
    html_body = markdown.markdown(md_text, extensions=['tables'])

    # Envolver la primera tabla para inyectar el texto vertical al lado izquierdo
    table_start = html_body.find("<table>")
    if table_start != -1:
        table_end = html_body.find("</table>", table_start) + len("</table>")
        main_table_html = html_body[table_start:table_end]
        
        wrapper_html = f"""
        <div class="table-wrapper">
            <div class="vertical-text">
                <p>(Direcciones ordenadas por orden óptimo de visita)</p>
            </div>
            <div class="table-content">
                {main_table_html}
            </div>
        </div>
        """
        html_body = html_body[:table_start] + wrapper_html + html_body[table_end:]

    # CSS para dar el formato solicitado
    css = """
    <style>
        @page {
            size: A4;
            margin: 1.5cm;
        }
        body {
            font-family: Arial, sans-serif;
            font-size: 12px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .table-wrapper {
            position: relative;
            margin-bottom: 30px;
            padding-left: 25px;
        }
        .table-content {
            width: 100%;
        }
        .vertical-text {
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .vertical-text p {
            transform: rotate(-90deg);
            white-space: nowrap;
            margin: 0;
            color: #666;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 1px;
        }
        h3 {
            font-size: 14px;
            margin-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #f2f2f2;
        }
        td:first-child {
            width: 35%;
        }
        td:last-child {
            width: 40%;
        }
    </style>
    """

    # Combinar HTML base y CSS
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        {css}
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    html_file = 'temp_output.html'
    
    # Guardar el HTML temporal
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("Generando PDF usando WeasyPrint...")
    
    # Ejecutar WeasyPrint a través de la línea de comandos
    try:
        subprocess.run(['weasyprint', html_file, pdf_file], check=True)
        print(f"✅ PDF generado con éxito en: {pdf_file}")
    except FileNotFoundError:
        print("ERROR: No se encontró WeasyPrint en tu sistema.")
    except subprocess.CalledProcessError as e:
        print(f"Hubo un error al ejecutar WeasyPrint: {e}")
    finally:
        # Limpiar el archivo HTML temporal
        if os.path.exists(html_file):
            os.remove(html_file)

if __name__ == "__main__":
    markdown_to_pdf('template.md', 'plantilla_salida.pdf')
