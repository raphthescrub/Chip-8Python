import math

# Constants for screen dimensions and Chip-8 display
#Dimensions
CHIP8_WIDTH = 64
CHIP8_HEIGHT = 32

class CPU:
    def __init__(self):
        print("Emulator Started")
        self.Vregisters = [0]*16  # 16 general-purpose 8-bit registers (V0-VF)
        self.PC = 0  # Program Counter (12-bit addressable)
        self.Iregister = 0  # Index Register (12-bit addressable)
        self.memory = [0] * 4096  # 4KB memory
        self.Stack = []  # Stack for subroutine calls
        self.font = [        0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
        0x20, 0x60, 0x20, 0x20, 0x70, # 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
        0x90, 0x90, 0xF0, 0x10, 0x10, # 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
        0xF0, 0x10, 0x20, 0x40, 0x40, # 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, # A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
        0xF0, 0x80, 0x80, 0x80, 0xF0, # C
        0xE0, 0x90, 0x90, 0x90, 0xE0, # D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
        0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]  # Font set
        #Store the fonts in memory for later use 
        #for i in range(len(self.font)):
        #    self.memory[i] = self.font[i]
        self.DelayTimer = 0  # 8-bit delay timer
        self.SoundTimer = 0  # 8-bit sound timer

    def Decode(self):
        print("Decoding")
        Nibble1, Nibble2 = self.Fetch()
        opcode = (Nibble1 << 8) + Nibble2
        Nibs = [(opcode & 0xF000) >> 12,
                (opcode & 0x0F00) >> 8,
                (opcode & 0x00F0) >> 4,
                (opcode & 0x000F)]
        print(hex(opcode))
        print(Nibs)

        if Nibs[0] == 0x1:  # 1NNN: Jump to address NNN
            self.PC = (Nibs[1] << 8) + (Nibs[2] << 4) + Nibs[3]
            print(f"Jumping to address {self.PC}")
        elif Nibs[0] == 0x0 and Nibs[3] == 0xE:  # 00EE: Return from subroutine
            self.PC = self.Stack.pop()
            print(f"Popped: {self.PC}")
        elif Nibs[0] == 0x2:  # 2NNN: Call subroutine at NNN
            print("Subroutine call")
            self.Stack.append(self.PC)
            self.PC = (Nibs[1] << 8) + (Nibs[2] << 4) + Nibs[3]
        elif Nibs[0] == 0x3:  # 3XNN: Skip next instruction if VX equals NN
            print("If EQ statement")
            NN = (Nibs[2] << 4) + Nibs[3]
            if self.Vregisters[Nibs[1]] == NN:
                self.PC += 1
        elif Nibs[0] == 0x4:  # 4XNN: Skip next instruction if VX does not equal NN
            print("If Not EQ statement")
            NN = (Nibs[2] << 4) + Nibs[3]
            if self.Vregisters[Nibs[1]] != NN:
                self.PC += 1
        elif Nibs[0] == 0x5:  # 5XY0: Skip next instruction if VX equals VY
            print("Register Compare")
        elif Nibs[0] == 0x6:  # 6XNN: Set VX to NN
            print("SET Register")
            self.Vregisters[Nibs[1]] = (Nibs[2] << 4) + Nibs[3]
            print(self.Vregisters)
        elif Nibs[0] == 0x7:  # 7XNN: Add NN to VX
            print("ADD Register")
            self.Vregisters[Nibs[1]] += (Nibs[2] << 4) + Nibs[3]
            print(self.Vregisters)
        elif Nibs[0] == 0x8:
            if Nibs[3] == 0x0:  # 8XY0: Set VX to the value of VY
                print("Vx set to VY")
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[2]]
            elif Nibs[3] == 0x1:  # 8XY1: Set VX to VX | VY
                print("Vx or Vy")
                self.Vregisters[Nibs[1]] |= self.Vregisters[Nibs[2]]
            elif Nibs[3] == 0x2:  # 8XY2: Set VX to VX & VY
                print("Vx and Vy")
                self.Vregisters[Nibs[1]] &= self.Vregisters[Nibs[2]]
            elif Nibs[3] == 0x3:  # 8XY3: Set VX to VX ^ VY
                print("Xor")
                self.Vregisters[Nibs[1]] ^= self.Vregisters[Nibs[2]]
            elif Nibs[3] == 0x6:  # 8XY6: Shift VX right by 1
                print("Shift right")
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[2]] >> 1
                if self.Vregisters[Nibs[1]] & 0b00000001:
                    self.Vregisters[15] = 0x01
            elif Nibs[3] == 0x7:  # 8XY7: Set VX to VY - VX
                print("Minus")
            elif Nibs[3] == 0xE:  # 8XYE: Shift VX left by 1
                print("Shift left")
        elif Nibs[0] == 0x9:  # 9XY0: Skip next instruction if VX does not equal VY
            print("Skipping")
        elif Nibs[0] == 0xA:  # ANNN: Set I register to address NNN
            print("Setting I Register")
            self.Iregister = (Nibs[1] << 8) + (Nibs[2] << 4) + Nibs[3]
            print(self.Iregister)
        elif Nibs[0] == 0xC:  # CXNN: Set VX to a random number masked by NN
            print("Random number")
            CAP = (Nibs[1] << 4) + Nibs[0]
            RandN = math.random(0, CAP)
            self.Vregisters[Nibs[1]] = RandN
        elif Nibs[0] == 0xD:  # DXYN: Draw sprite at (VX, VY) with width 8 pixels and height N pixels
            print("Drawing")
            Xcord = Nibs[1] & 63  # Cap X coordinate at 63
            Ycord = Nibs[2] & 32  # Cap Y coordinate at 32
            self.Vregisters[15] = 0  # Collision detection (VF)
            
    def Fetch(self):
        print("Fetching")
        Nibble1 = self.memory[self.PC]
        Nibble2 = self.memory[self.PC + 1]
        self.PC += 2
        return Nibble1, Nibble2
    def DrawScreen():
        print("Drawing Screen")
        
    def Execute(self):
        print("Executing")
        self.Decode()

    def LoadROM(self):
        self.memory = [0x65, 0xAC, 0x75, 0x03, 0xA9, 0xBC, 0x10, 0x00]
        print("Loading ROM")
