# CHECKLIST DE VERIFICACIÓN - CARTA VIRTUAL CUBA

## ✅ FLUJO DE AUTENTICACIÓN

### 1. Usuario NO autenticado:
- [ ] Acceder a `/` → Debe mostrar home público
- [ ] Acceder a `/login/` → Debe mostrar formulario login
- [ ] Acceder a `/registro/` → Debe mostrar formulario registro
- [ ] Acceder a `/dashboard/` → Debe REDIRIGIR a `/login/?next=/dashboard/`

### 2. Registro nuevo usuario:
- [ ] Completar formulario en `/registro/`
- [ ] Debe crear usuario y restaurante
- [ ] Debe hacer login automático después del registro
- [ ] Debe redirigir a `/dashboard/`

### 3. Login existente:
- [ ] Usar credenciales correctas → Debe redirigir a `/dashboard/`
- [ ] Usar credenciales incorrectas → Debe mostrar error
- [ ] Campo "Recordarme" debe funcionar

### 4. Usuario autenticado:
- [ ] `/dashboard/` → Debe mostrar panel de control
- [ ] `/logout/` → Debe cerrar sesión y redirigir a home
- [ ] Después de logout, `/dashboard/` debe redirigir a login

## ✅ FLUJO RESTAURANTE

### 1. Dashboard:
- [ ] Mostrar nombre del restaurante
- [ ] Mostrar estadísticas básicas
- [ ] Links de navegación funcionan

### 2. Menú:
- [ ] `/dashboard/menu/` → Listar categorías y platos
- [ ] Poder crear nueva categoría
- [ ] Poder crear nuevo plato
- [ ] Poder editar/eliminar
- [ ] Cambios deben persistir

### 3. Pedidos:
- [ ] `/dashboard/pedidos/` → Listar pedidos
- [ ] Ver detalles de pedido
- [ ] Cambiar estado (pendiente → confirmado → etc.)
- [ ] Estados deben actualizarse

### 4. QR:
- [ ] `/dashboard/qr/` → Mostrar código QR
- [ ] QR debe tener URL correcta
- [ ] Botón de descarga debe funcionar

### 5. Configuración:
- [ ] `/restaurantes/mi-restaurante/` → Editar info
- [ ] Cambios deben guardarse
- [ ] Subir logo debe funcionar

## ✅ FLUJO CLIENTE (VISTA PÚBLICA)

### 1. Acceso por QR:
- [ ] Escanear QR o ir a `/cliente/{uuid}/`
- [ ] Debe mostrar carta del restaurante
- [ ] Nombre y logo del restaurante visibles

### 2. Navegación carta:
- [ ] Categorías deben mostrarse
- [ ] Platos deben mostrarse con precios
- [ ] Imágenes de platos deben cargar
- [ ] Filtros/ordenamiento deben funcionar

### 3. Carrito:
- [ ] Agregar plato al carrito
- [ ] Carrito debe actualizar cantidad
- [ ] Ver carrito debe mostrar items
- [ ] Modificar cantidades en carrito
- [ ] Eliminar items del carrito

### 4. Checkout:
- [ ] Ir a checkout desde carrito
- [ ] Formulario de información cliente
- [ ] Confirmar pedido
- [ ] Debe mostrar número/confirmación

### 5. Seguimiento:
- [ ] `/cliente/seguimiento/{codigo}/`
- [ ] Mostrar estado del pedido
- [ ] Actualizarse cuando cambia estado

## ✅ RESPONSIVE Y UX

### 1. Desktop:
- [ ] Todo funciona correctamente
- [ ] Layout organizado
- [ ] Navegación clara

### 2. Tablet:
- [ ] Menús se ajustan
- [ ] Cards se reorganizan
- [ ] Textos legibles

### 3. Móvil:
- [ ] Navbar colapsa correctamente
- [ ] Botones táctiles tamaño adecuado
- [ ] Formularios usables
- [ ] Carrito accesible

### 4. Performance:
- [ ] Páginas cargan rápido (<3s)
- [ ] Imágenes optimizadas
- [ ] JavaScript no bloqueante

## ✅ SEGURIDAD

### 1. Accesos:
- [ ] Usuario no puede acceder dashboard de otro
- [ ] Cliente no puede acceder dashboard
- [ ] APIs requieren autenticación

### 2. Formularios:
- [ ] CSRF tokens presentes
- [ ] Validación frontend y backend
- [ ] SQL injection prevenida

### 3. Archivos:
- [ ] Uploads restringidos (imágenes)
- [ ] Path traversal prevenido
- [ ] Nombres de archivos seguros

## ✅ DATOS DE PRUEBA

Para probar completamente, necesitas:

### 1. Usuarios:
- Superusuario (admin)
- Usuario con restaurante
- Usuario sin restaurante

### 2. Restaurante:
- Con logo subido
- Con categorías creadas
- Con platos creados (algunos con imágenes)

### 3. Pedidos:
- Varios pedidos en diferentes estados
- Pedidos con múltiples items
- Pedidos recientes y antiguos

## 🚨 PROBLEMAS COMUNES A VERIFICAR

### URLs incorrectas:
