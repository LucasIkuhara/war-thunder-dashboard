Vue.createApp({

    data() {
        return {
            connStatus: true,
            favicon: null,
            speedGaugeDrawn: false,
            altitudeGaugeDrawn: false,
            SMEGaugeDrawn: false,
            artificialHorizonDrawn: false,
            slowRate: 1,
            slowGraphs: {
                "speed": {div: 'speed-gauge', endpoint: 'speed', loop: null},
                "altitude": {div: 'altitude-gauge', endpoint: 'altitude', loop: null},
                "energy": {div: 'sme-gauge', endpoint: 'energy', loop: null},
                "radar-map": {div: 'radar-map', endpoint: 'radar-map', loop: null},
            }
        }
    },

    async mounted() {

        console.log('Starting Dashboard')
        this.registerServiceThreads();

        await this.startSlowGraphs();
        const fastRate = 5;

        this.favicon = document.getElementById('favicon');

        // Fast cycle
        setInterval(async () => {
            
            await Promise.all([
                this.plot('artificial-horizon', 'artificial-horizon', true),
            ])

        }, (1/fastRate)*1000);

    },

    computed: {

        connectionStyle: function () {
            
            if (this.favicon) {
                
                this.connStatus ? 
                (this.favicon.href = "https://img.icons8.com/cute-clipart/2x/fighter-jet.png") :
                (this.favicon.href = "https://img.icons8.com/cute-clipart/2x/explosion.png")
            }

            return  {
                'connected': this.connStatus,
                'disconnected': !this.connStatus,
            }
        },

        
    },

    methods: {

        /**
         * Start all graphs defined in the data slowGraphs section.
         * Evenly distribute their update cycles in time according to their refresh rate.
         */
        async startSlowGraphs() {

            console.log('Initializing graphs...')
            const slowList = Object.keys(this.slowGraphs)

            slowList.forEach((graphName, index) => {
                
                const graph = this.slowGraphs[graphName];
                const startAfter = index*(1/this.slowRate)/slowList.length

                // Create graph objects
                this.plot(graph.div, graph.endpoint, false);

                // Create evenly-spaced update loops
                setTimeout(() => 
                    graph.loop = setInterval(async () => 
                        this.plot(graph.div, graph.endpoint, true),
                        this.slowRate*1000
                    ),

                startAfter);
            })

            console.log('Graphs initialized.')
        },

        /**
         * Plot a Plotly graph onto and HTML div using data from an API endpoint.
         * 
         * @param {string} div The element id of the div in which to mount the graph.
         * @param {string} endpoint The api endpoint from which to fetch the graph json.
         * @param {boolean} redraw Only refreshes if set to true, which is a lot faster, but requires
         * the graph to have been initialized previously.
         * @param {{displayModeBar: boolean, responsive: boolean}} config The graph's config object.
         */
        async plot(div, endpoint, redraw=true, config={displayModeBar: false, responsive: true}) {

            try {
                const response = await fetch(`http://localhost:8000/${endpoint}`)
                let graph = await response.json()

                if (redraw) this.refreshGraph(div, graph, config);
                else this.startGraph(div, graph, config);

                this.connStatus = true;
            }

            catch (err) {
                console.error(`Failed to plot ${div} due to an exception. Error: ${JSON.stringify(err)}`);
                this.connStatus = false;
            }
        },

        /**
         * Register a Data Thread and a Graphing Thread for completely embarked operation,
         * without requiring the python backend.
         * 
         * @throws In case service workers are not supported in the environment.
        **/
        async registerServiceThreads() {

            if (('serviceWorker' in navigator) && '') 
                throw new Error('ServiceWorker API not available in the current environment. Use of the app will require a backend.');

            // Start new threads
            const graphing_thread = await navigator.serviceWorker.register('../graphing_thread.js');
            const data_thread = new Worker("../data_thread.js");

            // Connect threads via MessageChannel, so they can talk to each other
            const channel = new MessageChannel();
            graphing_thread.active.postMessage('register', [channel.port2]);
            data_thread.postMessage('register', [channel.port1])
        },

        /**
         * refreshGraph
         * Refresh data in a Plotly Figure  
        **/
        refreshGraph(divName, graph, config) {
            Plotly.react(
                divName, 
                graph.data, 
                graph.layout,
                config
            );
        },

        /**
         * startGraph
         * Initialize Plotly Figure
        **/
        startGraph(divName, graph, config) {
            console.log(`Starting ${divName}`)
            Plotly.newPlot(
                divName, 
                graph.data, 
                graph.layout, 
                config
            );
        }

    }

}).mount('#app')
