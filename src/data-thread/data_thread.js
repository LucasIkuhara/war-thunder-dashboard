/**
 * @callback DataThreadCallback
 * @param {} dataUpdate
 */

class DataThread {

    /**
     * @type {callback[]} 
     */
    registeredCallbacks = [];

    constructor() {

    }

    /**
     * @param {DataThreadCallback} callback 
     */
    registerCallback(callback) {

        if (typeof(callback) !== "function")
            throw Error("Callback registration of non-callable object attempted.");
    }
}