/**
 * CARRITO.JS - Funcionalidades del carrito de compras
 * Versión mejorada con clases y eventos
 */

class Carrito {
    constructor(restauranteUUID) {
        this.restauranteUUID = restauranteUUID;
        this.storageKey = `cart_${restauranteUUID}`;
        this.items = this.load();
        this.initEventListeners();
    }

    load() {
        try {
            const stored = localStorage.getItem(this.storageKey);
            return stored ? JSON.parse(stored) : { items: {} };
        } catch (e) {
            console.error('Error loading cart:', e);
            return { items: {} };
        }
    }

    save() {
        localStorage.setItem(this.storageKey, JSON.stringify(this.items));
        this.dispatchChange();
    }

    clear() {
        this.items = { items: {} };
        this.save();
    }

    addItem(platoId, nombre, precio, cantidad = 1, imagen_url = '') {
        if (this.items.items[platoId]) {
            this.items.items[platoId].cantidad += cantidad;
        } else {
            this.items.items[platoId] = {
                nombre: nombre,
                precio: precio,
                cantidad: cantidad,
                imagen_url: imagen_url
            };
        }
        this.save();
    }

    updateItem(platoId, cantidad) {
        if (cantidad <= 0) {
            this.removeItem(platoId);
        } else if (this.items.items[platoId]) {
            this.items.items[platoId].cantidad = cantidad;
            this.save();
        }
    }

    removeItem(platoId) {
        delete this.items.items[platoId];
        this.save();
    }

    getItems() {
        return this.items.items;
    }

    getItemCount() {
        return Object.values(this.items.items).reduce((acc, item) => acc + item.cantidad, 0);
    }

    getTotal() {
        return Object.values(this.items.items).reduce((acc, item) => acc + (item.precio * item.cantidad), 0);
    }

    dispatchChange() {
        window.dispatchEvent(new CustomEvent('cartUpdated', {
            detail: { restauranteUUID: this.restauranteUUID }
        }));
    }

    initEventListeners() {
        window.addEventListener('storage', (e) => {
            if (e.key === this.storageKey) {
                this.items = JSON.parse(e.newValue || '{"items":{}}');
                this.dispatchChange();
            }
        });
    }
}

// Instancia global (se inicializará después)
let carrito = null;

// Funciones de inicialización y acceso global
function initCart(restauranteUUID) {
    carrito = new Carrito(restauranteUUID);
    updateUI();
    window.addEventListener('cartUpdated', () => updateUI());
}

function updateUI() {
    if (!carrito) return;
    const badge = document.getElementById('cartCount') || document.getElementById('cartBadge');
    if (badge) {
        const count = carrito.getItemCount();
        badge.textContent = count;
        badge.style.display = count > 0 ? 'flex' : 'none';
    }
    // Actualizar carrito flotante si existe
    const cartSidebar = document.getElementById('cartSidebar');
    if (cartSidebar && cartSidebar.classList.contains('open')) {
        renderFloatingCart();
    }
}

// Funciones para usar desde las plantillas
function addToCart(platoId, nombre, precio, cantidad = 1, imagen_url = '') {
    if (!carrito) throw new Error('Carrito no inicializado. Llama a initCart primero.');
    carrito.addItem(platoId, nombre, precio, cantidad, imagen_url);
    // Feedback visual
    const btn = event?.target.closest('button');
    if (btn) {
        const original = btn.innerHTML;
        btn.innerHTML = '<i class="bi bi-check"></i>';
        btn.classList.add('added');
        setTimeout(() => {
            btn.innerHTML = original;
            btn.classList.remove('added');
        }, 500);
    }
}

function updateCartItem(platoId, cantidad) {
    if (!carrito) return;
    carrito.updateItem(platoId, cantidad);
}

function removeFromCart(platoId) {
    if (!carrito) return;
    carrito.removeItem(platoId);
}

function getCart() {
    return carrito ? {
        items: carrito.getItems(),
        count: carrito.getItemCount(),
        total: carrito.getTotal()
    } : { items: {}, count: 0, total: 0 };
}

// Renderizar el carrito flotante
function renderFloatingCart() {
    const cartItemsDiv = document.getElementById('cartItems');
    const cartTotalSpan = document.getElementById('cartTotal');
    const emptyCart = document.getElementById('emptyCart');
    const customerData = document.getElementById('customerData');

    if (!cartItemsDiv || !cartTotalSpan) return;

    const items = carrito.getItems();
    const total = carrito.getTotal();

    if (Object.keys(items).length === 0) {
        cartItemsDiv.innerHTML = emptyCart ? emptyCart.outerHTML : '<div class="text-center text-muted py-4">Carrito vacío</div>';
        if (customerData) customerData.style.display = 'none';
        cartTotalSpan.textContent = '$0.00';
        return;
    }

    if (customerData) customerData.style.display = 'block';

    let html = '';
    for (const [id, item] of Object.entries(items)) {
        const subtotal = item.precio * item.cantidad;
        html += `
        <div class="cart-item" data-id="${id}">
            <div class="cart-item-info">
                <h6>${item.nombre}</h6>
                <small>$${item.precio} x ${item.cantidad}</small>
            </div>
            <div class="cart-item-actions">
                <button onclick="updateCartItem('${id}', ${item.cantidad - 1})">−</button>
                <span>${item.cantidad}</span>
                <button onclick="updateCartItem('${id}', ${item.cantidad + 1})">+</button>
                <button class="btn-remove" onclick="removeFromCart('${id}')"><i class="bi bi-trash"></i></button>
            </div>
        </div>
        `;
    }
    cartItemsDiv.innerHTML = html;
    cartTotalSpan.textContent = `$${total.toFixed(2)}`;
}

// Exportar al ámbito global
window.Carrito = Carrito;
window.initCart = initCart;
window.addToCart = addToCart;
window.updateCartItem = updateCartItem;
window.removeFromCart = removeFromCart;
window.getCart = getCart;
window.renderFloatingCart = renderFloatingCart;
