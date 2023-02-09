importScripts('https://cdn.jsdelivr.net/pyodide/v0.22.1/full/pyodide.js');


async function main() {

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
    const FigureFactory = pyodide.globals.get('FigureAsJSON')
    
    const r = FigureFactory.speed_series([1,2,3], [2,3,4])
    console.log(r)

 
    addEventListener('new-telemetry', e => {
        console.log('received', e)
    })
};

main();

