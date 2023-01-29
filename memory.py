class Memory:
    def __init__(self):
        self.data = [0] * 256
        self.lastAccess = -1

    def load(self, address):
        if address < 0 or address >= len(self.data):
            print("Memory access violation at " + str(address))
        else:    
            self.lastAccess = address;
            return self.data[address];
    
    def store(self, address, value):
        if address < 0 or address >= len(self.data):
            print("Memory access violation at " + str(address))
        else:
            self.lastAccess = address;
            self.data[address] = value;
    
    def reset(self):
        self.lastAccess = -1;
        for x in self.data:
            self.data[x] = 0

    def print(self):
        idx = 0
        line = ""
        

        for x in range(16):
            line = ""
            for y in range(16):
                line = line + str("{:02x}".format(self.load((x*16)+y))) + " "
            print(line)
            
    def output(self):
        line = ""
        for x in range(232,254):
            line = line + chr(self.data[x])
        print(line)
