/*
   FUNCIONALIDADES PRINCIPALES DEL PANEL ADMINISTRATIVO
*/

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    initSidebar();
    initNotifications();
    initModals();
    initForms();
    initTables();
    initCharts();

    // Verificar sesión periódicamente
    checkSession();

    // Cargar estadísticas iniciales
    loadDashboardStats();
});

// SIDEBAR TOGGLE
function initSidebar() {
    const toggleBtn = document.querySelector('.toggle-sidebar');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('expanded');

            // Guardar preferencia en localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });

        // Cargar preferencia guardada
        const savedState = localStorage.getItem('sidebarCollapsed');
        if (savedState === 'true') {
            sidebar.classList.add('collapsed');
            mainContent.classList.add('expanded');
        }
    }

    // Sidebar responsive en móviles
    const sidebarToggleMobile = document.querySelector('.sidebar-toggle-mobile');
    if (sidebarToggleMobile) {
        sidebarToggleMobile.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });
    }
}

// NOTIFICACIONES EN TIEMPO REAL
function initNotifications() {
    const notificationBtn = document.querySelector('.notification-btn');
    const notificationDropdown = document.querySelector('.notification-dropdown-content');

    if (notificationBtn && notificationDropdown) {
        notificationBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            notificationDropdown.classList.toggle('show');

            // Marcar notificaciones como leídas
            markNotificationsAsRead();
        });

        // Cerrar al hacer clic fuera
        document.addEventListener('click', () => {
            notificationDropdown.classList.remove('show');
        });
    }

    // Polling para nuevas notificaciones
    setInterval(checkNewNotifications, 30000); // Cada 30 segundos
}

async function checkNewNotifications() {
    try {
        const response = await fetch('/api/notifications/unread-count/');
        const data = await response.json();

        const badge = document.querySelector('.notification-badge');
        if (badge) {
            if (data.count > 0) {
                badge.textContent = data.count;
                badge.style.display = 'flex';

                // Notificación push
                if (data.count > parseInt(badge.textContent || 0)) {
                    showPushNotification('Nuevo pedido recibido');
                }
            } else {
                badge.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error checking notifications:', error);
    }
}

function markNotificationsAsRead() {
    fetch('/api/notifications/mark-as-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
        }
    });
}

function showPushNotification(message) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Carta Virtual Cuba', {
            body: message,
            icon: '/static/images/logo.png'
        });
    }
}

// MODALES DINÁMICOS
function initModals() {
    // Abrir modal
    document.querySelectorAll('[data-modal-target]').forEach(button => {
        button.addEventListener('click', () => {
            const modalId = button.getAttribute('data-modal-target');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('show');
            }
        });
    });

    // Cerrar modal
    document.querySelectorAll('.modal .btn-close, .modal .btn-cancel').forEach(button => {
        button.addEventListener('click', () => {
            const modal = button.closest('.modal');
            if (modal) {
                modal.classList.remove('show');
            }
        });
    });

    // Cerrar al hacer clic fuera
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        });
    });
}

// FORMULARIOS AJAX
function initForms() {
    // Validación en tiempo real
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            if (!AdminUtils.validateForm(form)) {
                AdminUtils.showAlert('Por favor complete todos los campos requeridos', 'danger');
                return;
            }

            const submitBtn = form.querySelector('[type="submit"]');
            const originalText = submitBtn.innerHTML;

            // Mostrar loading
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
            submitBtn.disabled = true;

            try {
                const formData = new FormData(form);
                const url = form.getAttribute('action') || window.location.href;
                const method = form.getAttribute('method') || 'POST';

                const response = await fetch(url, {
                    method: method,
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                    }
                });

                const data = await response.json();

                if (data.success) {
                    AdminUtils.showAlert(data.message || 'Operación exitosa', 'success');

                    // Redireccionar si hay URL
                    if (data.redirect) {
                        setTimeout(() => {
                            window.location.href = data.redirect;
                        }, 1500);
                    }

                    // Recargar si es necesario
                    if (data.reload) {
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    }

                    // Cerrar modal si está abierto
                    const modal = form.closest('.modal');
                    if (modal) {
                        setTimeout(() => {
                            modal.classList.remove('show');
                        }, 1500);
                    }
                } else {
                    AdminUtils.showAlert(data.message || 'Error en la operación', 'danger');
                }
            } catch (error) {
                AdminUtils.showAlert('Error de conexión', 'danger');
                console.error('Form submission error:', error);
            } finally {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    });
}

// TABLAS INTERACTIVAS
function initTables() {
    // Ordenamiento
    document.querySelectorAll('.table th[data-sort]').forEach(th => {
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
            const table = th.closest('table');
            const column = th.getAttribute('data-sort');
            const currentOrder = th.getAttribute('data-order') || 'asc';
            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';

            th.setAttribute('data-order', newOrder);

            // Ordenar tabla
            sortTable(table, column, newOrder);

            // Actualizar iconos
            table.querySelectorAll('th i.fa-sort').forEach(icon => {
                icon.className = 'fas fa-sort';
            });

            const icon = th.querySelector('i');
            if (icon) {
                icon.className = `fas fa-sort-${newOrder === 'asc' ? 'up' : 'down'}`;
            }
        });
    });

    // Búsqueda
    const searchInput = document.querySelector('.table-search');
    if (searchInput) {
        searchInput.addEventListener('input', debounce((e) => {
            const searchTerm = e.target.value.toLowerCase();
            const table = document.querySelector('.table');

            if (table) {
                const rows = table.querySelectorAll('tbody tr');

                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        }, 300));
    }
}

function sortTable(table, column, order) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aValue = a.querySelector(`td:nth-child(${column})`).textContent;
        const bValue = b.querySelector(`td:nth-child(${column})`).textContent;

        // Intentar convertir a número si es posible
        const aNum = parseFloat(aValue.replace(/[^\d.-]/g, ''));
        const bNum = parseFloat(bValue.replace(/[^\d.-]/g, ''));

        if (!isNaN(aNum) && !isNaN(bNum)) {
            return order === 'asc' ? aNum - bNum : bNum - aNum;
        }

        // Ordenar como texto
        return order === 'asc'
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
    });

    // Reordenar filas
    rows.forEach(row => tbody.appendChild(row));
}

// GRÁFICOS CON CHART.JS
function initCharts() {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js no está cargado');
        return;
    }

    // Gráfico de ventas
    const salesChart = document.getElementById('salesChart');
    if (salesChart) {
        const ctx = salesChart.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
                datasets: [{
                    label: 'Ventas',
                    data: [12000, 19000, 15000, 25000, 22000, 30000],
                    borderColor: '#4361ee',
                    backgroundColor: 'rgba(67, 97, 238, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Gráfico de categorías
    const categoriesChart = document.getElementById('categoriesChart');
    if (categoriesChart) {
        const ctx = categoriesChart.getContext('2d');
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Entradas', 'Platos Fuertes', 'Postres', 'Bebidas'],
                datasets: [{
                    data: [30, 40, 15, 15],
                    backgroundColor: [
                        '#4361ee',
                        '#7209b7',
                        '#4cc9f0',
                        '#f72585'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// VERIFICAR SESIÓN
function checkSession() {
    // Verificar cada 5 minutos
    setInterval(async () => {
        try {
            const response = await fetch('/api/check-session/');
            if (response.status === 401) {
                AdminUtils.showAlert('Tu sesión ha expirado', 'warning');
                setTimeout(() => {
                    window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
                }, 2000);
            }
        } catch (error) {
            // Silencioso en error de red
        }
    }, 300000);
}

// CARGAR ESTADÍSTICAS DEL DASHBOARD
async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats/');
        const data = await response.json();

        // Actualizar contadores
        document.querySelectorAll('[data-stat]').forEach(element => {
            const stat = element.getAttribute('data-stat');
            if (data[stat] !== undefined) {
                element.textContent = data[stat];

                // Animar números
                if (element.classList.contains('stats-number')) {
                    animateCounter(element, data[stat]);
                }
            }
        });
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function animateCounter(element, target) {
    const current = parseInt(element.textContent.replace(/\D/g, '')) || 0;
    const increment = target > current ? 1 : -1;
    let currentValue = current;

    const interval = setInterval(() => {
        currentValue += increment;
        element.textContent = currentValue.toLocaleString();

        if (currentValue === target) {
            clearInterval(interval);
        }
    }, 20);
}

// HELPER FUNCTIONS
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Exportar funciones globales
window.initCharts = initCharts;
window.loadDashboardStats = loadDashboardStats;
