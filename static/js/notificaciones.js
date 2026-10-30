// Sistema de notificaciones en tiempo real para Carta Virtual Cuba

class NotificacionesRealtime {
    constructor(options = {}) {
        this.options = {
            pollingInterval: 30000, // 30 segundos
            playSound: true,
            showDesktopNotifications: false,
            ...options
        };

        this.sound = new Audio('/static/sounds/notification.mp3');
        this.lastNotificationId = null;
        this.isPolling = false;
        this.pollingTimer = null;

        // Verificar si el navegador soporta notificaciones
        this.desktopNotificationsSupported = ('Notification' in window);
        if (this.desktopNotificationsSupported) {
            this.requestPermission();
        }
    }

    // Solicitar permiso para notificaciones de escritorio
    requestPermission() {
        if (this.desktopNotificationsSupported && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                console.log('Permiso de notificaciones:', permission);
            });
        }
    }

    // Iniciar polling para nuevas notificaciones
    startPolling() {
        if (this.isPolling) return;

        this.isPolling = true;
        this.poll();

        this.pollingTimer = setInterval(() => {
            this.poll();
        }, this.options.pollingInterval);

        console.log('Polling de notificaciones iniciado');
    }

    // Detener polling
    stopPolling() {
        if (this.pollingTimer) {
            clearInterval(this.pollingTimer);
            this.pollingTimer = null;
        }
        this.isPolling = false;
        console.log('Polling de notificaciones detenido');
    }

    // Obtener notificaciones del servidor
    async poll() {
        try {
            const response = await fetch('/notificaciones/api/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) throw new Error('Error en la petición');

            const data = await response.json();

            if (data.success && data.notificaciones.length > 0) {
                this.processNotifications(data.notificaciones);
            }

            this.updateBadgeCount(data.total || 0);

        } catch (error) {
            console.error('Error polling notificaciones:', error);
        }
    }

    // Procesar nuevas notificaciones
    processNotifications(notificaciones) {
        // Ordenar por ID para asegurar que procesamos las más nuevas
        notificaciones.sort((a, b) => b.id - a.id);

        // Procesar solo notificaciones nuevas
        const nuevas = notificaciones.filter(n =>
            this.lastNotificationId === null || n.id > this.lastNotificationId
        );

        if (nuevas.length === 0) return;

        // Actualizar última notificación ID
        this.lastNotificationId = notificaciones[0].id;

        // Mostrar cada notificación nueva
        nuevas.reverse().forEach(notif => {
            this.showNotification(notif);
        });
    }

    // Mostrar notificación
    showNotification(notificacion) {
        // Reproducir sonido
        if (this.options.playSound) {
            this.playNotificationSound();
        }

        // Mostrar notificación de escritorio
        if (this.options.showDesktopNotifications &&
            this.desktopNotificationsSupported &&
            Notification.permission === 'granted') {

            this.showDesktopNotification(notificacion);
        }

        // Mostrar notificación en página
        this.showInPageNotification(notificacion);

        // Actualizar contadores en tiempo real
        this.updateRealTimeCounters(notificacion);
    }

    // Mostrar notificación en la página
    showInPageNotification(notificacion) {
        // Crear elemento de notificación
        const notificationEl = document.createElement('div');
        notificationEl.className = 'toast notification-toast';
        notificationEl.setAttribute('role', 'alert');
        notificationEl.setAttribute('aria-live', 'assertive');
        notificationEl.setAttribute('aria-atomic', 'true');
        notificationEl.setAttribute('data-bs-delay', '5000');

        // Icono según tipo
        const icon = this.getNotificationIcon(notificacion.tipo);

        notificationEl.innerHTML = `
            <div class="toast-header">
                <strong class="me-auto">
                    <i class="bi ${icon} me-2"></i>
                    ${notificacion.titulo}
                </strong>
                <small class="text-muted">${notificacion.creada_en}</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${notificacion.mensaje}
                ${notificacion.url ?
                    `<a href="${notificacion.url}" class="btn btn-sm btn-primary mt-2">Ver</a>` :
                    ''
                }
            </div>
        `;

        // Agregar al contenedor
        const container = document.getElementById('notification-container');
        if (!container) {
            // Crear contenedor si no existe
            const newContainer = document.createElement('div');
            newContainer.id = 'notification-container';
            newContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            newContainer.style.zIndex = '1060';
            document.body.appendChild(newContainer);
        }

        document.getElementById('notification-container').appendChild(notificationEl);

        // Inicializar toast de Bootstrap
        const toast = new bootstrap.Toast(notificationEl);
        toast.show();

        // Eliminar del DOM después de ocultar
        notificationEl.addEventListener('hidden.bs.toast', () => {
            notificationEl.remove();
        });
    }

    // Mostrar notificación de escritorio
    showDesktopNotification(notificacion) {
        const notification = new Notification(notificacion.titulo, {
            body: notificacion.mensaje,
            icon: '/static/images/logo.png',
            badge: '/static/images/logo.png',
            tag: `notif-${notificacion.id}`,
            renotify: true,
            requireInteraction: false,
            silent: false,
        });

        notification.onclick = () => {
            window.focus();
            if (notificacion.url) {
                window.location.href = notificacion.url;
            }
            notification.close();
        };

        // Auto cerrar después de 5 segundos
        setTimeout(() => notification.close(), 5000);
    }

    // Reproducir sonido de notificación
    playNotificationSound() {
        this.sound.currentTime = 0;
        this.sound.play().catch(e => console.log('No se pudo reproducir sonido:', e));
    }

    // Actualizar contador de notificaciones
    updateBadgeCount(count) {
        // Actualizar badge en el navbar
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }

        // Actualizar título de la página
        if (count > 0) {
            document.title = `(${count}) Carta Virtual Cuba`;
        } else {
            document.title = 'Carta Virtual Cuba';
        }
    }

    // Actualizar contadores en tiempo real
    updateRealTimeCounters(notificacion) {
        // Incrementar contador de pedidos si es un pedido nuevo
        if (notificacion.tipo === 'pedido_nuevo') {
            const pedidosBadge = document.querySelector('.pedidos-badge');
            if (pedidosBadge) {
                const current = parseInt(pedidosBadge.textContent) || 0;
                pedidosBadge.textContent = current + 1;
                pedidosBadge.style.display = 'inline-block';
            }
        }

        // Incrementar contador de reservas si es una reserva nueva
        if (notificacion.tipo === 'reserva_nueva') {
            const reservasBadge = document.querySelector('.reservas-badge');
            if (reservasBadge) {
                const current = parseInt(reservasBadge.textContent) || 0;
                reservasBadge.textContent = current + 1;
                reservasBadge.style.display = 'inline-block';
            }
        }
    }

    // Obtener icono según tipo de notificación
    getNotificationIcon(tipo) {
        const icons = {
            'reserva_nueva': 'bi-calendar-plus',
            'reserva_confirmada': 'bi-calendar-check',
            'reserva_cancelada': 'bi-calendar-x',
            'pedido_nuevo': 'bi-cart-plus',
            'pedido_listo': 'bi-cart-check',
            'sistema': 'bi-info-circle',
        };
        return icons[tipo] || 'bi-bell';
    }

    // Marcar notificación como leída
    async marcarComoLeida(notificacionId) {
        try {
            const response = await fetch(`/notificaciones/${notificacionId}/marcar-leida/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const data = await response.json();
                return data.success;
            }
        } catch (error) {
            console.error('Error marcando notificación como leída:', error);
        }
        return false;
    }

    // Marcar todas como leídas
    async marcarTodasLeidas() {
        try {
            const response = await fetch('/notificaciones/marcar-todas-leidas/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.updateBadgeCount(0);
                    return true;
                }
            }
        } catch (error) {
            console.error('Error marcando todas como leídas:', error);
        }
        return false;
    }
}

// Helper para obtener CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Inicializar sistema de notificaciones cuando la página cargue
document.addEventListener('DOMContentLoaded', function() {
    // Solo inicializar si el usuario está autenticado
    if (document.body.classList.contains('user-authenticated')) {
        const notificaciones = new NotificacionesRealtime({
            pollingInterval: 30000, // 30 segundos
            playSound: true,
            showDesktopNotifications: false // Cambiar a true si quieres notificaciones de escritorio
        });

        // Iniciar polling
        notificaciones.startPolling();

        // Guardar instancia en window para acceso global
        window.NotificacionesRealtime = notificaciones;

        // Detener polling cuando la pestaña no está activa
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                notificaciones.stopPolling();
            } else {
                notificaciones.startPolling();
            }
        });

        // Actualizar contador inicial
        notificaciones.poll();
    }
});
