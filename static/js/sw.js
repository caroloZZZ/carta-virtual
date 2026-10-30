// KILL SWITCH: este SW se auto-desregistra y borra todos sus cachés.
// Se reemplazará por el SW real cuando el proyecto pase a fase PWA.

self.addEventListener('install', () => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        (async () => {
            // Borrar todos los cachés
            const keys = await caches.keys();
            await Promise.all(keys.map(k => caches.delete(k)));

            // Auto-desregistrarse
            const regs = await self.registration.unregister();
            console.log('[KILL SW] Caches borrados y SW desregistrado');

            // Notificar a clientes abiertos (opcional)
            const clients = await self.clients.matchAll();
            clients.forEach(c => c.postMessage({ type: 'SW_KILLED' }));
        })()
    );
});

// Passthrough: no interceptar nada (si queda vivo por un tiempo)
self.addEventListener('fetch', (event) => {
    event.respondWith(fetch(event.request));
});
