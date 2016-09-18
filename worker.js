var Gearman = require('node-gearman');
var spawn = require('child_process').spawn;
var gearman = new Gearman();

var worker;

function workerCallback(payload, worker) {
    var text = payload.toString('utf8');
    console.log(text);
    var bulb;
    switch (text) {
        case "bulbOff":
            bulb = spawn('sudo', ['/mnt/media/projects/temp/alarm/off.sh']);
            bulb.on('close', (code) => {
                console.log(`child process exited with code ${code}`);
                worker.end("DONE");
            });
            break;
        case "bulbOn1":
            bulb = spawn('sudo', ['/mnt/media/projects/temp/alarm/on1.sh']);
            bulb.on('close', (code) => {
                console.log(`child process exited with code ${code}`);
                worker.end("DONE");
            });
            break;
        case "bulbOn2":
            bulb = spawn('sudo', ['/mnt/media/projects/temp/alarm/on2.sh']);
            bulb.on('close', (code) => {
                console.log(`child process exited with code ${code}`);
                worker.end("DONE");
            });
            break;
        case "bulbOn3":
            bulb = spawn('sudo', ['/mnt/media/projects/temp/alarm/on3.sh']);
            bulb.on('close', (code) => {
                console.log(`child process exited with code ${code}`);
                worker.end("DONE");
            });
            break;
        case "bulbOn4":
            bulb = spawn('sudo', ['/mnt/media/projects/temp/alarm/on4.sh']);
            bulb.on('close', (code) => {
                console.log(`child process exited with code ${code}`);
                worker.end("DONE");
            });
            break;
        case "temp":
            job = gearman.submitJob("temp.reader", "");

            job.on("data", function(data){
                worker.end(data);
            });

            job.on("error", function(error){
                console.log(error.message);
            });
    }
}

gearman.registerWorker("temp", workerCallback);
