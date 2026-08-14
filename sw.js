const CACHE = "guia-operativa-v7-executive-20260814";
const CORE = ["./", "index.html", "offline.html", "styles.css", "app.js", "objectives.js", "data/content.js", "data/objectives.js", "data/objectives.json", "assets/icon-192.png", "assets/icon-512.png", "manifest.webmanifest", "assets/products/temporada/unicorn-frappuccino.webp", "assets/products/temporada/salsa-azul-drizzle.webp", "assets/references/temporada/unicorn-frappuccino.webp", "assets/references/temporada/salsa-azul-drizzle.webp", "assets/campaigns/unicorn-checklist.webp", "assets/campaigns/unicorn-buenas-practicas.webp", "assets/campaigns/unicorn-concurso.webp"];
self.addEventListener("install", event => event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(CORE)).then(() => self.skipWaiting())));
self.addEventListener("activate", event => event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim())));
self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") return;
  if (event.request.mode === "navigate") {
    event.respondWith(fetch(event.request).then(response => { const copy = response.clone(); caches.open(CACHE).then(cache => cache.put(event.request, copy)); return response; }).catch(() => caches.match(event.request).then(cached => cached || caches.match("index.html") || caches.match("offline.html"))));
    return;
  }
  event.respondWith(caches.match(event.request).then(cached => {
    const update = fetch(event.request).then(response => { if (response.ok && new URL(event.request.url).origin === self.location.origin) caches.open(CACHE).then(cache => cache.put(event.request, response.clone())); return response; }).catch(() => cached || Response.error());
    return cached || update;
  }));
});
