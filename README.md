# home automations
Summer pet project

My stuff:
* I've got a fan connected to a Wemo switch (http://www.belkin.com/us/p/P-F7C027/).
* One BeeWi temperature & humidity sensor http://www.bee-wi.com/bbw200,us,4,BBW200-A1.cfm.
* One BeeWi Smart LED Color Bulb http://www.bee-wi.com/bbl207,us,4,BBL207-A1.cfm.

## tempReaderWorker.js
* gearman worker
* it reads temperature and humidity from my BeeWi sensor via BTLE

## worker.js
* gearman worker
* yes I know. It's ugly, but I need to add this worker. tempReaderWorker finish (process.exit()) after sending data to this worker. I don't want to free bt interface to be able to have more scripts using it. That's a fast and ugly solution but it works.

## bot.py
* Telegram bot
* The following commands are available:
 * /switchInfo: get switch info
 * /switchOFF: switch OFF the switch
 * /help: Gives you information about the available commands
 * /temp: Get temperature
 * /switchON: switch ON the switch

## sniff.py
* detects when I'm close to my home and sends me a message via Telegram with the temperature.
* It's a network sniffer
* It detects when my mobile phone send a ARP package to my router (aka when I connect to my Wifi). It happens before I enter in my house, so the telegram message arrives before I put the key in the door :)

## bulb.py
* control BeeWi Smart LED Color Bulb.

## alarm/crontab
* crontab to turn on/off and set the color of the bulb

## supervisor.conf
* all scripts are running in my Raspberry Pi3.
* I need to keep alive all. So I supervisor to ensure process are up
