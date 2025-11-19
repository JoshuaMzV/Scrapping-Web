import pandas as pd
import os

downloads_path = os.path.expanduser('~\\Downloads')
excel_files = [f for f in os.listdir(downloads_path) if f.startswith('catalogo_nike_') and f.endswith('.xlsx')]

if excel_files:
    excel_files.sort(key=lambda x: os.path.getmtime(os.path.join(downloads_path, x)), reverse=True)
    latest_file = excel_files[0]
    file_path = os.path.join(downloads_path, latest_file)
    
    print(f'📄 ARCHIVO: {latest_file}')
    print('=' * 140)
    
    df = pd.read_excel(file_path)
    
    print(f'\nColumnas: {list(df.columns)}')
    print(f'Filas: {len(df)} productos\n')
    
    for idx, row in df.iterrows():
        print(f'\n🔹 Producto {idx+1}: {row["Nombre del Producto"][:60]}')
        print(f'   Sitio: {row["Sitio"]}')
        print(f'   Precio USD: ${row["Precio Original (USD)"]}')
        tallas = str(row["Tallas Disponibles"])[:70]
        print(f'   Tallas: {tallas}')
        print(f'   Precio Venta GTQ: Q{row["Precio Sugerido Venta (GTQ)"]}')
else:
    print('No se encontraron archivos')
