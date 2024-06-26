
#What does a cpu have 
#Registers[V]
#RAM
#STACK
import math
class CPU:
    #1byte is 8bits
    #AB in hexadecimal is a 16 bit number

    #Whats in a cpu:
    #4KB RAM
    #64 x 32 display(could use pygame or something)
    #Program Counter(PC)
    #16 Bit register I
    #Stack for 16 bit registers(used to call subroutines)
    #8 bit delay timer
    #8 bit sound timer

    #WE want every instruction to be in bytes
    def __init__(self):
        #VF is the final register or the flag register
        print("Emulator Started")
        #Registers(Hexidecimal for 0 to F)
        self.Vregisters = [0]* 16 
        Vregisters = self.Vregisters
        #Program Counters
        self.PC = 0 #Can only address 12 bits
        PC = self.PC
        #Memory instructions
        #Points to Location in Memory
        self.Iregister = 0 #Can only address 12 bits
        Iregister = self.Iregister
        #4096 spaces for bytes
        self.memory = 4096 * [0]
        memory = self.memory
        self.Stack = []
        Stack = self.Stack
        self.font = [] #Array is online you konw man
        font = self.font
        self.DelayTimer = 0
        DelayTimer = self.DelayTimer
        self.SoundTimer = 0
        SoundTimer = self.SoundTimer
        #Keypad

    def Decode(self):
        print("Decoding")
        #Hex example is 0x45
        #nibs is an array of two bytes 
        Nibble1,Nibble2= self.Fetch()
        #GEts instructions into one code by shift 2 bytes an adding nibble 2 insructs
        print(hex(Nibble1))
        print(hex(Nibble2))
        opcode = (Nibble1 << 8) + (Nibble2)
        #isolates each value into a hexidecimal 
        Nibs = [(opcode & 0xF000) >> 12,
                 (opcode & 0x0F00) >> 8, 
                 (opcode & 0x00F0) >> 4, 
                 (opcode & 0x000F)]
        print(hex(opcode))
        print(Nibs)
        #when the first element of the first byte is 1
        #Jump Instruction
        if(Nibs[0] == 0x1):
            self.PC = int((Nibs[1] <<8 ) + (Nibs[2] << 4 ) + (Nibs[3]))
            print("Jumping to address" + str(self.PC))
        #Return Back
        elif(Nibs[0] == 0x0):
        #Call routine at NNN
            if(Nibs[3] == 0xE):
                #Moves the program counter to the value saved to the stack
                self.PC = self.Stack.pop()
                print("Popped: " + self.PC)
        #CMD 2NNN
        elif(Nibs[0] == 0x2):
            print("Subroutine call")
            #puts the current program counter on the stack to return to for functions
            #append is added to stack
            self.Stack.append(self.PC)
            self.PC = int((Nibs[1] <<8 ) + (Nibs[2] << 4 ) + (Nibs[3]))
        #IF EQUAL Statment
        #Skips next instruction if VX is equal to NN
        #CMD 3xNN
        elif(Nibs[0] == 0x3):
            print("If EQ STATMENT")
            NN = (Nibs[2] << 4) + Nibs[3]
            if(self.Vregisters[Nibs[1]] == NN ):
                #Skips instruction
                self.PC = self.PC +1
        #skips instrctuion if VX is not equal
        #4XNN
        elif(Nibs[0] == 0x4):
            print("If Not EQ statement")
            NN = (Nibs[2] << 4) + Nibs[3]
            if(self.Vregisters[Nibs[1]] != NN ):
                #Skips instruction
                self.PC = self.PC +1
        #Skip instruction if Vx = Vy
        #CMD 5XY0
        elif(Nibs[0] == 0x5):
            print("Register Compare")
        #SET
        elif(Nibs[0] == 0x6):
            #CMD = 6XNN
            #No Carry
            #ADD NN to register X
            #make VX in instruction equal to six
            #The second element of the Nib
            print("SET Register")
            print(Nibs[2])
            print(Nibs[3])
            self.Vregisters[Nibs[1]] = Nibs[2]<<4 or Nibs[3] <<2
            print(self.Vregisters)
        #ADD Value to Register
        elif(Nibs[0] == 0x7):
                #ADDVal
                #Turn nib into int and convert to binary
                #7XNN ADD NN to register Vx
                print("ADD Register")
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[1]] + ((Nibs[2] << 4) + (Nibs[3]))
                print(self.Vregisters)
        #Commands starting in 8: A little complex but can do it
        elif(Nibs[0] == 0x8):
            #Bit Operations
            #Vx = Vy
            #CMD 8xy0
            if(Nibs[3] == 0x0):
                #Set Vx to Vy
                print("Vx set to VY")
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[2]]
            #Vx = Vx or Vy
            #CMD 8xy1
            elif(Nibs[3] == 0x1):
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[1]] + self.Vregisters[Nibs[2]]  
                print("Vx or Vy")
            #Vx = Vx and Vy
            #CMD 8xy2
            elif(Nibs[3] == 0x2):
                print("Vx and Vy")
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[1]] and self.Vregisters[Nibs[2]]  
            #Vx = Vx xor Vy
            #CMD 8XY3
            elif(Nibs[3] == 0x3):
                print("Xor")
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[1]] ** self.Vregisters[Nibs[2]]
            #Vx+=Vy
            #CMD 8xy4
            #carry
            elif(Nibs[3]== 0x4):
                print("Add with carry")
            #Vx-=Vy
            #CMD 8xy5
            #carry
            elif(Nibs[3]== 0x5):
                print("minus")
            #set vx to vy
            #Shift Vx by 1
            #CMD 8xy6
            #carry
            elif(Nibs[3]== 0x6):
                print("shift right")
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[2]]
                if(self.Vregisters[Nibs[1]] and 0b00000001):
                    #makes flag register final register equal to 1
                    self.Vregisters[self.Vregisters.length - 1] = 0x01
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[1]] >> 1
            #VY - Vx
            #CMD 8x7
            #carry
            elif(Nibs[3]== 0x7):
                print("minus")
            #shift Vs to left by 1
            #sets Vf to 1 if most significant bit of Vx
            elif(Nibs[3] == 0xE):
                print("Shift left")
        #Skip instruction if Vx not Vy
        elif(Nibs[0] == 0x9):
            print("Skipping")
        #SET I register
        elif(Nibs[0] == 0xA):
            print("Setting I Register")
            self.Iregister = (Nibs[1] << 8) + (Nibs[2] << 4) + (Nibs[3])
            print(self.Iregister)
        #CXNN 
        #Makes Register Equal to a rand num
        #The rand num generator will binary and with the given NN
        elif(Nibs[0] == 0xC):
            #RANDOM.RANDRANGE
            CAP = Nibs[1] << 4 + Nibs[0]
            RandN = math.random(0, int(CAP))
            self.Vregisters[Nibs[1]] = RandN

        #CMD DXYN
        #
        elif(Nibs[0] == 0xD):
            print("Drawing")
            #Draw N pixel tall sprite
            #From memory location that i index register is hold to screen
            #if pixel set off flag register is 1 
            #Fetch X and Y value from VX and VY
            #Do this
            #Use Pygame ot put it on there
            Xcord = Nibs[1] and 63 #Creates a cap at 63
            Ycord = Nibs[2] and 32 # Creates a cap at 32
            #Flag Register 0
            self.Vregisters[15] = 0
            
    def Fetch(self):
        print("Fetching")
        #Read instruction PC is pointing to in memory
        #Get variable that points to instruction
        #byte1
        Nibble1 = self.memory[self.PC]
        #byte2
        Nibble2 = self.memory[self.PC + 1]
        self.PC = self.PC + 2
        return Nibble1, Nibble2
    def Execute(self):
        print("Executing")
        #Implement whatever it says I gues
        self.Decode()
    def LoadROM(self):
        self.memory = [0x65,0xAC,0x75,0x03,0xA9,0xBC, 0x10, 0x00]
        print("LoadingRom")
        #Making the memory instructions to be anything
    