# home automations
Summer pet project

I've got a fan connected to a Wemo switch (http://www.belkin.com/us/p/P-F7C027/).
I also have one BeeWi temperature & humidity sensor http://www.bee-wi.com/bbw200,us,4,BBW200-A1.cfm.

## worker.js
* gearman worker
* it reads temperature and humidity from my BeeWi sensor via BTLE

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

## supervisor.conf
* all scripts are running in my Raspberry Pi3.
* I need to keep alive all. So I supervisor to ensure process are up
