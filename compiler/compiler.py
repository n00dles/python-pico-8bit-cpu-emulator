import re   

class Compile:
    
    def __init__(self):
        regex = "^[\t ]*(?:([.A-Za-z]\w*)[:])?(?:[\t ]*([A-Za-z]{2,4})(?:[\t ]+(\[(\w+((\+|-)\d+)?)\]|\".+?\"|\'.+?\'|[.A-Za-z0-9]\w*)(?:[\t ]*[,][\t ]*(\[(\w+((\+|-)\d+)?)\]|\".+?\"|\'.+?\'|[.A-Za-z0-9]\w*))?)?)?"
        
        # Regex group indexes for operands
        op1_group = 3
        op2_group = 7

        # MATCHES: "(+|-)INTEGER"
        regexNum = "^[-+]?[0-9]+$"
        # MATCHES: "(.L)abel"
        regexLabel = "^[.A-Za-z]\w*$"
        # Contains the program code & data generated by the assembler
        code = []
        # Contains the mapping from instructions to assembler line
        mapping = {}
        # Hash map of label used to replace the labels after the assembler generated the code
        labels = {}
        # Hash of uppercase labels used to detect duplicates
        normalizedLabels = {}

        # Split text into code lines
        #lines = input.split('\n')
        
        s = "      MOV A, 0x54"
        match = self.exec(regex,s)
        print(match)

    def parseNumber(self,input):
        if input[0:2] == "0x":
            return int(input[2:], 16)
        elif  input[0:2] == "0o":
            return int(input[2:], 8);
        elif  input[len(input) - 1] == "b":
            return int(input[0: len(input) - 1], 2)
        elif  input[len(input) - 1] == "d":
            return int(input[0:len(input) - 1], 10)
        elif self.exec(self.regexNum, input):
            return int(input, 10)
        else:
            print("Invalid number format")

    def parseRegister(self,input):
        input = input.upper()

        if input == 'A':
            return 0
        elif (input == 'B'):
            return 1
        elif (input == 'C'):
            return 2
        elif (input == 'D'):
            return 3
        elif (input == 'SP'):
            return 4
        else:
            return None

    def exec(self,regex, s):
        m = re.search(regex, s)
        if m:
            return [s for s in m.groups()]


c = Compile()
print(c.parseNumber("43d"))