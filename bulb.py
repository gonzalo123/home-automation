import os
import sys
import json
from subprocess import call, check_output
import pexpect
import time

def cycleHCI():
    call(['hciconfig', 'hci0', 'down'])
    time.sleep(0.1)
    call(['hciconfig', 'hci0', 'up'])
    time.sleep(0.1)

def getSettings(mac):
    cycleHCI()
    settings_array = [0, 0, 0, 0, 0]
    raw_input = check_output(['gatttool', '-i', 'hci0', '-b', mac, '--char-read', '--handle=0x0024'])
    if ':' in raw_input:
        raw_list = raw_input.split(':')
        raw_data = raw_list[1]
        raw_data = raw_data.strip()
        octet_list = raw_data.split(' ')
        if len(octet_list) > 4:
            for i in range(0, 5):
                j = int(octet_list[i], 16)
                settings_array[i] = j
    return settings_array

def getDeviceInfo(mac):
    deviceName = ''
    deviceVers = ''
    raw_input = check_output(['gatttool', '-i', 'hci0', '-b', mac, '--char-read', '--handle=0x0003'])
    if ':' in raw_input:
        raw_list = raw_input.split(':')
        raw_data = raw_list[1]
        raw_data = raw_data.strip()
        octet_list = raw_data.split(' ')
        for octet in octet_list:
            j = int(octet, 16)
            if j > 31 and j < 127:
                deviceName += str(unichr(j))
    raw_input = check_output(['gatttool', '-i', 'hci0', '-b', mac, '--char-read', '--handle=0x0018'])
    if ':' in raw_input:
        raw_list = raw_input.split(':')
        raw_data = raw_list[1]
        raw_data = raw_data.strip()
        octet_list = raw_data.split(' ')
        for octet in octet_list:
            j = int(octet, 16)
            if j > 31 and j < 127:
                deviceVers += str(unichr(j))
    cycleHCI()
    return (deviceName, deviceVers)

def writeCommandToBulb(mac, the_command):
    if the_command != '':
        the_command = '55' + the_command + '0D0A'
        cycleHCI()
        hd = check_output(['/usr/bin/hcitool', '-i', 'hci0', 'lecc', mac])
        ha = hd.split(' ')
        connectionHandle = 0
        if ha[0] == 'Connection' and ha[1] == 'handle':
            connectionHandle = ha[2]
        if connectionHandle > 0:
            bulb = pexpect.spawn('gatttool -i hci0 -b ' + mac + ' -I')
            bulb.expect('\[LE\]>', timeout=60)
            bulb.sendline('connect')
            bulb.expect('\[LE\]>', timeout=60)
            bulb.sendline('char-write-cmd 0x0021 ' + the_command)
            bulb.expect('\[LE\]>', timeout=60)
            bulb.sendline('disconnect')
            bulb.expect('\[LE\]>', timeout=60)
            bulb.sendline('exit')
            bulb.expect(pexpect.EOF, timeout=60)
            call(['hcitool', '-i', 'hci0', 'ledc', connectionHandle])
        cycleHCI()

def setBrightness(mac, value):
    # brightness command is 12 [02 to 0B] (18, [2 to 11])
    if value == 'low':
        writeCommandToBulb(mac, '1202')
    elif value == 'med':
        writeCommandToBulb(mac, '1207')
    else:
        writeCommandToBulb(mac, '120B')

def setBulbWhiteTemp(mac, tone):
    # brightness command is 11 [02 to 0B] (17, [2 to 11])
    if tone == 'warm':
        writeCommandToBulb(mac, '110B')
    elif tone == 'cool':
        writeCommandToBulb(mac, '1102')

def setBulbWhite(mac):
    # set to white command is 14 FF FF FF (20, -128, -128, -128)
    writeCommandToBulb(mac, '14FFFFFF')

def setBulbColour(mac, colour):
    # colour command is 13 RR GG BB (19, Red, Green, Blue)
    value = '13' + colour
    writeCommandToBulb(mac, value)

def switchBulbOn(mac):
    # on command is 10 01 (16, 1)
    writeCommandToBulb(mac, '1001')

def switchBulbOff(mac):
    # off command is 10 00 (16, 0)
    writeCommandToBulb(mac, '1000')

def printHelp():
    print 'Correct usage is "[sudo] beewibulb <device address> <command> [argument]"'
    print '       <device address> in the format XX:XX:XX:XX:XX:XX'
    print '       Commands:  toggle          - toggle light on / off'
    print '                  on              - turn light on'
    print '                  off             - turn light off'
    print '                  bright          - set brightness to 100%'
    print '                  medium          - set brightness to  60%'
    print '                  dim             - set brightness to  10%'
    print '                  colour RRGGBB   - set bulb to colour RRGGBB'
    print '                  white           - set bulb to white mode'
    print '                  warm            - set white to warm CCT'
    print '                  cool            - set white to cool CCT'

if __name__ == '__main__':
    try:
        with open(sys.argv[1]) as data_file:
            data = json.load(data_file)
            bulbAddress = data['bulbAddress']
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    if os.geteuid() != 0:
        print 'WARNING: This script may not work correctly without sudo / root. Sorry.'
    if len(sys.argv) < 3:
        printHelp()
    else:
        bulbIsOn = False
        bulbIsWhite = False
        device_address = bulbAddress
        command = sys.argv[2]
        command = command.lower()
        extra = ''
        error = ''
        if len(sys.argv) == 4:
            extra = sys.argv[3]
        extra = extra.lower()

        if len(device_address) != 17:
            print 'ERROR: device address must be in the format NN:NN:NN:NN:NN:NN'
            exit()
        settings = getSettings(device_address)
        if (settings[0] % 2) == 1:
            bulbIsOn = True
        if (settings[1] & 15) > 0:
            bulbIsWhite = True
        if command == 'colour' and extra == 'ffffff':
            command = 'white'
        if 'stat' in command:
            name, version = getDeviceInfo(device_address)
            status = '%02x %02x %02x %02x %02x' % (settings[0], settings[1], settings[2], settings[3], settings[4])
            colour = '%02x%02x%02x' % (settings[2], settings[3], settings[4])
            brightness = (((settings[1] & 240) >> 4) - 1) * 10
            print 'bulb name   = ' + name
            print 'firmware    = ' + version
            print 'raw status  = ' + status
            print 'bulbIsOn    = ' + str(bulbIsOn)
            print 'bulbIsWhite = ' + str(bulbIsWhite)
            print 'brightness  = ' + str(brightness) + '%'
            if bulbIsWhite:
                cct = (settings[1] & 15)
                if cct == 2:
                    cct = 'cool'
                if cct == 11:
                    cct = 'warm'
                print 'white tone  = ' + cct
            else:
                print 'colour      = ' + colour
        elif command == 'on':
            if not bulbIsOn:
                switchBulbOn(device_address)
        elif command == 'off':
            if bulbIsOn:
                switchBulbOff(device_address)
        elif command == 'toggle':
            if bulbIsOn:
                switchBulbOff(device_address)
            else:
                switchBulbOn(device_address)
        elif bulbIsOn:
            if command == 'bright':
                setBrightness(device_address, 'high')
            elif command == 'dim':
                setBrightness(device_address, 'low')
            elif command == 'medium':
                setBrightness(device_address, 'med')
            elif command == 'warm' or command == 'cool':
                if bulbIsWhite:
                    setBulbWhiteTemp(device_address, command)
            elif command == 'white':
                if not bulbIsWhite:
                    setBulbWhite(device_address)
            elif command == 'colour':
                if len(extra) == 6:
                    setBulbColour(device_address, extra)
                elif extra == '':
                    extra = '%02x%02x%02x' % (settings[2], settings[3], settings[4])
                    setBulbColour(device_address, extra)
                else:
                    error = 'ERROR: colour command requires a 6-digit colour argument, in hex. eg. 6633CC'
            else:
                printHelp()
        else:
            error = 'off'
        if error != '':
            if error == 'off':
                error = 'ERROR: Turn the bulb on before trying to change the settings.'
            print error
    exit()
