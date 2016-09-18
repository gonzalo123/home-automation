var Gearman = require('node-gearman');

var gearman = new Gearman();

var worker;

function workerCallback(payload, worker) {
    job = gearman.submitJob("temp.reader", "");
    job.on("data", function(data){
        worker.end(data);
    });

    job.on("error", function(error){
        console.log(error.message);
    });

}

gearman.registerWorker("temp", workerCallback);
