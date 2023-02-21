from machine import Pin, Timer

class Bus:
    def __init__(self):
        d1 = Pin(16, Pin.OUT)
        d2 = Pin(17, Pin.OUT)
        d3 = Pin(18, Pin.OUT)
        d4 = Pin(19, Pin.OUT)
        d5 = Pin(20, Pin.OUT)
        d6 = Pin(21, Pin.OUT)
        d7 = Pin(22, Pin.OUT)
        d8 = Pin(26, Pin.OUT)

        a1 = Pin(4, Pin.OUT)
        a2 = Pin(5, Pin.OUT)
        a3 = Pin(6, Pin.OUT)
        a4 = Pin(7, Pin.OUT)

        self.dbus = 0
        self.abus = 0
        self.dataleds = [d1,d2,d3,d4,d5,d6,d7,d8]
        self.addrleds = [a1,a2,a3,a4]
        self.reset()
        
    def reset(self):
        for i in range(8):
            self.dataleds[i].off()
        for i in range(4):
            self.addrleds[i].off()
        
    def dataBus(self,num):
        for i in range(8):
            if (num % pow(2,i+1) ) > pow(2,i)-1:
                self.dataleds[i].on()
            else:
                self.dataleds[i].off()

    def addrBus(self,num):
        global addrleds
        for i in range(4):
            if (num % pow(2,i+1) ) > pow(2,i)-1:
                self.addrleds[i].on()
            else:
                self.addrleds[i].off() 
