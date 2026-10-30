/**
 * DASHBOARD JS - Carta Virtual Cuba
 * Funcionalidades principales del panel administrativo
 */

document.addEventListener('DOMContentLoaded', function() {
    // ============================================
    // 1. TOGGLE SIDEBAR
    // ============================================
    const menuToggle = document.getElementById('menu-toggle');
    const wrapper = document.getElementById('wrapper');

    if (menuToggle) {
        menuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            wrapper.classList.toggle('active');

            // Cambiar ícono
            const icon = this.querySelector('i');
            if (wrapper.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
                localStorage.setItem('sidebarState', 'open');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
                localStorage.setItem('sidebarState', 'closed');
            }
        });
    }

    // Restaurar estado del sidebar
    const sidebarState = localStorage.getItem('sidebarState');
    if (sidebarState === 'open' && window.innerWidth > 1024) {
        wrapper.classList.add('active');
        if (menuToggle) {
            const icon = menuToggle.querySelector('i');
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-times');
        }
    }

    // ============================================
    // 2. AUTO-DISMISS ALERTS
    // ============================================
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert && alert.classList.contains('show')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });

    // ============================================
    // 3. CONFIRMACIÓN PARA ELIMINAR
    // ============================================
    const deleteButtons = document.querySelectorAll('.btn-delete, [data-action="delete"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('¿Estás seguro de que quieres eliminar este elemento?\nEsta acción no se puede deshacer.')) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        });
    });

    // ============================================
    // 4. PREVIEW DE IMÁGENES EN FORMULARIOS
    // ============================================
    const imageInputs = document.querySelectorAll('input[type="file"][data-preview]');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const previewId = this.getAttribute('data-preview');
            const previewElement = document.getElementById(previewId);

            if (this.files && this.files[0]) {
                const reader = new FileReader();

                reader.onload = function(e) {
                    if (previewElement) {
                        previewElement.src = e.target.result;
                        previewElement.style.display = 'block';
                    }
                }

                reader.readAsDataURL(this.files[0]);
            }
        });
    });

    // ============================================
    // 5. VALIDACIÓN DE FORMULARIOS
    // ============================================
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('is-invalid');

                    // Crear mensaje de error si no existe
                    if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('invalid-feedback')) {
                        const errorDiv = document.createElement('div');
                        errorDiv.className = 'invalid-feedback';
                        errorDiv.textContent = 'Este campo es obligatorio';
                        field.parentNode.appendChild(errorDiv);
                    }
                } else {
                    field.classList.remove('is-invalid');
                    field.classList.add('is-valid');
                }
            });

            if (!isValid) {
                e.preventDefault();

                // Mostrar alerta general
                if (!form.querySelector('.alert-danger')) {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-danger mt-3';
                    alertDiv.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i> Por favor, completa todos los campos obligatorios.';
                    form.prepend(alertDiv);
                }
            }
        });
    });

    // ============================================
    // 6. CONTADOR DE CARACTERES
    // ============================================
    const textareas = document.querySelectorAll('textarea[data-maxlength]');
    textareas.forEach(function(textarea) {
        const maxLength = parseInt(textarea.getAttribute('data-maxlength'));
        const counterId = textarea.id + '-counter';

        // Crear contador si no existe
        if (!document.getElementById(counterId)) {
            const counter = document.createElement('small');
            counter.id = counterId;
            counter.className = 'form-text text-end text-muted';
            counter.textContent = '0/' + maxLength;
            textarea.parentNode.appendChild(counter);
        }

        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            const counter = document.getElementById(counterId);

            if (counter) {
                counter.textContent = currentLength + '/' + maxLength;

                if (currentLength > maxLength) {
                    counter.classList.add('text-danger');
                    this.classList.add('is-invalid');
                } else {
                    counter.classList.remove('text-danger');
                    this.classList.remove('is-invalid');
                }
            }
        });
    });

    // ============================================
    // 7. TOOLTIPS
    // ============================================
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // ============================================
    // 8. COPIAR AL PORTAPAPELES
    // ============================================
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-copy');
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                // Crear área de texto temporal
                const tempTextArea = document.createElement('textarea');
                tempTextArea.value = targetElement.textContent || targetElement.value;
                document.body.appendChild(tempTextArea);

                // Seleccionar y copiar
                tempTextArea.select();
                document.execCommand('copy');
                document.body.removeChild(tempTextArea);

                // Mostrar feedback
                const originalHtml = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check me-1"></i> Copiado!';
                this.classList.add('btn-success');

                setTimeout(() => {
                    this.innerHTML = originalHtml;
                    this.classList.remove('btn-success');
                }, 2000);
            }
        });
    });

    // ============================================
    // 9. ACTUALIZACIÓN EN TIEMPO REAL
    // ============================================
    function updateStats() {
        // Solo si estamos en el dashboard
        if (window.location.pathname.includes('/dashboard') && !window.location.pathname.includes('/dashboard/')) {
            fetch('/api/stats/')
                .then(response => response.json())
                .then(data => {
                    // Actualizar contadores
                    if (data.pedidos_pendientes !== undefined) {
                        const badge = document.querySelector('.badge-pedidos-pendientes');
                        if (badge) {
                            badge.textContent = data.pedidos_pendientes;
                            badge.classList.toggle('d-none', data.pedidos_pendientes === 0);
                        }
                    }
                })
                .catch(error => console.error('Error actualizando estadísticas:', error));
        }
    }

    // Actualizar cada 30 segundos
    setInterval(updateStats, 30000);

    // ============================================
    // 10. MANEJO DE MODALES
    // ============================================
    const modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        modal.addEventListener('shown.bs.modal', function() {
            // Enfocar primer campo
            const input = this.querySelector('input, textarea, select');
            if (input) {
                setTimeout(() => input.focus(), 100);
            }
        });
    });

    // ============================================
    // 11. FILTRADO DE TABLAS
    // ============================================
    const tableFilters = document.querySelectorAll('.table-filter');
    tableFilters.forEach(function(filter) {
        filter.addEventListener('input', function() {
            const tableId = this.getAttribute('data-table');
            const columnIndex = parseInt(this.getAttribute('data-column'));
            const table = document.getElementById(tableId);

            if (table) {
                const searchTerm = this.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');

                rows.forEach(function(row) {
                    const cell = row.children[columnIndex];
                    const text = cell.textContent.toLowerCase();

                    if (text.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
        });
    });

    // ============================================
    // 12. ORDENACIÓN DE TABLAS
    // ============================================
    const sortableHeaders = document.querySelectorAll('th[data-sortable]');
    sortableHeaders.forEach(function(header) {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const tableId = this.closest('table').id;
            const columnIndex = Array.from(this.parentNode.children).indexOf(this);
            const table = document.getElementById(tableId);

            if (table) {
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const isAscending = !this.classList.contains('sort-asc');

                // Remover clases de ordenación de todos los headers
                table.querySelectorAll('th[data-sortable]').forEach(h => {
                    h.classList.remove('sort-asc', 'sort-desc');
                });

                // Añadir clase al header actual
                this.classList.add(isAscending ? 'sort-asc' : 'sort-desc');

                // Ordenar filas
                rows.sort(function(a, b) {
                    const aText = a.children[columnIndex].textContent.trim();
                    const bText = b.children[columnIndex].textContent.trim();

                    // Intentar convertir a número si es posible
                    const aNum = parseFloat(aText.replace(/[^0-9.-]+/g, ''));
                    const bNum = parseFloat(bText.replace(/[^0-9.-]+/g, ''));

                    let comparison = 0;
                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        comparison = aNum - bNum;
                    } else {
                        comparison = aText.localeCompare(bText);
                    }

                    return isAscending ? comparison : -comparison;
                });

                // Reinsertar filas ordenadas
                rows.forEach(function(row) {
                    tbody.appendChild(row);
                });
            }
        });
    });

    // ============================================
    // 13. EXPORTACIÓN DE DATOS
    // ============================================
    const exportButtons = document.querySelectorAll('[data-export]');
    exportButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const format = this.getAttribute('data-export');
            const tableId = this.getAttribute('data-table');
            const table = document.getElementById(tableId);

            if (table && format === 'csv') {
                exportTableToCSV(table, 'datos.csv');
            }
        });
    });

    // Función para exportar a CSV
    function exportTableToCSV(table, filename) {
        const rows = table.querySelectorAll('tr');
        const csv = [];

        rows.forEach(function(row) {
            const rowData = [];
            const cells = row.querySelectorAll('th, td');

            cells.forEach(function(cell) {
                // Excluir columnas de acciones
                if (!cell.closest('.actions-column')) {
                    let text = cell.textContent.trim();
                    // Escapar comillas
                    text = text.replace(/"/g, '""');
                    // Si contiene comas, rodear con comillas
                    if (text.includes(',')) {
                        text = '"' + text + '"';
                    }
                    rowData.push(text);
                }
            });

            csv.push(rowData.join(','));
        });

        const csvContent = csv.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');

        if (navigator.msSaveBlob) {
            // Para IE
            navigator.msSaveBlob(blob, filename);
        } else {
            link.href = URL.createObjectURL(blob);
            link.setAttribute('download', filename);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }

    // ============================================
    // 14. CARGAR DATOS VÍA AJAX
    // ============================================
    window.loadData = function(url, containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Mostrar spinner
        container.innerHTML = '<div class="spinner-container"><div class="spinner"></div></div>';

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (options.callback && typeof options.callback === 'function') {
                    options.callback(data, container);
                }
            })
            .catch(error => {
                console.error('Error cargando datos:', error);
                container.innerHTML = '<div class="alert alert-danger">Error cargando datos</div>';
            });
    };

    // ============================================
    // 15. INICIALIZACIÓN
    // ============================================
    console.log('Dashboard JS cargado correctamente');
});
