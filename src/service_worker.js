async function cacheThenNetwork(request) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log("Found response in cache:", cachedResponse);
      return cachedResponse;
    }
    console.log("Falling back to network");
    return fetch(request);
  }
  
  self.addEventListener("fetch", (event) => {
    console.log(`Handling fetch event for ${event.request.url}`);
    event.respondWith(cacheThenNetwork(event.request));
});
