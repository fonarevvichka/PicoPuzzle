from machine import Pin, ADC
import time
import uasyncio


led = Pin(25, Pin.OUT)
keyOne = Pin(15, Pin.IN, Pin.PULL_DOWN)
clueOnePin = Pin(17, Pin.OUT)
clueTwoPin = Pin(16, Pin.OUT)
keysTwo = [Pin(0, Pin.IN, Pin.PULL_UP), Pin(2, Pin.IN, Pin.PULL_UP), Pin(4, Pin.IN, Pin.PULL_UP), \
           Pin(6, Pin.IN, Pin.PULL_UP), Pin(8, Pin.IN, Pin.PULL_UP), Pin(10, Pin.IN, Pin.PULL_UP)]

adcPin = Pin(26, Pin.IN, Pin.PULL_DOWN)
adcPin = ADC(0)

def checkLockOne():
    global printingMessage
    if (keyOne.value() == 1):
        global STATE
        STATE += 1
        printingMessage = False
        messageTask.cancel()

async def checkLockTwo():
    for pin in keysTwo:
        if pin.value():
            return

    global STATE
    STATE += 1
    messageTask.cancel()

async def checkLockThree():
    print(adcPin.read_u16())
    # currPin = 
    # global STATE
    # STATE += 1
    # messageTask.cancel()

async def blinkReset(pin):
    # indicate reset
    for i in range(0, 10):
        pin.on()
        await uasyncio.sleep(0.05)
        pin.off()
        await uasyncio.sleep(0.05)


async def morseBlink(character, pin):
    DOT_TIME = .15
    DASH_TIME = 0.25
    PAUSE_TIME = 0.1

    pin.on()
    if (character == '-'):
        await uasyncio.sleep(DASH_TIME)
    else:
        await uasyncio.sleep(DOT_TIME)
    pin.off()
    await uasyncio.sleep(PAUSE_TIME)


def blinkMorse(message, pin):
    SPACE_TIME = 0.25
    for letter in message:
        if (letter != ' '):
            await uasyncio.create_task(morseBlink(letter, pin))
        else:
            await uasyncio.sleep(SPACE_TIME)
    await blinkReset(pin)


async def sendBinaryMessage(message, pin):
    for character in message:
        if character == '0':
            pin.off()
            await uasyncio.sleep(0.25)
        else:
            pin.on()
            await uasyncio.sleep(0.25)

    await uasyncio.sleep(0.25)
    await blinkReset(pin)


async def stageBlink(blinks):
    for i in range(0, blinks):
        led.on()
        await uasyncio.sleep(0.1)
        led.off()
        await uasyncio.sleep(0.1)
    await uasyncio.sleep(1 - (2 *(0.1 * (blinks))))


async def stageOneClue():
    global printingMessage
    #  pull pin 15 high
    await blinkMorse('.--. ..- .-.. .-.. .-.-.- .--. .. -. .-.-.- .---- ..... .-.-.- .... .. --. ....', clueOnePin)
    printingMessage = False


async def stageTwoClue():
    global printingMessage
    await sendBinaryMessage('00101101', clueTwoPin)
    printingMessage = False


async def stageThreeClue():
    global printingMessage
    #  i.want.about.2.5v.at.adc.0
    await blinkMorse('.. .-.-.- .-- .- -. - .-.-.- .- -... --- ..- - .-.-.- ..--- .-.-.- ..... ...- .-.-.- .- - .-.-.- .- -.. -.-. .-.-.- -----', clueOnePin)
    printingMessage = False


async def stageOne():
    global printingMessage
    global messageTask 
    
    blinkTask = uasyncio.create_task(stageBlink(1))
    
    if not printingMessage:
        printingMessage = True
        messageTask = uasyncio.create_task(stageOneClue())
    
    checkLockOne()
    await blinkTask


async def stageTwo():
    global printingMessage
    print('I may be xored but an even pin holds the key')
    print('5D 58 41 41 0D 4C 41 41 0D 48 5B 48 43 0D 5D 44 43 5E 0D 41 48 5E 5E 0D 59 45 4C 43 0D 1C 1C 0D 49 42 5A 43')
    
    blinkTask = uasyncio.create_task(stageBlink(2))
    if not printingMessage:
        printingMessage = True
        messageTask = uasyncio.create_task(stageTwoClue())

    uasyncio.create_task(checkLockTwo())
    await blinkTask


async def stageThree():
    global printingMessage
    blinkTask = uasyncio.create_task(stageBlink(3))

    if not printingMessage:
        printingMessage = True
        messageTask = uasyncio.create_task(stageThreeClue())

    uasyncio.create_task(checkLockThree())

    await blinkTask

async def stageSolved():
    blinkTask = uasyncio.create_task(stageBlink(5))
    await blinkTask

def main():
    while True:
        if STATE == 1:
            uasyncio.run(stageOne())
        if STATE == 2:
            uasyncio.run(stageTwo())
        if STATE == 3:
            uasyncio.run(stageThree())
        if STATE == 4:
            uasyncio.run(stageSolved())
            print('good job')

STATE = 1
printingMessage = False
uasyncio.run(main())
