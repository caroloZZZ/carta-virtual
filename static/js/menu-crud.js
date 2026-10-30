// =============================================
// MENÚ CRUD JS - GESTIÓN DE CATEGORÍAS Y PLATOS
// =============================================

class MenuCRUD {
    constructor() {
        this.csrfToken = this.getCookie('csrftoken');
        this.currentCategoriaId = null;
        this.currentPlatoId = null;
        this.initialize();
    }

    initialize() {
        this.bindEvents();
        this.loadCategorias();
    }

    getCookie(name) {
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

    // ===== CATEGORÍAS =====
    async loadCategorias() {
        try {
            const response = await fetch('/dashboard/api/categorias/');
            if (response.ok) {
                const categorias = await response.json();
                this.renderCategorias(categorias);
            }
        } catch (error) {
            console.error('Error cargando categorías:', error);
        }
    }

    renderCategorias(categorias) {
        const container = document.getElementById('categorias-container');
        if (!container) return;

        container.innerHTML = categorias.map(categoria => `
            <div class="col-md-4 mb-4" data-categoria-id="${categoria.id}">
                <div class="card dashboard-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h5 class="card-title mb-0">
                                <i class="${categoria.icono || 'fas fa-folder'} me-2"></i>
                                ${categoria.nombre}
                            </h5>
                            <span class="badge ${categoria.activa ? 'bg-success' : 'bg-secondary'}">
                                ${categoria.activa ? 'Activa' : 'Inactiva'}
                            </span>
                        </div>
                        <p class="text-muted small">${categoria.descripcion || 'Sin descripción'}</p>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="text-muted">
                                ${categoria.cantidad_platos || 0} platos
                            </span>
                            <div class="btn-group">
                                <button class="btn btn-sm btn-outline-primary"
                                        onclick="menuCRUD.editarCategoria(${categoria.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger"
                                        onclick="menuCRUD.eliminarCategoria(${categoria.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    abrirModalCategoria() {
        this.currentCategoriaId = null;
        document.getElementById('modalCategoriaLabel').textContent = 'Nueva Categoría';
        document.getElementById('formCategoria').reset();
        document.getElementById('categoriaId').value = '';
        new bootstrap.Modal(document.getElementById('modalCategoria')).show();
    }

    editarCategoria(categoriaId) {
        this.currentCategoriaId = categoriaId;

        // Cargar datos de la categoría
        fetch(`/dashboard/api/categorias/${categoriaId}/`)
            .then(response => response.json())
            .then(categoria => {
                document.getElementById('modalCategoriaLabel').textContent = 'Editar Categoría';
                document.getElementById('categoriaId').value = categoria.id;
                document.getElementById('categoriaNombre').value = categoria.nombre;
                document.getElementById('categoriaDescripcion').value = categoria.descripcion;
                document.getElementById('categoriaOrden').value = categoria.orden;
                document.getElementById('categoriaIcono').value = categoria.icono || '';
                document.getElementById('categoriaActiva').checked = categoria.activa;

                new bootstrap.Modal(document.getElementById('modalCategoria')).show();
            })
            .catch(error => {
                console.error('Error cargando categoría:', error);
                this.showNotification('danger', 'Error al cargar categoría');
            });
    }

    async guardarCategoria(event) {
        event.preventDefault();

        const formData = new FormData(event.target);

        try {
            const url = this.currentCategoriaId
                ? `/dashboard/api/categorias/${this.currentCategoriaId}/`
                : '/dashboard/api/categorias/';

            const method = this.currentCategoriaId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'X-CSRFToken': this.csrfToken
                },
                body: formData
            });

            if (response.ok) {
                this.showNotification('success',
                    this.currentCategoriaId
                        ? 'Categoría actualizada correctamente'
                        : 'Categoría creada correctamente');

                bootstrap.Modal.getInstance(document.getElementById('modalCategoria')).hide();
                this.loadCategorias();
                this.loadCategoriasParaSelect();
            } else {
                const error = await response.json();
                this.showNotification('danger', error.message || 'Error al guardar categoría');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('danger', 'Error de conexión');
        }
    }

    eliminarCategoria(categoriaId) {
        if (!confirm('¿Estás seguro de eliminar esta categoría? Se eliminarán todos los platos asociados.')) {
            return;
        }

        fetch(`/dashboard/api/categorias/${categoriaId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': this.csrfToken
            }
        })
        .then(response => {
            if (response.ok) {
                this.showNotification('success', 'Categoría eliminada correctamente');
                this.loadCategorias();
                this.loadCategoriasParaSelect();
            } else {
                this.showNotification('danger', 'Error al eliminar categoría');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('danger', 'Error de conexión');
        });
    }

    // ===== PLATOS =====
    async loadPlatos() {
        try {
            const response = await fetch('/dashboard/api/platos/');
            if (response.ok) {
                const platos = await response.json();
                this.renderPlatos(platos);
            }
        } catch (error) {
            console.error('Error cargando platos:', error);
        }
    }

    renderPlatos(platos) {
        const container = document.getElementById('platos-container');
        if (!container) return;

        container.innerHTML = platos.map(plato => `
            <div class="col-md-4 mb-4" data-plato-id="${plato.id}">
                <div class="card dashboard-card h-100">
                    ${plato.imagen ? `
                        <img src="${plato.imagen}" class="card-img-top" alt="${plato.nombre}" style="height: 200px; object-fit: cover;">
                    ` : ''}
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h5 class="card-title mb-0">${plato.nombre}</h5>
                            <span class="badge bg-primary">$${parseFloat(plato.precio).toFixed(2)}</span>
                        </div>
                        <p class="text-muted small mb-3">${plato.descripcion || 'Sin descripción'}</p>

                        <div class="mb-3">
                            ${plato.es_vegetariano ? '<span class="badge bg-success me-1">Vegetariano</span>' : ''}
                            ${plato.es_picante ? '<span class="badge bg-danger me-1">Picante</span>' : ''}
                            ${plato.disponible ? '<span class="badge bg-success">Disponible</span>' : '<span class="badge bg-secondary">No disponible</span>'}
                        </div>

                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">${plato.categoria_nombre}</small>
                            <div class="btn-group">
                                <button class="btn btn-sm btn-outline-primary"
                                        onclick="menuCRUD.editarPlato(${plato.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger"
                                        onclick="menuCRUD.eliminarPlato(${plato.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    abrirModalPlato() {
        this.currentPlatoId = null;
        document.getElementById('modalPlatoLabel').textContent = 'Nuevo Plato';
        document.getElementById('formPlato').reset();
        document.getElementById('platoId').value = '';
        document.getElementById('platoImagenPreview').innerHTML = '';

        // Cargar categorías en el select
        this.loadCategoriasParaSelect();

        new bootstrap.Modal(document.getElementById('modalPlato')).show();
    }

    async loadCategoriasParaSelect() {
        const select = document.getElementById('platoCategoria');
        if (!select) return;

        try {
            const response = await fetch('/dashboard/api/categorias/');
            if (response.ok) {
                const categorias = await response.json();
                select.innerHTML = categorias.map(cat =>
                    `<option value="${cat.id}">${cat.nombre}</option>`
                ).join('');
            }
        } catch (error) {
            console.error('Error cargando categorías:', error);
        }
    }

    editarPlato(platoId) {
        this.currentPlatoId = platoId;

        fetch(`/dashboard/api/platos/${platoId}/`)
            .then(response => response.json())
            .then(plato => {
                document.getElementById('modalPlatoLabel').textContent = 'Editar Plato';
                document.getElementById('platoId').value = plato.id;
                document.getElementById('platoNombre').value = plato.nombre;
                document.getElementById('platoDescripcion').value = plato.descripcion;
                document.getElementById('platoPrecio').value = plato.precio;
                document.getElementById('platoCategoria').value = plato.categoria_id;
                document.getElementById('platoDisponible').checked = plato.disponible;
                document.getElementById('platoVegetariano').checked = plato.es_vegetariano;
                document.getElementById('platoPicante').checked = plato.es_picante;

                if (plato.imagen) {
                    document.getElementById('platoImagenPreview').innerHTML = `
                        <img src="${plato.imagen}" class="img-thumbnail mb-2" style="max-height: 150px;">
                        <p class="text-muted small">Imagen actual</p>
                    `;
                }

                // Asegurarse de que las categorías estén cargadas
                this.loadCategoriasParaSelect().then(() => {
                    document.getElementById('platoCategoria').value = plato.categoria_id;
                    new bootstrap.Modal(document.getElementById('modalPlato')).show();
                });
            })
            .catch(error => {
                console.error('Error cargando plato:', error);
                this.showNotification('danger', 'Error al cargar plato');
            });
    }

    async guardarPlato(event) {
        event.preventDefault();

        const formData = new FormData(event.target);

        try {
            const url = this.currentPlatoId
                ? `/dashboard/api/platos/${this.currentPlatoId}/`
                : '/dashboard/api/platos/';

            const method = this.currentPlatoId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'X-CSRFToken': this.csrfToken
                },
                body: formData
            });

            if (response.ok) {
                this.showNotification('success',
                    this.currentPlatoId
                        ? 'Plato actualizado correctamente'
                        : 'Plato creado correctamente');

                bootstrap.Modal.getInstance(document.getElementById('modalPlato')).hide();
                this.loadPlatos();
            } else {
                const error = await response.json();
                this.showNotification('danger', error.message || 'Error al guardar plato');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('danger', 'Error de conexión');
        }
    }

    eliminarPlato(platoId) {
        if (!confirm('¿Estás seguro de eliminar este plato?')) {
            return;
        }

        fetch(`/dashboard/api/platos/${platoId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': this.csrfToken
            }
        })
        .then(response => {
            if (response.ok) {
                this.showNotification('success', 'Plato eliminado correctamente');
                this.loadPlatos();
            } else {
                this.showNotification('danger', 'Error al eliminar plato');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('danger', 'Error de conexión');
        });
    }

    previewImagen(event) {
        const input = event.target;
        const preview = document.getElementById('platoImagenPreview');

        if (input.files && input.files[0]) {
            const reader = new FileReader();

            reader.onload = function(e) {
                preview.innerHTML = `
                    <img src="${e.target.result}" class="img-thumbnail mb-2" style="max-height: 150px;">
                    <p class="text-muted small">Vista previa</p>
                `;
            };

            reader.readAsDataURL(input.files[0]);
        }
    }

    // ===== NOTIFICACIONES =====
    showNotification(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        const container = document.querySelector('.dashboard-content');
        if (container) {
            container.prepend(alertDiv);
        }

        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    // ===== EVENT BINDING =====
    bindEvents() {
        // Formulario categoría
        const formCategoria = document.getElementById('formCategoria');
        if (formCategoria) {
            formCategoria.addEventListener('submit', (e) => this.guardarCategoria(e));
        }

        // Formulario plato
        const formPlato = document.getElementById('formPlato');
        if (formPlato) {
            formPlato.addEventListener('submit', (e) => this.guardarPlato(e));
        }

        // Preview de imagen
        const imagenInput = document.getElementById('platoImagen');
        if (imagenInput) {
            imagenInput.addEventListener('change', (e) => this.previewImagen(e));
        }

        // Botones de acción
        document.getElementById('btnNuevaCategoria')?.addEventListener('click', () => this.abrirModalCategoria());
        document.getElementById('btnNuevoPlato')?.addEventListener('click', () => this.abrirModalPlato());
    }
}

// Inicializar
let menuCRUD;
document.addEventListener('DOMContentLoaded', () => {
    menuCRUD = new MenuCRUD();
    window.menuCRUD = menuCRUD;
});
