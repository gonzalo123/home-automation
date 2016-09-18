import telebot
import logging
import sys
import json
from StringIO import StringIO
import gearman
from ouimeaux.environment import Environment

BUFFER_SIZE = 1024
commands = {
    'help': 'Gives you information about the available commands',
    'temp': 'Get temperature',
    'switchON': 'switch ON the switch',
    'switchOFF': 'switch OFF the switch',
    'switchInfo': 'get switch info',
    'bulbOff': 'turn off bulb',
    'bulbOn1': 'turn on bulb (preset 1)',
    'bulbOn2': 'turn on bulb (preset 2)',
    'bulbOn3': 'turn on bulb (preset 3)',
    'bulbOn4': 'turn on bulb (preset 4)',
}

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

try:
    with open(sys.argv[1]) as data_file:
        data = json.load(data_file)
        TOKEN = data['telegramBotAPIKey']
        allowedChatIDs = data['allowedChatIDs']
        gearmanServer = data['gearmanServer'],
        wemoDevice = data['wemoDevice']
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise

def getSensorData():
    gm_client = gearman.GearmanClient(gearmanServer)
    completed_job_request = gm_client.submit_job("temp", 'temp')
    io = StringIO(completed_job_request.result)
    out = json.load(io)
    print out
    return out

def bulb(action):
    gm_client = gearman.GearmanClient(gearmanServer)
    completed_job_request = gm_client.submit_job("temp", action)
    io = StringIO(completed_job_request.result)
    print io

bot = telebot.TeleBot(TOKEN)

# help page
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "The following commands are available: \n"
    for key in commands:
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)

def extract_unique_code(text):
    return text.split()[1] if len(text.split()) > 1 else None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    print message
    unique_code = extract_unique_code(message.text)
    print unique_code
    reply = "Hello I'm a private bot of Gonzalo's house. I only speak with Gonzalo."
    bot.reply_to(message, reply)

@bot.message_handler(func=lambda message: message.text == "Hi")
def command_text_hi(m):
    if m.chat.id in allowedChatIDs:
        bot.send_message(m.chat.id, "Hello")
    else:
        bot.send_message(m.chat.id, "Yes. I know. You aren't Gonzalo and I said that I only speak with Gonzalo but I'm polite.")

@bot.message_handler(commands=['temp'])
def command_temp(m):
    if m.chat.id in allowedChatIDs:
        bot.send_message(m.chat.id, "Reading information ...")
        sensorData = getSensorData()
        message = "Temperature: %s humidity: %s" % (sensorData['temperature'], sensorData['humidity'])
        bot.send_message(m.chat.id, message)
    else:
        bot.send_message(m.chat.id, "Sory. I'm a private bot. I don't want to speak with you")

@bot.message_handler(commands=['bulbOff'])
def command_bulbOff(m):
    if m.chat.id in allowedChatIDs:
        bulb('bulbOff')
        message = "bulb Off"
        bot.send_message(m.chat.id, message)
    else:
        bot.send_message(m.chat.id, "Sory. I'm a private bot. I don't want to speak with you")

@bot.message_handler(commands=['bulbOn1'])
def command_bulbOn1(m):
    if m.chat.id in allowedChatIDs:
        bulb('bulbOn1')
        message = "bulb on (preset 1)"
        bot.send_message(m.chat.id, message)
    else:
        bot.send_message(m.chat.id, "Sory. I'm a private bot. I don't want to speak with you")

@bot.message_handler(commands=['bulbOn2'])
def command_bulbOn2(m):
    if m.chat.id in allowedChatIDs:
        bulb('bulbOn2')
        message = "bulb on (preset 2)"
        bot.send_message(m.chat.id, message)
    else:
        bot.send_message(m.chat.id, "Sory. I'm a private bot. I don't want to speak with you")

@bot.message_handler(commands=['bulbOn3'])
def command_bulbOn3(m):
    if m.chat.id in allowedChatIDs:
        bulb('bulbOn3')
        message = "bulb on (preset 3)"
        bot.send_message(m.chat.id, message)
    else:
        bot.send_message(m.chat.id, "Sory. I'm a private bot. I don't want to speak with you")

@bot.message_handler(commands=['bulbOn4'])
def command_bulbOn4(m):
    if m.chat.id in allowedChatIDs:
        bulb('bulbOn4')
        message = "bulb on (preset 4)"
        bot.send_message(m.chat.id, message)
    else:
        bot.send_message(m.chat.id, "Sory. I'm a private bot. I don't want to speak with you")

@bot.message_handler(commands=['switchInfo'])
def command_switchInfo(m):
    if m.chat.id in allowedChatIDs:
        def on_switch(switch):
            if wemoDevice == switch.name:
                bot.send_message(m.chat.id, "Switch found! state: %s" % 'ON' if switch.get_state() == 1 else 'OFF')
        bot.send_message(m.chat.id, "Looking for switch ...")
        env = Environment(on_switch)
        env.start()
        env.discover(seconds=3)
    else:
        bot.send_message(m.chat.id, "Sory. I'm a private bot. I don't want to speak with you")

@bot.message_handler(commands=['switchON'])
def command_switchON(m):
    if m.chat.id in allowedChatIDs:
        def on_switch(switch):
            if wemoDevice == switch.name:
                if switch.get_state() == 1:
                    bot.send_message(m.chat.id, "Switch already ON")
                else:
                    switch.basicevent.SetBinaryState(BinaryState=1)
                    bot.send_message(m.chat.id, "Switch ON")
        bot.send_message(m.chat.id, "Looking for switch ...")
        env = Environment(on_switch)
        env.start()
        env.discover(seconds=3)
    else:
        bot.send_message(m.chat.id, "Sory. I'm a private bot. I don't want to speak with you")

@bot.message_handler(commands=['switchOFF'])
def command_switchOFF(m):
    if m.chat.id in allowedChatIDs:
        def on_switch(switch):
            if wemoDevice == switch.name:
                if switch.get_state() == 0:
                    bot.send_message(m.chat.id, "Switch already OFF")
                else:
                    switch.basicevent.SetBinaryState(BinaryState=0)
                    bot.send_message(m.chat.id, "Switch OFF")
        bot.send_message(m.chat.id, "Looking for switch ...")
        env = Environment(on_switch)
        env.start()
        env.discover(seconds=3)
    else:
        bot.send_message(m.chat.id, "Sory. I'm a private bot. I don't want to speak with you")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def command_default(m):
    bot.send_message(m.chat.id, "I don't understand \"" + m.text + "\"\nMaybe try the help page at /help")

bot.polling()
