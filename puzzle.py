from machine import Pin
import time
import uasyncio


led = Pin(25, Pin.OUT)
keyOne = Pin(15, Pin.IN, Pin.PULL_DOWN)
messagePin = Pin(16, Pin.OUT)

def checkLockOne():
    if (keyOne.value() == 1):
        global STATE
        STATE += 1

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

def blinkMorse(message, messagePin):
    SPACE_TIME = 0.25
    for letter in message:
        if (letter != ' '):
            await uasyncio.create_task(morseBlink(letter, messagePin))
        else:
            await uasyncio.sleep(SPACE_TIME)

async def stageBlink(blinks):
    for i in range(0, blinks):
        led.on()
        await uasyncio.sleep(0.1)
        led.off()
        await uasyncio.sleep(0.1)
    await uasyncio.sleep(1 - (0.1 * (blinks + 1)))
    
async def stageOneClue():
    global printingMessage
    await blinkMorse('.--. ..- .-.. .-.. .-.-.- .--. .. -. .-.-.- .---- ..... .-.-.- .... .. --. ....', messagePin)
    printingMessage = False

async def stageOne():
    print('stage one')
    global printingMessage
    
    blinkTask = uasyncio.create_task(stageBlink(1))
    
    if not printingMessage:
        printingMessage = True
        messageTask = uasyncio.create_task(stageOneClue())
    
    if STATE != 1:
       messageTask.cancel()

    checkLockOne()
    await blinkTask
    
async def stageTwo():
    print('stage two')
    uasyncio.run(stageBlink(2))
    
def main():
    while True:
        if STATE == 1:
            uasyncio.run(stageOne())
        if STATE == 2:
            uasyncio.run(stageTwo())

STATE = 1
printingMessage = False
uasyncio.run(main())


