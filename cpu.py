import math
from  opcodes import opcodes
from bus import Bus
from time import sleep

class Cpu:

    def __init__(self, memory):
        self.maxSP = 231
        self.minSP = 0
        self.gpr = [0, 0, 0, 0]
        self.sp = self.maxSP
        self.ip = 0
        self.zero = False
        self.carry = False
        self.fault = False
        self.memory = memory
        self.debug = False
        self.bus = Bus()

    def print(self):
        print("IP : %02x, SP : %02x" % (self.ip, self.sp))
        print("A  : %02x, B  : %02x, C  : %02x, D  : %02x" % (self.gpr[0],self.gpr[1],self.gpr[2], self.gpr[3]))
        
    def registerMap(self):
        return """\
  +------+   +-+-+-+
 A| 0x%02X |   |Z|C|F|
 B| 0x%02X |   |%1d|%1d|%1d|
 C| 0x%02X |   +-+-+-+
 D| 0x%02X |
  +------+  
IP| 0x%02X |
SP| 0x%02X |  
  +------+ 
""" % (self.gpr[0],self.gpr[1],self.zero, self.carry, self.fault,self.gpr[2],self.gpr[3],self.ip, self.sp)


    def checkGPR(self, reg):
        if reg < 0 or reg >= len(self.gpr):
            print("Invalid register: " + str(reg) + " at IP " + str(self.ip))
        else:
            return reg

    def checkGPR_SP(self, reg):
        if reg < 0 or reg >= 1 + len(self.gpr):
            print("Invalid register: " + str(reg) + " at IP " + str(self.ip))
        else:
            return reg

    def setGPR_SP(self,reg,value):
        if reg >= 0 and reg < len(self.gpr):
            self.gpr[reg] = value
        elif reg == len(self.gpr):
            self.sp = value

            ## Not likely to happen, since we always get here after checkOpertion().
            if (self.sp < self.minSP):
                print("Stack overflow")
            elif self.sp > self.maxSP:
                print("Stack underflow")
        else: 
            print("Invalid register: " + str(reg) + " at IP " + str(self.ip))

    
    def getGPR_SP(self,reg):
        if reg >= 0 and reg < len(self.gpr):
            return self.gpr[reg]
        elif reg == len(self.gpr):
            return self.sp
        else:
            print("Invalid register: " + str(reg) + " at IP " + str(self.ip))

    def indirectRegisterAddress(self, value):
        reg = value % 8
        
        base = 0
        if reg < len(self.gpr):
            base = self.gpr[reg]
        else:
            base = self.sp
        
        offset = math.floor(value / 8)
        if offset > 15:
            offset = offset - 32
        
        return base+offset

    def checkOperation(self,value):
        self.zero = False
        self.carry = False

        if value >= 256:
            self.carry = True
            value = value % 256
        elif value == 0:
            self.zero = True
        elif value < 0:
            self.carry = True
            value = 256 - (-value) % 256
        return value

    def jump(self,newIP):
        if newIP < 0 or newIP >= len(self.memory.data):
            print("IP outside memory")
        else:
            self.ip = newIP

    def push(self,value):
        self.sp -= 1
        self.memory.store(self.sp, value)
        if self.sp < self.minSP:
            print("Stack overflow")
        

    def pop(self):
        self.sp += 1
        value = self.memory.load(self.sp)
        
        if self.sp > self.maxSP:
            print("Stack underflow")
        return value

    def division(self,divisor):
        if divisor == 0:
            print("Division by 0")

        return math.floor(self.gpr[0] / divisor)

    def getIP(self):
        return self.ip

    def cycle(self):
        if self.ip < 0 or self.ip >= len(self.memory.data):
            print("Instruction pointer is outside of memory")
        
        regTo = 0  
        regFrom = 0 
        memFrom = 0
        memTo = 0
        number = 0
        instr = self.memory.load(self.ip)
        self.bus.dataBus(instr)
        print(instr)
        sleep(1)
        if self.debug:
            print("-1: %02x, 0: %02x, +1: %02x, +2: %02x " % (self.memory.data[self.ip-1],self.memory.data[self.ip],self.memory.data[self.ip+1],self.memory.data[self.ip+2]))
        if instr == opcodes["NONE"]:
            return False # Abort step
        elif instr==opcodes["MOV_REG_TO_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.checkGPR_SP(self.memory.load(self.ip))
            self.setGPR_SP(regTo,self.getGPR_SP(regFrom))
            self.ip += 1

        elif instr==opcodes["MOV_ADDRESS_TO_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip+1))
            self.ip += 1
            memFrom = self.memory.load(self.ip+1)
            self.setGPR_SP(regTo,self.memory.load(memFrom))
            self.ip += 1
            
        elif instr==opcodes["MOV_REGADDRESS_TO_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.memory.load(self.ip)
            self.setGPR_SP(regTo,self.memory.load(self.indirectRegisterAddress(regFrom)))
            self.ip += 1
            
        elif instr==opcodes["MOV_REG_TO_ADDRESS"]:
            self.ip += 1
            memTo = self.memory.load(self.ip)
            self.ip += 1
            regFrom = self.checkGPR_SP(self.memory.load(self.ip))
            self.memory.store(memTo, self.getGPR_SP(regFrom))
            self.ip += 1
            
        elif instr==opcodes["MOV_REG_TO_REGADDRESS"]:
            self.ip += 1
            regTo = self.memory.load(self.ip)
            self.ip += 1
            regFrom = self.checkGPR_SP(self.memory.load(self.ip))
            self.memory.store(self.indirectRegisterAddress(regTo), self.getGPR_SP(regFrom))
            self.ip += 1
            
        elif instr==opcodes["MOV_NUMBER_TO_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            number = self.memory.load(self.ip)
            self.setGPR_SP(regTo,number)
            self.ip += 1
            
        elif instr==opcodes["MOV_NUMBER_TO_ADDRESS"]:
            self.ip += 1
            memTo = self.memory.load(self.ip)
            self.ip += 1
            number = self.memory.load(self.ip)
            self.memory.store(memTo, number)
            self.ip += 1
            
        elif instr==opcodes["MOV_NUMBER_TO_REGADDRESS"]:
            self.ip += 1
            regTo = self.memory.load(self.ip)
            self.ip += 1
            number = self.memory.load(self.ip)
            self.memory.store(self.indirectRegisterAddress(regTo), number)
            self.ip += 1
            
        elif instr==opcodes["ADD_REG_TO_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.checkGPR_SP(self.memory.load(self.ip))
            self.setGPR_SP(regTo,self.checkOperation(self.getGPR_SP(regTo) + self.getGPR_SP(regFrom)))
            self.ip += 1
            
        elif instr==opcodes["ADD_REGADDRESS_TO_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.memory.load(self.ip)
            self.setGPR_SP(regTo,self.checkOperation(self.getGPR_SP(regTo) + self.memory.load(self.indirectRegisterAddress(regFrom))))
            self.ip += 1
            
        elif instr==opcodes["ADD_ADDRESS_TO_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            memFrom = self.memory.load(self.ip)
            self.setGPR_SP(regTo,self.checkOperation(self.getGPR_SP(regTo) + self.memory.load(memFrom)))
            self.ip += 1
            
        elif instr==opcodes["ADD_NUMBER_TO_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            number = self.memory.load(self.ip)
            self.setGPR_SP(regTo,self.checkOperation(self.getGPR_SP(regTo) + number))
            self.ip += 1
            
        elif instr==opcodes["SUB_REG_FROM_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.checkGPR_SP(self.memory.load(self.ip))
            self.setGPR_SP(regTo,self.checkOperation(self.getGPR_SP(regTo) - self.gpr[regFrom]))
            self.ip += 1
            
        elif instr==opcodes["SUB_REGADDRESS_FROM_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.memory.load(self.ip)
            self.setGPR_SP(regTo,self.checkOperation(self.getGPR_SP(regTo) - self.memory.load(self.indirectRegisterAddress(regFrom))))
            self.ip += 1
            
        elif instr==opcodes["SUB_ADDRESS_FROM_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            memFrom = self.memory.load(self.ip)
            self.setGPR_SP(regTo,self.checkOperation(self.getGPR_SP(regTo) - self.memory.load(memFrom)))
            self.ip += 1
            
        elif instr==opcodes["SUB_NUMBER_FROM_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            number = self.memory.load(self.ip)
            self.setGPR_SP(regTo,self.checkOperation(self.getGPR_SP(regTo) - number))
            self.ip += 1
            
        elif instr==opcodes["INC_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.setGPR_SP(regTo,self.checkOperation(self.getGPR_SP(regTo) + 1))
            self.ip += 1
            
        elif instr==opcodes["DEC_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.setGPR_SP(regTo,self.checkOperation(self.getGPR_SP(regTo) - 1))
            self.ip += 1
            
        elif instr==opcodes["CMP_REG_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.checkGPR_SP(self.memory.load(self.ip))
            self.checkOperation(self.getGPR_SP(regTo) - self.getGPR_SP(regFrom))
            self.ip += 1
            
        elif instr==opcodes["CMP_REGADDRESS_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.memory.load(self.ip)
            self.checkOperation(self.getGPR_SP(regTo) - self.memory.load(self.indirectRegisterAddress(regFrom)))
            self.ip += 1
            
        elif instr==opcodes["CMP_ADDRESS_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            memFrom = self.memory.load(self.ip)
            self.checkOperation(self.getGPR_SP(regTo) - self.memory.load(memFrom))
            self.ip += 1
            
        elif instr==opcodes["CMP_NUMBER_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR_SP(self.memory.load(self.ip))
            self.ip += 1
            number = self.memory.load(self.ip)
            self.checkOperation(self.getGPR_SP(regTo) - number)
            self.ip += 1
            
        elif instr==opcodes["JMP_REGADDRESS"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.jump(self.gpr[regTo])
            
        elif instr==opcodes["JMP_ADDRESS"]:
            self.ip += 1
            number = self.memory.load(self.ip)
        
            self.jump(number)
            
        elif instr==opcodes["JC_REGADDRESS"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            if self.carry:
                self.jump(self.gpr[regTo])
            else:
                self.ip += 1
            
            
        elif instr==opcodes["JC_ADDRESS"]:
            self.ip += 1
            number = self.memory.load(self.ip)
            if self.carry:
                self.jump(number)
            else:
                self.ip += 1
            
            
        elif instr==opcodes["JNC_REGADDRESS"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            if not self.carry:
                self.jump(self.gpr[regTo])
            else:
                self.ip += 1
            
        elif instr==opcodes["JNC_ADDRESS"]:
            self.ip += 1
            number = self.memory.load(self.ip)
            if not self.carry:
                self.jump(number)
            else:
                self.ip += 1
            
        elif instr==opcodes["JZ_REGADDRESS"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            if self.zero:
                self.jump(self.gpr[regTo])
            else:
                self.ip += 1
            
        elif instr==opcodes["JZ_ADDRESS"]:
            self.ip += 1
            number = self.memory.load(self.ip)
            if self.zero:
                self.jump(number)
            else:
                self.ip += 1
            
        elif instr==opcodes["JNZ_REGADDRESS"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            if not self.zero:
                self.jump(self.gpr[regTo])
            else:
                self.ip += 1
            
        elif instr==opcodes["JNZ_ADDRESS"]:
            self.ip += 1
            number = self.memory.load(self.ip)
            if not self.zero:
                self.jump(number)
            else:
                self.ip += 1
            
        elif instr==opcodes["JA_REGADDRESS"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            if not self.zero and not self.carry:
                self.jump(self.gpr[regTo])
            else:
                self.ip += 1
            
            
        elif instr==opcodes["JA_ADDRESS"]:
            self.ip += 1
            number = self.memory.load(self.ip)
            if not self.zero and not self.carry:
                self.jump(number)
            else:
                self.ip += 1
            
            
        elif instr==opcodes["JNA_REGADDRESS"]: # JNA REG
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            if self.zero or self.carry:
                self.jump(self.gpr[regTo])
            else:
                self.ip += 1
            
            
        elif instr==opcodes["JNA_ADDRESS"]:
            self.ip += 1
            number = self.memory.load(self.ip)
            if self.zero or self.carry:
                self.jump(number)
            else:
                self.ip += 1
            
            
        elif instr==opcodes["PUSH_REG"]:
            self.ip += 1
            regFrom = self.checkGPR(self.memory.load(self.ip))
            self.push(self.gpr[regFrom])
            self.ip += 1
            
        elif instr==opcodes["PUSH_REGADDRESS"]:
            self.ip += 1
            regFrom = self.memory.load(self.ip)
            self.push(self.memory.load(self.indirectRegisterAddress(regFrom)))
            self.ip += 1
            
        elif instr==opcodes["PUSH_ADDRESS"]:
            self.ip += 1
            memFrom = self.memory.load(self.ip)
            self.push(self.memory.load(memFrom))
            self.ip += 1
            
        elif instr==opcodes["PUSH_NUMBER"]:
            self.ip += 1
            number = self.memory.load(self.ip)
            self.push(number)
            self.ip += 1
            
        elif instr==opcodes["POP_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.gpr[regTo] = self.pop()
            self.ip += 1
            
        elif instr==opcodes["CALL_REGADDRESS"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.push(self.ip+1)
            self.jump(self.gpr[regTo])
            
        elif instr==opcodes["CALL_ADDRESS"]:
            self.ip += 1
            number = self.memory.load(self.ip)
            self.push(self.ip)
            self.jump(number)
            
        elif instr==opcodes["RET"]:
            self.jump(self.pop())
            
        elif instr==opcodes["MUL_REG"]: # A = A * REG
            self.ip += 1
            regFrom = self.checkGPR(self.memory.load(self.ip))
            self.gpr[0] = self.checkOperation(self.gpr[0] * self.gpr[regFrom])
            self.ip += 1
            
        elif instr==opcodes["MUL_REGADDRESS"]: # A = A * [REG]
            self.ip += 1
            regFrom = self.memory.load(self.ip)
            self.gpr[0] = self.checkOperation(self.gpr[0] * self.memory.load(self.indirectRegisterAddress(regFrom)))
            self.ip += 1
            
        elif instr==opcodes["MUL_ADDRESS"]: # A = A * [NUMBER]
            self.ip += 1
            memFrom = self.memory.load(self.ip)
            self.gpr[0] = self.checkOperation(self.gpr[0] * self.memory.load(memFrom))
            self.ip += 1
            
        elif instr==opcodes["MUL_NUMBER"]: # A = A * NUMBER
            self.ip += 1
            number = self.memory.load(self.ip)
            self.gpr[0] = self.checkOperation(self.gpr[0] * number)
            self.ip += 1
            
        elif instr==opcodes["DIV_REG"]: # A = A / REG
            self.ip += 1
            regFrom = self.checkGPR(self.memory.load(self.ip))
            self.gpr[0] = self.checkOperation(self.division(self.gpr[regFrom]))
            self.ip += 1
            
        elif instr==opcodes["DIV_REGADDRESS"]: # A = A / [REG]
            self.ip += 1
            regFrom = self.memory.load(self.ip)
            self.gpr[0] = self.checkOperation(self.division(self.memory.load(self.indirectRegisterAddress(regFrom))))
            self.ip += 1
            
        elif instr==opcodes["DIV_ADDRESS"]: # A = A / [NUMBER]
            self.ip += 1
            memFrom = self.memory.load(self.ip)
            self.gpr[0] = self.checkOperation(self.division(self.memory.load(memFrom)))
            self.ip += 1
            
        elif instr==opcodes["DIV_NUMBER"]: # A = A / NUMBER
            self.ip += 1
            number = self.memory.load(self.ip)
            self.gpr[0] = self.checkOperation(self.division(number))
            self.ip += 1
            
        elif instr==opcodes["AND_REG_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.checkGPR(self.memory.load(self.ip))
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] & self.gpr[regFrom])
            self.ip += 1
            
        elif instr==opcodes["AND_REGADDRESS_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] & self.memory.load(self.indirectRegisterAddress(regFrom)))
            self.ip += 1
            
        elif instr==opcodes["AND_ADDRESS_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            memFrom = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] & self.memory.load(memFrom))
            self.ip += 1
            
        elif instr==opcodes["AND_NUMBER_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            number = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] & number)
            self.ip += 1
            
        elif instr==opcodes["OR_REG_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.checkGPR(self.memory.load(self.ip))
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] | self.gpr[regFrom])
            self.ip += 1
            
        elif instr==opcodes["OR_REGADDRESS_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] | self.memory.load(self.indirectRegisterAddress(regFrom)))
            self.ip += 1
            
        elif instr==opcodes["OR_ADDRESS_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            memFrom = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] | self.memory.load(memFrom))
            self.ip += 1
            
        elif instr==opcodes["OR_NUMBER_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            number = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] | number)
            self.ip += 1
            
        elif instr==opcodes["XOR_REG_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.checkGPR(self.memory.load(self.ip))
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] ^ self.gpr[regFrom])
            self.ip += 1
            
        elif instr==opcodes["XOR_REGADDRESS_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] ^ self.memory.load(self.indirectRegisterAddress(regFrom)))
            self.ip += 1
            
        elif instr==opcodes["XOR_ADDRESS_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            memFrom = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] ^ self.memory.load(memFrom))
            self.ip += 1
            
        elif instr==opcodes["XOR_NUMBER_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            number = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] ^ number)
            self.ip += 1
            
        elif instr==opcodes["NOT_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.gpr[regTo] = self.checkOperation(~self.gpr[regTo])
            self.ip += 1
            
        elif instr==opcodes["SHL_REG_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.checkGPR(self.memory.load(self.ip))
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] << self.gpr[regFrom])
            self.ip += 1
            
        elif instr==opcodes["SHL_REGADDRESS_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] << self.memory.load(self.indirectRegisterAddress(regFrom)))
            self.ip += 1
            
        elif instr==opcodes["SHL_ADDRESS_WITH_REG"]:
            regTo = self.checkGPR(self.memory.load(self.ip))
            memFrom = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] << self.memory.load(memFrom))
            self.ip += 1
            
        elif instr==opcodes["SHL_NUMBER_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            number = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] << number)
            self.ip += 1
            
        elif instr==opcodes["SHR_REG_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.checkGPR(self.memory.load(self.ip))
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] >> self.gpr[regFrom])
            self.ip += 1
            
        elif instr==opcodes["SHR_REGADDRESS_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            regFrom = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] >> self.memory.load(self.indirectRegisterAddress(regFrom)))
            self.ip += 1
            
        elif instr==opcodes["SHR_ADDRESS_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            memFrom = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] >> self.memory.load(memFrom))
            self.ip += 1
            
        elif instr==opcodes["SHR_NUMBER_WITH_REG"]:
            self.ip += 1
            regTo = self.checkGPR(self.memory.load(self.ip))
            self.ip += 1
            number = self.memory.load(self.ip)
            self.gpr[regTo] = self.checkOperation(self.gpr[regTo] >> number)
            self.ip += 1
            
        else:
            print("Invalid op code: " + str(instr))
        if self.debug:
            self.print()
        if self.debug:
            print("Intrs: " + str("{:02x}".format(instr)))
    
