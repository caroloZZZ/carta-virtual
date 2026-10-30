/*
   UTILIDADES GENERALES DEL SISTEMA
*/

class AdminUtils {

    // Mostrar alerta temporal
    static showAlert(message, type = 'success', duration = 5000) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
            <button class="alert-close"><i class="fas fa-times"></i></button>
        `;

        document.querySelector('.content-wrapper').prepend(alert);

        // Cerrar alerta
        alert.querySelector('.alert-close').addEventListener('click', () => {
            alert.remove();
        });

        // Auto cerrar
        if (duration > 0) {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, duration);
        }
    }

    // Formatear moneda
    static formatCurrency(amount) {
        return new Intl.NumberFormat('es-CU', {
            style: 'currency',
            currency: 'CUP',
            minimumFractionDigits: 2
        }).format(amount);
    }

    // Formatear fecha
    static formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // Validar formulario
    static validateForm(form) {
        const inputs = form.querySelectorAll('[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });

        return isValid;
    }

    // Cargar imagen y crear preview
    static previewImage(input, previewId) {
        const preview = document.getElementById(previewId);
        const file = input.files[0];

        if (file) {
            const reader = new FileReader();

            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }

            reader.readAsDataURL(file);
        }
    }

    // Confirmar acción
    static confirmAction(message) {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal show';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="card">
                        <div class="card-header">
                            <h5>Confirmar acción</h5>
                            <button class="btn-close"></button>
                        </div>
                        <div class="card-body">
                            <p>${message}</p>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-secondary cancel">Cancelar</button>
                            <button class="btn btn-danger confirm">Confirmar</button>
                        </div>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            modal.querySelector('.btn-close').addEventListener('click', () => {
                modal.remove();
                resolve(false);
            });

            modal.querySelector('.cancel').addEventListener('click', () => {
                modal.remove();
                resolve(false);
            });

            modal.querySelector('.confirm').addEventListener('click', () => {
                modal.remove();
                resolve(true);
            });
        });
    }

    // Copiar al portapapeles
    static copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showAlert('Copiado al portapapeles', 'success');
        }).catch(() => {
            this.showAlert('Error al copiar', 'danger');
        });
    }
}

// Exportar para uso global
window.AdminUtils = AdminUtils;
