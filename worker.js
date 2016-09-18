var Gearman = require('node-gearman');
var spawn = require('child_process').spawn;
var gearman = new Gearman();

var worker;


function workerCallback(payload, worker) {
    var text, bulb;
    var callProcess = (process) => {
        bulb = spawn('sudo', [`/mnt/media/projects/temp/alarm/${process}.sh`]);
        bulb.on('close', (code) => {
            worker.end("DONE");
        });
    };

    action = payload.toString('utf8');
    console.log("action", action);
    switch (action) {
        case "bulbOff":
            callProcess('off');
            break;
        case "bulbOn1":
            callProcess('on1');
            break;
        case "bulbOn2":
            callProcess('on2');
            break;
        case "bulbOn3":
            callProcess('on3');
            break;
        case "bulbOn4":
            callProcess('on4');
            break;
        case "temp":
            job = gearman.submitJob("temp.reader", "");

            job.on("data", function(data){
                worker.end(data);
            });

            job.on("error", function(error){
                console.log(error.message);
            });
            break;
        default:
            worker.end("");
    }
}

gearman.registerWorker("iot.worker", workerCallback);
