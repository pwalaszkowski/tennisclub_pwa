const CACHE_NAME = 'tennisclub-v1';
const urlsToCache = [
  '/',
  '/static/css/styles.css',
  '/static/images/icons/icon-512x512.png',
];

// Installation files to cache
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Activate - clear old cache
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      )
    )
  );
});

// Request handling
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request).catch(() =>
      caches.match(event.request).then(response =>
        response || caches.match('/static/offline.html')
      )
    )
  );
});