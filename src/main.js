
Vue.createApp({

    data() {
        return {
            connStatus: true,
            favicon: null,
            speedGaugeDrawn: false,
            altitudeGaugeDrawn: false,
            SMEGaugeDrawn: false,
            artificialHorizonDrawn: false
        }
    },

    async mounted() {

        console.log('Starting Dashboard')

        const slowRate = 1;
        const fastRate = 8;

        this.favicon = document.getElementById('favicon');

        // Start graphs
        console.log('Initializing graphs...')
        await Promise.all([
            this.plot('speed-gauge', 'speed', false),
            this.plot('altitude-gauge', 'altitude', false),
            this.plot('sme-gauge', 'energy', false),
            this.plot('radar-map', 'radar-map', false),
            this.plot('artificial-horizon', 'artificial-horizon', false)
        ]);
        console.log('Graphs initialized.')

        // Start update cycles
        // Slow cycle
        setInterval(async () => {
            
            await Promise.all([
                this.plot('speed-gauge', 'speed', true),
                this.plot('altitude-gauge', 'altitude', true),
                this.plot('sme-gauge', 'energy', true),
                this.plot('radar-map', 'radar-map', true)
            ])

        }, (1/slowRate)*1000);
        
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
        async plot(div, endpoint, redraw=true, config={displayModeBar: false, responsive: true}) {
        
            await fetch(`http://localhost:8000/${endpoint}`)
            .then( async (value) => {
                let graph = await value.json()
                
                if (redraw) this.refreshGraph(div, graph, config);
                else this.startGraph(div, graph, config);

                this.connStatus = true;

            }).catch(() => {
                this.connStatus = false;
            })

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