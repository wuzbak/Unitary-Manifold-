/**
 * public-site/sw-geo-monitor.js
 * UM Geo Monitor v3 — PWA Service Worker (offline cache)
 *
 * Caches the last successful feed payloads so the app continues to show
 * data when the external feeds are unreachable.
 *
 * Strategy: network-first for feeds, cache-first for static assets.
 *
 * 🔵 ADJACENT TRACK — part of geo monitor infrastructure; not hardgate.
 */

'use strict';

const CACHE_NAME = 'um-geo-monitor-v3';
const STATIC_ASSETS = [
  '/az-apps/20-geo-monitor.html',
  '/js/20-geo-monitor.js',
];

// Feed URLs that should be cached on success
const FEED_PATTERNS = [
  'earthquake.usgs.gov',
  'eonet.gsfc.nasa.gov',
  'api.weather.gov',
  'api.avalanche.org',
  'services.swpc.noaa.gov',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS).catch(() => {}))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const url = event.request.url;
  const isFeed = FEED_PATTERNS.some(p => url.includes(p));

  if (isFeed) {
    // Network-first: serve from network, fall back to cached payload
    event.respondWith(
      fetch(event.request.clone()).then(resp => {
        if (resp && resp.status === 200) {
          const respClone = resp.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, respClone));
        }
        return resp;
      }).catch(() => caches.match(event.request))
    );
  } else {
    // Cache-first for static assets
    event.respondWith(
      caches.match(event.request).then(cached => cached || fetch(event.request))
    );
  }
});
