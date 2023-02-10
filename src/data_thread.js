importScripts('https://cdnjs.cloudflare.com/ajax/libs/gl-matrix/3.4.2/gl-matrix-min.js');
console.log("Starting data thread..");

/**
 * Represents a telemetry message generated in the data thread.
 * @typedef telemetryMessage 
 * @property {string} name Type of telemetry represented by 'update-<type>'.
 * @property {object} data The telemetry data.
 */

// Wait for Channel Message port to be registered
this.port = null;
addEventListener('message', ev => {
    console.log('data thread: registering communication channel..');
    this.port = ev.ports[0];
})

/**
 * Fetch new telemetry data and post as a message.
 * The event name will be "update-endpoint" with the word "endpoint" being replaced
 * with the name of the endpoint. The event will contain the received data.
 * 
 * @emits update-<endpoint>
 * @param {string} endpoint The Endpoint name.
 * @throws In case the fetch or parsing fails.
*/
async function updateTelemetry(endpoint) {

    try {
        const data = await fetch(`http://localhost:8111/${endpoint}`);

        /**
         * Post to graphing thread 
         * @type {telemetry-message }
         */
        const msg = {
            name: `update-${endpoint}`,
            data: await data.json()
        };
        this.port.postMessage(msg)
    }

    catch(err) {
        throw new Error(`An exception ocurred while trying to update telemetry: ${err}`)
    }
}


// Register War Thunder's endpoints
updateRate = {
    "state": 0.03,
    "indicators": 0.03,
    "map_obj.json": 0.3
}

Object.keys(updateRate).forEach(async endpoint => {

    const rate = updateRate[endpoint];
    console.log(`Starting update loop for ${endpoint} every ${rate} seconds.`);
    setInterval(async () => {
        if (!this.port)
            throw new Error('Cannot update telemetry before the message channel port has been registered.')

        await updateTelemetry(endpoint)

    }, rate*1000);
})
