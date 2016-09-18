#!/usr/bin/env python

import sys
from scapy.all import *
import telebot
import gearman
import json
from StringIO import StringIO

BUFFER_SIZE = 1024

try:
    with open(sys.argv[1]) as data_file:
        data = json.load(data_file)
        myPhone = data['myPhone']
        routerIP = data['routerIP']
        TOKEN = data['telegramBotAPIKey']
        chatID = data['telegramChatId']
        gearmanServer = data['gearmanServer']
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

def getSensorData():
    gm_client = gearman.GearmanClient([gearmanServer])
    completed_job_request = gm_client.submit_job("iot.worker", 'break;')
    io = StringIO(completed_job_request.result)

    return json.load(io)

tb = telebot.TeleBot(TOKEN)

def arp_display(pkt):
    if pkt[ARP].op == 1 and pkt[ARP].hwsrc == myPhone and pkt[ARP].pdst == routerIP:
        sensorData = getSensorData()
        message = "Wellcome home Gonzalo! Temperature: %s humidity: %s" % (sensorData['temperature'], sensorData['humidity'])
        tb.send_message(chatID, message)
        print message

print sniff(prn=arp_display, filter='arp', store=0)
