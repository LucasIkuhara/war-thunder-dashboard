if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register("src/service_worker.js");
}
else {
    console.log("Service worker API is not available in the current context.");
}
