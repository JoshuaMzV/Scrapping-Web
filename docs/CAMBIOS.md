# 🔄 Cambios Realizados - Arquitectura Flexible por Marca

## Resumen
Se refactorizó la arquitectura del sistema para que funcione **por marca en lugar de por sitio**. Ahora puedes pegar links de CUALQUIER sitio donde se venda una marca específica, y el sistema detectará automáticamente dónde está cada producto.

---

## Cambios Principales

### 1️⃣ **Lógica de Scrapers (scrapers/nike.py y scrapers/sephora.py)**

**ANTES:** Un scraper único por sitio
```python
def scrape_nike(driver, wait, url):
    # Solo funcionaba con Nike.com
```

**AHORA:** Scraper inteligente que detecta automáticamente
```python
def scrape_nike(driver, wait, url):
    """Detecta automáticamente si es Nike.com, Amazon, eBay, etc."""
    if "nike.com" in url.lower():
        return scrape_nike_desde_nike_com(driver, wait, url)
    elif "amazon" in url.lower():
        return scrape_nike_desde_amazon(driver, wait, url)
    elif "ebay" in url.lower():
        return scrape_nike_desde_ebay(driver, wait, url)
```

**Ventajas:**
- ✅ Un archivo de scraper por marca
- ✅ Soporta Nike/Sephora de Nike.com, Amazon, eBay, etc.
- ✅ Fácil de extender: agregá sitios sin tocar `app.py`
- ✅ Un único Excel con todos los productos de la marca

### 2️⃣ **Backend Flask (app.py)**

**CAMBIOS:**
- Selecciona scraper según **marca**, no según sitio
- Pasa todos los links a UN ÚNICO scraper
- El scraper detecta cada sitio internamente
- Retorna una columna extra "Sitio" en el Excel

```python
# Ahora el flujo es:
marca = "Nike"
scraper = scrape_nike
for url in links:
    data = scraper(driver, wait, url)  # Auto-detecta sitio
```

### 3️⃣ **Interfaz HTML (templates/index.html)**

**ANTES:**
- Selector con 4 opciones: Nike, Sephora, Amazon, eBay
- Confuso para el usuario final

**AHORA:**
- Solo 2 opciones: Nike y Sephora
- Cada opción explica que acepta links de múltiples sitios
- Hint claro: "Puedes mezclar links de diferentes sitios"
- Nueva sección "¿Cómo funciona?" con pasos

### 4️⃣ **Excel Generado**

**Columnas incluidas:**
```
✓ Nombre del Producto
✓ Sitio (Nike.com, Amazon, eBay) - NUEVA
✓ Tallas Disponibles
✓ Precio Original (USD)
✓ Costo Final por Unidad (USD/GTQ)
✓ Precio Sugerido Venta (GTQ)
✓ Ganancia por Unidad (GTQ)
✓ Margen de Ganancia (%)
✓ URL Imagen
✓ URL Producto
```

---

## Flujo de Trabajo (Usuarios)

### ✅ Flujo Antiguo (NO SE USA)
```
1. Abre la app
2. Selecciona "Nike" en la marca
3. ❌ Espera a que solo acepte links de Nike.com
4. ❌ Para Amazon Nike, tiene que cambiar a "Amazon" en marca
5. ❌ Genera múltiples archivos Excel
```

### ✅ Flujo Nuevo (USA AHORA)
```
1. Abre la app
2. Selecciona "Nike" en marca
3. ✅ Pega links de Nike.com + Amazon + eBay
4. ✅ Generador detecta automáticamente cada sitio
5. ✅ Un solo Excel con todas las marcas Nike
6. ✅ Columna extra muestra dónde viene cada producto
```

---

## Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `scrapers/nike.py` | ✅ Refactorizado - ahora detecta sitios automáticamente |
| `scrapers/sephora.py` | ✅ Refactorizado - ahora detecta sitios automáticamente |
| `app.py` | ✅ Simplificado - lógica por marca, no por sitio |
| `templates/index.html` | ✅ Actualizado - texto más claro, solo 2 opciones |
| `static/css/style.css` | ✅ Agregados estilos para `.hint` e `.info-box` |

---

## Cómo Agregar Nueva Marca

### 📌 Ejemplo: Agregar Nike + Amazon + eBay

**Ya está hecho** ✅ - Los scrapers detectan automáticamente

### 📌 Ejemplo: Agregar Brand Nuevo (Ej: Adidas)

1. **Crear `scrapers/adidas.py`:**
```python
def scrape_adidas_desde_adidas_com(driver, wait, url): ...
def scrape_adidas_desde_amazon(driver, wait, url): ...
def scrape_adidas_desde_ebay(driver, wait, url): ...

def scrape_adidas(driver, wait, url):
    if "adidas.com" in url.lower():
        return scrape_adidas_desde_adidas_com(driver, wait, url)
    elif "amazon" in url.lower():
        return scrape_adidas_desde_amazon(driver, wait, url)
    # ... etc
```

2. **Editar `app.py`:**
```python
from scrapers.adidas import scrape_adidas, calcular_precios as adidas_calcular

@app.route('/scrape', methods=['POST'])
def scrape():
    # ... código existente ...
    elif 'adidas' in marca.lower():
        scraper_func = scrape_adidas
        calcular = adidas_calcular
```

3. **Editar `templates/index.html`:**
```html
<option value="adidas">👟 Adidas (links de Adidas.com, Amazon, eBay, etc.)</option>
```

¡Listo! No hay más cambios necesarios.

---

## Ventajas Técnicas

1. **Separación de Responsabilidades:**
   - Cada marca en su propio archivo
   - Cada sitio en su propia función

2. **Mantenibilidad:**
   - Agregar sitio = nueva función en scraper existente
   - Agregar marca = nuevo archivo scraper
   - No afecta `app.py`

3. **Escalabilidad:**
   - Soporta N marcas
   - Soporta N sitios por marca
   - Excel único por marca

4. **UX Mejorada:**
   - Usuario selecciona solo marca
   - Sistema hace lo demás automáticamente
   - Un archivo en lugar de múltiples

---

## Próximos Pasos (Opcionales)

- [ ] Agregar base de datos para guardar historial de catálogos
- [ ] Agregar notificaciones cuando el scraping falla
- [ ] Cachear imágenes para offline
- [ ] Agregar más marcas (Adidas, Puma, Gucci, etc.)

