'use strict';

const CACHE_NAME = 'psicat-braided-brain-v3';
const STATIC_ASSETS = [
  './ui/index.html',
  './ui/app.js?v=3',
  './ui/game-core.js?v=3',
  './ui/manifest.webmanifest?v=2',
  './ui/icon-192.png',
  './ui/icon-192.png?v=3',
  './ui/icon-512.png',
  './ui/icon-512.png?v=3',
  './ui/favicon.png',
  './css/main.css?v=3',
  './README.md',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.matchAll({ includeUncontrolled: true }))
      .then((clients) => Promise.all(clients.map((client) => client.postMessage({ type: 'psicat-braided-brain-offline-ready' }))))
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((response) => {
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return response;
      });
    })
  );
});
