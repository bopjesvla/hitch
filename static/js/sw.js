// Choose a cache name
const cacheName = 'hitchmap-v1';
// List the files to precache
const precacheResources = ['/', '/light.html', '/icon.png', '/favicon.ico', 'https://a.tile.openstreetmap.org/0/0/0.png'];

// When the service worker is installing, open the cache and add the precache resources to it
self.addEventListener('install', (event) => {
    console.log('Service worker install event!');
    event.waitUntil(caches.open(cacheName).then((cache) => cache.addAll(precacheResources)));
});

self.addEventListener('activate', (event) => {
    console.log('Service worker activate event!');
});

self.addEventListener('fetch', (event) => {
    console.log(event.request.url)
    if (event.request.destination === 'image') {
        event.respondWith(caches.open(cacheName).then((cache) => {
            // Go to the cache first
            return cache.match(event.request.url).then((cachedResponse) => {
                // Return a cached response if we have one
                if (cachedResponse) {
                    return cachedResponse;
                }

                // Otherwise, hit the network
                return fetch(event.request).then((fetchedResponse) => {
                    // Add the network response to the cache for later visits (NOPE LOTS OF TILES)
                    // cache.put(event.request, fetchedResponse.clone());

                    // Return the network response
                    return fetchedResponse;
                });
            });
        }));
    }
    else {
        // Open the cache
        event.respondWith(caches.open(cacheName).then((cache) => {
            // Go to the network first
            return fetch(event.request.url).then((fetchedResponse) => {
                cache.put(event.request, fetchedResponse.clone());

                return fetchedResponse;
            }).catch(() => {
                // If the network is unavailable, get
                return cache.match(event.request.url);
            });
        }));
    }
});
