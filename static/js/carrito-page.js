/**
 * CARTA VIRTUAL CUBA - Página de carrito
 */

let carrito = null;

document.addEventListener('DOMContentLoaded', function() {
    carrito = window.getCarrito(restauranteUUID);
    renderizarPaginaCarrito();

    // Escuchar cambios en el carrito (desde otra pestaña)
    window.addEventListener('storage', (e) => {
        if (e.key === carrito.storageKey) {
            carrito.items = JSON.parse(e.newValue || '{}');
            renderizarPaginaCarrito();
        }
    });

    // Escuchar evento personalizado
    window.addEventListener('cartUpdated', (e) => {
        if (e.detail.restauranteUUID === restauranteUUID) {
            renderizarPaginaCarrito();
        }
    });
});

function renderizarPaginaCarrito() {
    const items = carrito.itemsList;
    const contenedor = document.getElementById('carritoItems');
    const emptyMsg = document.getElementById('emptyCartMessage');
    const checkoutBtn = document.getElementById('checkoutButton');
    const subtotalSpan = document.getElementById('subtotal');
    const impuestosSpan = document.getElementById('impuestos');
    const totalSpan = document.getElementById('total');

    if (items.length === 0) {
        contenedor.innerHTML = '';
        emptyMsg.style.display = 'block';
        checkoutBtn.disabled = true;
        subtotalSpan.textContent = '$0.00';
        impuestosSpan.textContent = '$0.00';
        totalSpan.textContent = '$0.00';
        return;
    }

    emptyMsg.style.display = 'none';
    checkoutBtn.disabled = false;

    let html = '';
    let subtotal = 0;

    items.forEach(item => {
        const itemSubtotal = item.precio * item.cantidad;
        subtotal += itemSubtotal;
        html += `
            <div class="cart-item mb-3 pb-3 border-bottom" data-plato-id="${item.id}">
                <div class="d-flex">
                    <div class="flex-shrink-0">
                        <img src="${item.imagen || '/static/images/placeholder.png'}"
                             alt="${item.nombre}" class="img-thumbnail" style="width: 80px; height: 80px; object-fit: cover;">
                    </div>
                    <div class="flex-grow-1 ms-3">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h6 class="mb-1">${item.nombre}</h6>
                                <p class="text-muted mb-0">$${item.precio} c/u</p>
                            </div>
                            <div class="text-end">
                                <h5 class="mb-1">$${itemSubtotal.toFixed(2)}</h5>
                                <div class="input-group input-group-sm" style="width: 120px;">
                                    <button class="btn btn-outline-secondary" onclick="actualizarCantidad('${item.id}', ${item.cantidad - 1})">
                                        <i class="fas fa-minus"></i>
                                    </button>
                                    <input type="number" class="form-control text-center"
                                           value="${item.cantidad}" min="1"
                                           onchange="actualizarCantidad('${item.id}', parseInt(this.value))">
                                    <button class="btn btn-outline-secondary" onclick="actualizarCantidad('${item.id}', ${item.cantidad + 1})">
                                        <i class="fas fa-plus"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="text-end mt-2">
                            <button class="btn btn-sm btn-outline-danger" onclick="eliminarDelCarrito('${item.id}')">
                                <i class="fas fa-trash me-1"></i> Eliminar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });

    contenedor.innerHTML = html;

    const impuestos = subtotal * 0.10;
    const total = subtotal + impuestos;

    subtotalSpan.textContent = `$${subtotal.toFixed(2)}`;
    impuestosSpan.textContent = `$${impuestos.toFixed(2)}`;
    totalSpan.textContent = `$${total.toFixed(2)}`;
}

window.actualizarCantidad = function(platoId, cantidad) {
    carrito.actualizarCantidad(platoId, cantidad);
    renderizarPaginaCarrito();
};

window.eliminarDelCarrito = function(platoId) {
    carrito.eliminar(platoId);
    renderizarPaginaCarrito();
};

window.realizarCheckout = function() {
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
        telefono_cliente: document.getElementById('customerPhone').value,
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
