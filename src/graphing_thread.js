// Load Pyodide and its dependency for service workers
importScripts("https://cdn.jsdelivr.net/npm/xhr-shim@0.1.3/src/index.min.js");
self.XMLHttpRequest = self.XMLHttpRequestShim;
importScripts('https://cdn.jsdelivr.net/pyodide/v0.22.1/full/pyodide.js');


/**
 * Initialize Pyodide and run the python source code for the application.
 * Register proxies of a python functions and objects to @property {object} this.pythonProxies
 */
async function startPyodide() {

    // Pyodide setup
    console.log("Loading Pyodide...")
    const pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");      
    const micropip = pyodide.pyimport("micropip");

    // Install dependencies
    await micropip.install('numpy')
    await micropip.install('plotly')
    await micropip.install('pandas')

    // Build source as a single file
    // As currently, pyodide has no way of importing custom modules
    const source = (await (await fetch('./figures.py')).text())
    .replace(/from data_models import MapState/, await (await fetch('./data_models.py')).text())
    .replace(/from utils import LinAlgUtils/, await (await fetch('./utils.py')).text())
    .concat(await (await fetch('./pyodide_start.py')).text());

    // Run source code 
    pyodide.runPython(source)

    // Register proxies from python to the service worker context
    this.pythonProxies = pyodide.globals.get('python_proxies');
};


/**
 * Update historic telemetry and map state in the python runtime.
 * 
 * @param {MessageEvent} message A received telemetry message.
 */
async function updateTelemetry(message) {

    // In case pyodide isn't loaded, abort
    if (!this.pythonProxies) return;

    /** @type {telemetryMessage} */
    const content = message.data;    

    // Update object according to message type
    switch(content.name) {

        case 'update-map_obj.json':
            this.pythonProxies.objects_from_json(JSON.stringify(content.data));
            return

        case 'update-indicators':
            this.pythonProxies.indicators_from_json(JSON.stringify(content.data));
            return

        case 'update-state':
            this.pythonProxies.state_from_json(JSON.stringify(content.data));
            return
    }
}


/**
 * Register a MessageChannel port to @property this.port to enable
 * communication between threads.
 */ 
addEventListener('message', e => {

    console.log('graphing thread: registering communication channel..');
    this.port = e.ports[0];
    this.port.onmessage = async message => await updateTelemetry(message);
})

/**
 * Register a fetch event interceptor.
 */
self.addEventListener('fetch', async event => {

    const url = new URL(event.request.url);

    // In case pyodide hasn't finished loading , abort interception
    if (!this.pythonProxies) return;

    // If the request isn't headed to the graphs API, ignore it
    if (url.host !== "localhost:8000") return;

    // Map url to graph
    switch (url.pathname) {

        case '/energy':
            event.respondWith(new Response(this.pythonProxies.energy_over_time()));
            return

        case '/radar-map':
            event.respondWith(new Response(this.pythonProxies.radar_map()));
            return

        case '/altitude':      
            event.respondWith(new Response(this.pythonProxies.altitude_over_time()));
            return

        case '/speed':
            event.respondWith(new Response(this.pythonProxies.speed_over_time()));
            return

        case '/artificial-horizon':
            event.respondWith(new Response(this.pythonProxies.artificial_horizon()));
            return
    }
})

startPyodide();
