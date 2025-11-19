// Navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = link.getAttribute('href');
        
        // Remove active class from all sections and links
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        
        // Add active class to target section and link
        document.querySelector(target).classList.add('active');
        link.classList.add('active');
    });
});

// Button Actions
document.getElementById('btnGenerar').addEventListener('click', generarCatalogo);
document.getElementById('btnLimpiar').addEventListener('click', limpiarFormulario);
document.getElementById('btnActualizar').addEventListener('click', actualizarDesdeGitHub);

// Generar Catálogo
async function generarCatalogo() {
    const marca = document.getElementById('marca').value;
    const links = document.getElementById('links').value;

    if (!marca) {
        mostrarError('Por favor selecciona una marca');
        return;
    }

    if (!links.trim()) {
        mostrarError('Por favor ingresa al menos un link');
        return;
    }

    const linkArray = links.split('\n').filter(l => l.trim());

    // Mostrar progreso
    document.getElementById('progressContainer').style.display = 'block';
    document.getElementById('resultContainer').style.display = 'none';
    document.getElementById('btnGenerar').disabled = true;

    try {
        const response = await fetch('/scrape', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                marca: marca,
                links: linkArray
            })
        });

        const data = await response.json();

        if (data.success) {
            mostrarExito('¡Catálogo generado exitosamente!');
            
            // Preguntar al usuario si quiere descargar
            setTimeout(() => {
                if (confirm('¿Descargar el catálogo ahora?')) {
                    descargarExcel(data.filename, data.excel_data);
                }
            }, 500);
            
            limpiarFormulario();
        } else {
            mostrarError(data.message || 'Error al generar catálogo');
        }
    } catch (error) {
        mostrarError('Error de conexión: ' + error.message);
    } finally {
        document.getElementById('progressContainer').style.display = 'none';
        document.getElementById('btnGenerar').disabled = false;
    }
}

// Limpiar Formulario
function limpiarFormulario() {
    document.getElementById('marca').value = '';
    document.getElementById('links').value = '';
    document.getElementById('resultContainer').style.display = 'none';
}

// Mostrar Error
function mostrarError(mensaje) {
    const resultContainer = document.getElementById('resultContainer');
    resultContainer.style.display = 'block';

    document.getElementById('successMessage').style.display = 'none';
    document.getElementById('errorMessage').style.display = 'block';
    document.getElementById('errorText').textContent = mensaje;
}

// Mostrar Éxito
function mostrarExito(mensaje) {
    const resultContainer = document.getElementById('resultContainer');
    resultContainer.style.display = 'block';

    document.getElementById('errorMessage').style.display = 'none';
    document.getElementById('successMessage').style.display = 'block';
}

// Descargar Excel desde base64
function descargarExcel(filename, excelBase64) {
    const binaryString = atob(excelBase64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    
    const blob = new Blob([bytes], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}

// Actualizar desde GitHub
async function actualizarDesdeGitHub() {
    // Confirmar actualización
    if (!confirm('¿Descargar e instalar las últimas actualizaciones de GitHub?\n\nLa aplicación se reiniciará automáticamente después.')) {
        return;
    }

    document.getElementById('btnActualizar').disabled = true;
    document.getElementById('updateContainer').style.display = 'block';

    try {
        const response = await fetch('/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})  // No se envía URL, está hardcodeada en el backend
        });

        const data = await response.json();

        if (data.success) {
            mostrarExitoActualizacion(data.message + ' (v' + data.version + ')');
        } else {
            mostrarErrorActualizacion(data.message || 'Error al actualizar');
        }
    } catch (error) {
        mostrarErrorActualizacion('Error de conexión: ' + error.message);
    } finally {
        document.getElementById('btnActualizar').disabled = false;
    }
}

// Mostrar Error de Actualización
function mostrarErrorActualizacion(mensaje) {
    document.getElementById('updateContainer').style.display = 'block';
    document.getElementById('updateSuccess').style.display = 'none';
    document.getElementById('updateError').style.display = 'block';
    document.getElementById('updateErrorText').textContent = mensaje;
}

// Mostrar Éxito de Actualización
function mostrarExitoActualizacion(mensaje) {
    document.getElementById('updateContainer').style.display = 'block';
    document.getElementById('updateError').style.display = 'none';
    document.getElementById('updateSuccess').style.display = 'block';
}

// WebSocket para progreso en tiempo real (opcional)
// const ws = new WebSocket('ws://localhost:5000/ws');
// ws.onmessage = (event) => {
//     const data = JSON.parse(event.data);
//     document.getElementById('progressText').textContent = data.progress + '%';
//     document.getElementById('statusText').textContent = data.status;
// };
