var noble,
    fs = require('fs'),
    Gearman = require('node-gearman'),
    beeWiData,
    address,
    bot,
    configuration,
    confPath,
    status,
    callback,
    gearman = new Gearman(),
    worker;

if (process.argv.length <= 2) {
    console.log("Usage: " + __filename + " conf.json");
    process.exit(-1);
}

confPath = process.argv[2];
try {
    configuration = JSON.parse(
        fs.readFileSync(process.argv[2])
    );
} catch (e) {
    console.log("configuration file not valid", e);
    process.exit(-1);
}
console.log("[START]");
address = configuration.beeWiAddress;
delay = configuration.tempServerDelayMinutes * 60 * 1000;
tcpPort = configuration.tempServerPort;

beeWiData = {};

function hexToInt(hex) {
    if (hex.length % 2 !== 0) {
        hex = "0" + hex;
    }
    var num = parseInt(hex, 16);
    var maxVal = Math.pow(2, hex.length / 2 * 8);
    if (num > maxVal / 2 - 1) {
        num = num - maxVal;
    }
    return num;
}

function workerCallback(payload, worker) {
    callback = function() {
        worker.end(JSON.stringify(beeWiData));
        console.log("[END]");
        process.exit();
    };

    beeWiData = {temperature: undefined, humidity: undefined, batery: undefined};

    if (status) {
        noble.stopScanning();
        noble.startScanning();
    } else {
        setTimeout(function() {
            workerCallback(payload, worker);
        }, 1000);
    }
}

gearman.registerWorker("temp.reader", function(payload, worker) {
    noble = require('noble');
    noble.on('stateChange', function(state) {
        if (state === 'poweredOn') {
            console.log("stateChange:poweredOn");
            status = true;
        } else {
            status = false;
        }
    });

    noble.on('discover', function(peripheral) {
        console.log('peripheral discovered (' + peripheral.id +
                  ' with address <' + peripheral.address +  ', ' + peripheral.addressType + '>,' +
                  ' connectable ' + peripheral.connectable + ',' +
                  ' RSSI ' + peripheral.rssi + ':' + peripheral.advertisement.localName);

        if (peripheral.address == address) {
            var data = peripheral.advertisement.manufacturerData.toString('hex');
            beeWiData.temperature = parseFloat(hexToInt(data.substr(10, 2)+data.substr(8, 2))/10).toFixed(1);
            beeWiData.humidity = Math.min(100,parseInt(data.substr(14, 2),16));
            beeWiData.batery = parseInt(data.substr(24, 2),16);
            beeWiData.date = new Date();
            noble.stopScanning();
        }
    });

    noble.on('scanStop', function() {
        console.log('scanStop', beeWiData);
        noble.stopScanning();
        callback();
    });
    setTimeout(function() {
        console.log("[END] Something wrong happens.");
        process.exit();
    }, 10000);
    workerCallback(payload, worker);
});
