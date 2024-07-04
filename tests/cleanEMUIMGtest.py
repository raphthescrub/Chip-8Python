import math
import time
import pygame
# Constants for screen dimensions and Chip-8 display
#Dimensions


class CPU:
    def __init__(self):
        print("Emulator Started")
        self.Vregisters = [0]*16  # 16 general-purpose 8-bit registers (V0-VF)
        #Where Font/Sprite Data Starts
        self.Iregister = 0  # Index Register (12-bit addressable)
        self.memory = [0] * 4096  # 4KB memory
        self.Stack = []  # Stack for subroutine calls
        self.font = [0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
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
        #start pc right after font set
        self.PC = len(self.font) + 1 # Program Counter (12-bit addressable)
        #self.PC = 0
        #Store the fonts in memory for later use 
        #for i in range(len(self.font)):
        #    self.memory[i] = self.font[i]
        self.DelayTimer = 0  # 8-bit delay timer
        self.SoundTimer = 0  # 8-bit sound timer
        #Information For Screen
        self.ScreenW = 64 #columns 
        self.ScreenH = 32 #Rows
        self.Screen = [[0 for _ in range(self.ScreenW)] for _ in range(self.ScreenH)]
        #Matrix for Screen Pixels
        #Make the Pixels hashes #
    def Decode(self):
        #print("Decoding")
        Nibble1, Nibble2 = self.Fetch()
        opcode = (Nibble1 << 8) + Nibble2
        Nibs = [(opcode & 0xF000) >> 12,
                (opcode & 0x0F00) >> 8,
                (opcode & 0x00F0) >> 4,
                (opcode & 0x000F)]
        print(hex(opcode))

        if Nibs[0] == 0x1:  # 1NNN: Jump to address NNN
            self.PC = (Nibs[1] << 8) + (Nibs[2] << 4) + Nibs[3]
            print(f"Jumping to address {self.PC}")
        elif Nibs[0] == 0x0 and Nibs[3] == 0xE:  # 00EE: Return from subroutine
            self.PC = self.Stack.pop()
            print(f"Popped: {self.PC}")
        elif Nibs[0] == 0x0 and Nibs[3] == 0x0:  # 00E0: Clear Screen
            #print("Clear")
            for row in self.Screen:
                for col in range(len(row)):
                    row[col] =  0
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
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[1]] >> 1
                if self.Vregisters[Nibs[1]] & 0b00000001:
                    self.Vregisters[15] = 0x01
                    #carry
            elif Nibs[3] == 0x7:  # 8XY7: Set VX to VY - VX
                print("Minus")
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[2]] - self.Vregisters[Nibs[1]]
            elif Nibs[3] == 0xE:  # 8XYE: Shift VX left by 1
                print("Shift left")
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[1]] << 1
                #Carry
        elif Nibs[0] == 0x9:  # 9XY0: Skip next instruction if VX does not equal VY
            print("Skipping")
            if(self.Vregisters[Nibs[1]] != self.Vregisters[Nibs[2]]):
                self.PC = self.PC + 1
        elif Nibs[0] == 0xA:  # ANNN: Set I register to address NNN
            print("Setting I Register")
            IregisterPos = (Nibs[1] << 8) + (Nibs[2] << 4) + Nibs[3]
            print("I reg pos" + str(IregisterPos) )
            self.Iregister = IregisterPos
        elif Nibs[0] == 0xC:  # CXNN: Set VX to a random number masked by NN
            print("Random number")
            CAP = (Nibs[1] << 4) + Nibs[0]
            RandN = math.random(0, CAP)
            self.Vregisters[Nibs[1]] = RandN
        
        elif Nibs[0] == 0xD:  # DXYN: Draw sprite at (VX, VY) with width 8 pixels and height N pixels
            print("Drawing")
            Xpos = self.Vregisters[Nibs[1]] & 63  # Cap X coordinate at 63
            Ypos = self.Vregisters[Nibs[2]] & 32  # Cap Y coordinate at 32
            height = Nibs[3]
            self.Vregisters[15] = 0  # Collision detection (VF)
            #8 pixel wide sprites
            #Iterate through each sprite row (height)
            for Spriterow in range(height):
            #iterate for each bit in sprite row(spirte row data = Memory[INdex + spriteRow])
                spriterowdata = self.memory[self.Iregister + Spriterow]
                for spriteBit in range(8):
                    spritePixel = (spriterowdata and (0b1 << 7 - spriteBit))
                    #if high
                    if(spritePixel == 0b1):
                        #draw if on screen if(xpos + spriteBit<screenwisth and yPos)
                        if((Xpos + spriteBit) < 63 and (Ypos + Spriterow) < 32):
                            if(self.Screen[Xpos][Ypos] == "#"):
                                #Conflict
                                self.Screen[Xpos][Ypos] = ""
                                self.Vregisters[15] = 1
                            else:
                                self.Screen[Xpos][Ypos] = "#"
            self.DrawScreen()
    def Fetch(self):
        print("Fetching")
        Nibble1 = self.memory[self.PC]
        Nibble2 = self.memory[self.PC + 1]
        self.PC += 2
        return Nibble1, Nibble2
    def DrawScreen(self):
        print(self.Screen)
    def Execute(self):
        print("Executing")
        self.Decode()

    def LoadROM(self):
        #self.memory.append(self.font)
        with open("roms/C8Logo.ch8", 'rb') as f:
            rom_data = f.read()
        start_address = self.PC # CHIP-8 programs start at address 0x200
        print(enumerate(rom_data))
        for i, byte in enumerate(rom_data):
            self.memory[start_address + i] = byte
            #=print(hex(byte))
        print("Firtst Byte is " + str(self.memory[self.PC]))

    def LoadROM2(self):
        #ADD the font set
        start_address = len(self.font)
        for i,byte in enumerate(self.font):
            self.memory[i]= byte
        Instructions = [0xA0,0x00, 0x60, 0x10, 0x61, 0x10, 0xD0, 0x15]
        for i,byte in enumerate(Instructions):
            self.memory[i + start_address]= byte
        print(hex(self.memory[start_address]))

    def LoadROM3(self):
        #ADD the font set
        Instructions = [0xA0,0x08, 0x60, 0x10, 0x61, 0x10, 0xD0, 0x15,  0xF0, 0x90, 0x90, 0x90, 0xF0, 0x00, 0x00, 0x00]   
        self.memory = Instructions