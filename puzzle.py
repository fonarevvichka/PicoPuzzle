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
    pin.on()
    if (character == '-'):
        await uasyncio.sleep(0.15)
    else:
        await uasyncio.sleep(0.05)
    pin.off()

async def blinkMorse(message, messagePin):
    for letter in message:
        if (letter != ' '):
            print(letter)
            uasyncio.run(morseBlink(letter, messagePin))
        else:
            uasyncio.sleep(0.15)

async def stageBlink(blinks):
    for i in range(0, blinks):
        led.on()
        await uasyncio.sleep(0.1)
        led.off()
        await uasyncio.sleep(0.1)
    await uasyncio.sleep(1 - (0.1 * (blinks + 1)))
    
async def stageOneClue():
    uasyncio.run(blinkMorse('.--. ..- .-.. .-.. .-.-.- .--. .. -. .-.-.- .---- ..... .-.-.- .... .. --. ....', messagePin))

async def stageOne():
    uasyncio.run(stageBlink(1))
    uasyncio.run(stageOneClue())
    checkLockOne()
    
async def stageTwo():
    uasyncio.run(stageBlink(2))
    
def main():    
    while True:
        if STATE == 1:
            uasyncio.run(stageOne())
        if STATE == 2:
            uasyncio.run(stageTwo())
STATE = 1
if __name__ == "__main__":
    main()
