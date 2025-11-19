import pandas as pd
import os
import glob

downloads_path = os.path.expanduser("~\\Downloads")
files = sorted(glob.glob(os.path.join(downloads_path, "catalogo_nike_*.xlsx")), key=os.path.getmtime, reverse=True)

if files:
    latest = files[0]
    print(f"\n📄 Leyendo: {os.path.basename(latest)}")
    print("=" * 120)
    
    df = pd.read_excel(latest)
    print(f"Filas: {len(df)}, Columnas: {len(df.columns)}\n")
    
    for idx, row in df.iterrows():
        print(f"{'='*120}")
        print(f"PRODUCTO {idx + 1}:")
        print(f"{'='*120}")
        print(f"  Nombre: {row['Nombre del Producto'][:70]}")
        print(f"  Sitio: {row['Sitio']}")
        print(f"  Precio USD: {row['Precio Original (USD)']}")
        print(f"  Tallas: {row['Tallas Disponibles']}")
        print()
else:
    print("❌ No se encontraron archivos Excel")
