/**
 * DentalCare Pro — JavaScript principal
 * Micro-interacciones y mejoras de UX.
 */

'use strict';

// =========================================================================
// AUTO-DISMISS MENSAJES FLASH
// =========================================================================
(function autoDissmissMessages() {
    const DISMISS_DELAY_MS = 5000; // 5 segundos

    document.querySelectorAll('.message').forEach(function(msg) {
        setTimeout(function() {
            msg.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(20px)';
            setTimeout(function() { msg.remove(); }, 400);
        }, DISMISS_DELAY_MS);
    });
}());

// =========================================================================
// CONFIRMACIÓN ANTES DE CANCELAR CITA
// =========================================================================
document.querySelectorAll('[data-confirm]').forEach(function(el) {
    el.addEventListener('click', function(e) {
        if (!confirm(el.getAttribute('data-confirm'))) {
            e.preventDefault();
        }
    });
});

// =========================================================================
// PREVENIR DOBLE SUBMIT EN FORMULARIOS
// =========================================================================
document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
        // Obtener el botón que inició el submit y duplicar su valor en un input oculto
        // para que no se pierda al deshabilitarlo
        const submitter = e.submitter;
        if (submitter && submitter.name) {
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = submitter.name;
            hiddenInput.value = submitter.value;
            form.appendChild(hiddenInput);
        }

        const submitBtns = form.querySelectorAll('[type="submit"]');
        submitBtns.forEach(function(btn) {
            // Deshabilitar en el siguiente ciclo del event loop para permitir que el 
            // navegador procese el submit con el valor correcto primero
            setTimeout(function() {
                btn.disabled = true;
                btn.style.opacity = '0.7';
            }, 0);
        });
    });
});

// =========================================================================
// VALIDACIÓN DE TAMAÑO DE ARCHIVO (COMPROBANTE)
// =========================================================================
const fileInput = document.querySelector('input[type="file"]');
if (fileInput) {
    fileInput.addEventListener('change', function() {
        const MAX_SIZE_MB = 5;
        const file = this.files[0];
        if (file && file.size > MAX_SIZE_MB * 1024 * 1024) {
            alert('El archivo supera el tamaño máximo permitido (' + MAX_SIZE_MB + ' MB).');
            this.value = '';
        }
    });
}

// =========================================================================
// RESALTAR FILA DE TABLA AL HACER CLICK
// =========================================================================
document.querySelectorAll('.table tbody tr').forEach(function(row) {
    row.addEventListener('click', function() {
        // Buscar el primer enlace o botón y hacerle click
        const link = row.querySelector('a');
        if (link) { link.click(); }
    });
    row.style.cursor = row.querySelector('a') ? 'pointer' : 'default';
});
