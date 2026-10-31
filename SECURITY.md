# Política de Seguridad - Carta Virtual Cuba

## Versiones Soportadas
Actualmente, solo la rama `main` recibe actualizaciones de seguridad.

| Versión | Soportada |
| ------- | --------- |
| 1.0.x   | ✅ Sí     |

## Arquitectura de Seguridad Implementada

1. **Aislamiento de Red:** Los pedidos solo se aceptan si la IP del cliente está en el rango privado local (10.x.x.x, 192.168.x.x). El servidor rechaza peticiones de pedidos desde internet.
2. **Protección CSRF:** Todas las peticiones POST (carrito, login) están protegidas con Tokens CSRF de Django.
3. **Prevención de Inyección SQL:** Uso exclusivo del ORM de Django, lo que neutraliza ataques de inyección SQL.
4. **Rate Limiting (Sesión):** Límite de 4 pedidos por sesión y caducidad de la sesión a los 90 minutos para evitar spam.
5. **Validación en Backend:** Los datos enviados por el cliente (mesa, cantidades, personas) son re-validados en el servidor. Ignoramos los datos manipulados desde el navegador (F12).
6. **UUIDs:** Las URLs de los menús usan UUID4 en lugar de IDs secuenciales para evitar la enumeración de menús de otros restaurantes.

## Reportar una Vulnerabilidad
Si encuentras una falla de seguridad, por favor NO abras un "Issue" público. Envía un correo a [TU CORREO ELECTRÓNICO] con los detalles. Nos comprometemos a responder en un plazo de 48 horas.