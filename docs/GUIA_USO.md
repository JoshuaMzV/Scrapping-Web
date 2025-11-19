# 🎓 Guía de Uso - Sistema Flexible por Marca

## ¿Qué cambió?

**Ahora puedes pegar links de CUALQUIER sitio para una marca y el sistema detecta automáticamente dónde está cada producto.**

---

## 📚 Uso Básico

### Paso 1: Abre la Aplicación
```bash
# Windows - Click en iniciar.bat
iniciar.bat

# O si prefieres PowerShell
.\iniciar.ps1

# O desde terminal (con venv activado)
python run.py
```

### Paso 2: Selecciona Marca
En el formulario, selecciona:
- 👟 **Nike** - Para productos Nike
- 💄 **Sephora** - Para productos Sephora

**Nota:** Estos son MARCAS, no sitios. Puedes pegar links de cualquier sitio donde se venda esa marca.

### Paso 3: Pega los Links
En el área de texto, pega todos los links:
```
https://nike.com/us/es/producto1
https://amazon.com/dp/ASIN123
https://ebay.com/itm/123456789
https://nike.com/producto2
```

**✅ Ventajas:**
- Puedes mezclar sitios diferentes
- Un solo click para generar todo
- Un único Excel con todos los productos

### Paso 4: Genera el Catálogo
Click en **"🔄 Generar Catálogo"** y espera.

### Paso 5: Descarga el Archivo
El Excel se descargará automáticamente con nombre:
```
catalogo_nike_20251119_143052.xlsx
```

---

## 📊 Estructura del Excel

### Columnas:
| Columna | Ejemplo | Descripción |
|---------|---------|-------------|
| Nombre del Producto | Nike Air Force 1 | Nombre del artículo |
| **Sitio** | Nike.com | Dónde vino (Nike.com, Amazon, eBay) |
| Tallas Disponibles | 6, 7, 8, 9 | Tallas en stock |
| Precio Original (USD) | 110.00 | Precio de compra |
| Costo Final (USD) | 121.55 | Con costos adicionales |
| Costo Final (GTQ) | 947.09 | En quetzales |
| Precio Sugerido (GTQ) | 1185.86 | Precio de venta recomendado |
| Ganancia (GTQ) | 238.77 | Ganancia por unidad |
| Margen (%) | 20.14% | Porcentaje de ganancia |
| URL Imagen | https://... | Link a la imagen |
| URL Producto | https://... | Link al producto |

---

## 🎯 Ejemplos de Uso

### Ejemplo 1: Solo Nike.com
```
1. Selecciona: Nike
2. Pega 5 links de nike.com
3. Genera
4. Resultado: 1 Excel con 5 Nike
```

### Ejemplo 2: Mezclar Sitios
```
1. Selecciona: Nike
2. Pega:
   - 2 links de Nike.com
   - 3 links de Amazon
   - 4 links de eBay
3. Genera
4. Resultado: 1 Excel con 9 Nike
   Columna "Sitio" muestra dónde vino cada uno
```

### Ejemplo 3: Solo Sephora
```
1. Selecciona: Sephora
2. Pega:
   - 2 de Sephora.com
   - 3 de Amazon
   - 1 de eBay
3. Genera
4. Resultado: 1 Excel con 6 Sephora
```

---

## ⚙️ Configuración

### Cambiar Tasa de Cambio (GTQ)
```python
# Archivo: scrapers/nike.py (línea ~20)
TASA_CAMBIO_GTQ = 7.8  # ← Cambiar aquí
```

### Cambiar Porcentajes de Costo
```python
# Archivo: scrapers/nike.py (línea ~11-13)
PORCENTAJE_COSTO_CAJA = 8.0    # Costo de la caja
PORCENTAJE_COSTO_ENVIO = 5.0   # Costo de envío
PORCENTAJE_SEGURO = 3.0        # Seguro
```

### Cambiar Multiplicador de Precio
```python
# Archivo: scrapers/nike.py (línea ~17)
MULTIPLICADOR_PRECIO_MERCADO = 1.40  # 40% markup
FACTOR_DESCUENTO_VENTA = 0.90        # 10% descuento
```

---

## 🚨 Solución de Problemas

### "El sistema no detecta Amazon/eBay"
**Solución:** Verifica que el URL sea completo:
```
❌ amazon.com/dp
✅ https://www.amazon.com/dp/ASIN123
```

### "No aparece la talla disponible"
**Razones comunes:**
- El sitio no tiene selector de talla
- La talla está fuera de stock (oculta)
- El selector está dentro de un modal que no se abrió

**Workaround:** Deja "No especificadas" si no aparece

### "El Excel se genera pero está vacío"
**Verificar:**
1. ¿Seleccionaste marca?
2. ¿Pegaste URLs?
3. ¿Los URLs son válidos?
4. ¿Esperar a que termine el scraping?

Revisa la consola (terminal) para ver errores.

---

## 💡 Tips & Tricks

### Tip 1: Copia Rápida de URLs
Muchos navegadores permiten copiar URLs de múltiples pestaña:
```
1. Abre productos en 5 pestañas
2. Selecciona todas las pestañas (Ctrl+Click)
3. Click derecho → "Copiar las URL de las pestañas"
4. Pega en el formulario
```

### Tip 2: Copia desde Historial de Navegador
Si los links están en el historial:
```
1. Ctrl+H (Historial)
2. Busca dominio (amazon.com, ebay.com, etc.)
3. Click derecho → Copiar
4. Abre notepad, pega y limpia
5. Copia los URLs finales al formulario
```

### Tip 3: Validar URLs Antes de Generar
```
Abre cada URL en navegador para verificar que:
- El producto existe
- La página carga completa
- El precio es visible
```

### Tip 4: Personalizar Precios por Marca
Cada marca puede tener costos diferentes:
```
scrapers/nike.py:
  PORCENTAJE_COSTO_CAJA = 8.0

scrapers/sephora.py:
  PORCENTAJE_COSTO_CAJA = 10.0  # Sephora es más caro
```

---

## 🔐 Privacidad & Seguridad

**Importante:**
- ✅ Todo se procesa localmente en tu PC
- ✅ Los datos NO se envían a servidores externos
- ✅ Los archivos Excel se guardan en tu carpeta Descargas
- ✅ No hay login ni registro necesario

---

## 📞 Soporte

Si encuentras un error:

1. **Revisa la consola** (ventana negra)
2. **Copia el error completo**
3. **Anota:**
   - ¿Qué marca seleccionaste?
   - ¿Cuántos links pegaste?
   - ¿De qué sitios?
   - ¿Cuál es el error exacto?

---

## 🔄 Actualizar desde GitHub

Si hay actualizaciones:

1. Click en ⚙️ **Configuración** (en la app)
2. Pega la URL del repositorio:
   ```
   https://github.com/JoshuaMzV/Scrapping-Web
   ```
3. Click en **"Actualizar"**
4. Reinicia la app

---

## ✅ Checklist Antes de Usar

- [ ] Tengo Python activado (venv)
- [ ] Pude abrir la app (localhost:5000)
- [ ] La interfaz se ve bien
- [ ] Selecciono marca (Nike/Sephora)
- [ ] Pego URLs válidos
- [ ] Hago click en "Generar"
- [ ] El Excel se descarga

**¡Todo listo!** 🎉

