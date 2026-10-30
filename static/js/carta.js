/**
 * CARTA VIRTUAL CUBA - Lógica de la carta pública
 */

let carrito = null;

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar carrito
    carrito = window.initCarrito(restauranteUUID);

    // Configurar eventos de categorías
    document.querySelectorAll('.category-chip').forEach(chip => {
        chip.addEventListener('click', function() {
            document.querySelectorAll('.category-chip').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            const catId = this.dataset.categoria;
            document.querySelectorAll('.category-section').forEach(section => {
                section.style.display = 'none';
            });
            document.getElementById(`categoria-${catId}`).style.display = 'block';
        });
    });

    // Actualizar badge inicial
    actualizarBadgeCarrito();

    // Escuchar actualizaciones del carrito
    window.addEventListener('cartUpdated', function(e) {
        if (e.detail.restauranteUUID === restauranteUUID) {
            actualizarBadgeCarrito();
            renderizarCarritoLateral();
        }
    });

    // Si el sidebar está abierto al cargar, renderizarlo
    if (document.getElementById('cartSidebar').classList.contains('open')) {
        renderizarCarritoLateral();
    }
});

// Funciones para cantidad
window.cambiarCantidad = function(platoId, delta) {
    const input = document.getElementById(`qty-${platoId}`);
    let val = parseInt(input.value) + delta;
    if (val < 1) val = 1;
    input.value = val;
};

// Agregar plato al carrito (llamado desde botón)
window.agregarPlato = function(platoId, nombre, precio, imagen) {
    const cantidad = parseInt(document.getElementById(`qty-${platoId}`).value);
    carrito.agregar(platoId, nombre, precio, cantidad, imagen);
    actualizarBadgeCarrito();
    mostrarNotificacion(`${nombre} agregado al carrito`);

    // Feedback en el botón
    const btn = event.target.closest('button');
    const originalHtml = btn.innerHTML;
    btn.innerHTML = '<i class="bi bi-check"></i>';
    btn.classList.add('btn-success');
    setTimeout(() => {
        btn.innerHTML = originalHtml;
        btn.classList.remove('btn-success');
    }, 500);
};

// Toggle del sidebar
window.toggleCart = function() {
    const sidebar = document.getElementById('cartSidebar');
    sidebar.classList.toggle('open');
    if (sidebar.classList.contains('open')) {
        renderizarCarritoLateral();
    }
};

// Renderizar carrito lateral
function renderizarCarritoLateral() {
    const items = carrito.itemsList;
    const cartItemsDiv = document.getElementById('cartItems');
    const cartTotalSpan = document.getElementById('cartTotal');
    const customerDataDiv = document.getElementById('customerData');
    const checkoutBtn = document.getElementById('checkoutBtn');

    if (items.length === 0) {
        cartItemsDiv.innerHTML = `
            <div class="text-center text-muted py-4">
                <i class="fas fa-shopping-cart fa-2x mb-2"></i>
                <p>Tu carrito está vacío</p>
            </div>
        `;
        cartTotalSpan.textContent = '$0.00';
        customerDataDiv.style.display = 'none';
        checkoutBtn.disabled = true;
        return;
    }

    customerDataDiv.style.display = 'block';
    checkoutBtn.disabled = false;

    let html = '';
    items.forEach(item => {
        const subtotal = item.precio * item.cantidad;
        html += `
            <div class="cart-item mb-2 pb-2 border-bottom" data-id="${item.id}">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>${item.nombre}</strong>
                        <br>
                        <small class="text-muted">${item.cantidad} × $${item.precio} = $${subtotal.toFixed(2)}</small>
                    </div>
                    <div>
                        <button class="btn btn-sm btn-outline-danger" onclick="eliminarDelCarrito('${item.id}')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    });

    cartItemsDiv.innerHTML = html;
    cartTotalSpan.textContent = `$${carrito.total.toFixed(2)}`;
}

// Eliminar item
window.eliminarDelCarrito = function(platoId) {
    carrito.eliminar(platoId);
    renderizarCarritoLateral();
    actualizarBadgeCarrito();
};

// Checkout
window.checkout = function() {
    const nombre = document.getElementById('customerName').value.trim();
    if (!nombre) {
        alert('Por favor ingresa tu nombre');
        return;
    }

    const items = carrito.itemsList.map(item => ({
        plato_id: item.id,
        cantidad: item.cantidad,
        precio: item.precio
    }));

    const data = {
        nombre_cliente: nombre,
        telefono_cliente: document.getElementById('customerPhone')?.value || '',
        mesa: document.getElementById('customerTable').value,
        notas: document.getElementById('customerNotes').value,
        items: items
    };

    fetch(`/cliente/${restauranteUUID}/crear-pedido/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            carrito.vaciar();
            window.location.href = data.redirect_url;
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(err => {
        alert('Error de conexión');
        console.error(err);
    });
};

// Notificación (puede usar toast si existe)
function mostrarNotificacion(mensaje) {
    const toastContainer = document.getElementById('toastContainer');
    if (toastContainer) {
        const toast = document.createElement('div');
        toast.className = 'toast align-items-center text-white bg-success border-0';
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${mensaje}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        toastContainer.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        setTimeout(() => toast.remove(), 3000);
    }
}
