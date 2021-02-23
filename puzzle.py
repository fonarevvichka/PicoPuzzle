from machine import Pin
import time
import uasyncio


led = Pin(25, Pin.OUT)
keyOne = Pin(15, Pin.IN, Pin.PULL_DOWN)

def checkLockOne():
    if (keyOne.value() == 1):
        global STATE
        STATE += 1

async def stageBlink(blinks):
    for i in range(0, blinks):
        led.on()
        await uasyncio.sleep(0.1)
        led.off()
        await uasyncio.sleep(0.1)
    await uasyncio.sleep(1 - (0.1 * (blinks + 1)))
    
async def stageOne():
    uasyncio.run(stageBlink(1))
    #stageOneMessage()
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