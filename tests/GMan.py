import math
import pygame
import time

class CPU:
    def __init__(self):
        print("Emulator Started")
        self.Vregisters = [0]*16  # 16 general-purpose 8-bit registers (V0-VF)
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
        self.PC = len(self.font)  # Program Counter (start after font set)
        self.DelayTimer = 0  # 8-bit delay timer
        self.SoundTimer = 0  # 8-bit sound timer
        self.ScreenW = 64  # columns
        self.ScreenH = 32  # Rows
        self.Screen = [[' ' for _ in range(self.ScreenW)] for _ in range(self.ScreenH)]  # Initialize screen to spaces

    def Decode(self):
        Nibble1, Nibble2 = self.Fetch()
        opcode = (Nibble1 << 8) + Nibble2
        Nibs = [(opcode & 0xF000) >> 12,
                (opcode & 0x0F00) >> 8,
                (opcode & 0x00F0) >> 4,
                (opcode & 0x000F)]

        if Nibs[0] == 0x1:  # 1NNN: Jump to address NNN
            self.PC = (Nibs[1] << 8) + (Nibs[2] << 4) + Nibs[3]
            print(f"Jumping to address {self.PC}")
        elif Nibs[0] == 0x0 and Nibs[3] == 0xE:  # 00EE: Return from subroutine
            self.PC = self.Stack.pop()
            print(f"Popped: {self.PC}")
        elif Nibs[0] == 0x0 and Nibs[3] == 0x0:  # 00E0: Clear Screen
            for row in self.Screen:
                for col in range(len(row)):
                    row[col] = ' '
            print("Screen Cleared")
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
            if self.Vregisters[Nibs[1]] == self.Vregisters[Nibs[2]]:
                self.PC += 1
        elif Nibs[0] == 0x6:  # 6XNN: Set VX to NN
            print("SET Register")
            self.Vregisters[Nibs[1]] = (Nibs[2] << 4) + Nibs[3]
            print(f"V{Nibs[1]} = {self.Vregisters[Nibs[1]]}")
        elif Nibs[0] == 0x7:  # 7XNN: Add NN to VX
            print("ADD Register")
            self.Vregisters[Nibs[1]] += (Nibs[2] << 4) + Nibs[3]
            print(f"V{Nibs[1]} += {self.Vregisters[Nibs[1]]}")
        elif Nibs[0] == 0x8:
            if Nibs[3] == 0x0:  # 8XY0: Set VX to the value of VY
                print("Vx set to VY")
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[2]]
                print(f"V{Nibs[1]} = V{Nibs[2]}")
            elif Nibs[3] == 0x1:  # 8XY1: Set VX to VX | VY
                print("Vx or Vy")
                self.Vregisters[Nibs[1]] |= self.Vregisters[Nibs[2]]
                print(f"V{Nibs[1]} |= V{Nibs[2]}")
            elif Nibs[3] == 0x2:  # 8XY2: Set VX to VX & VY
                print("Vx and Vy")
                self.Vregisters[Nibs[1]] &= self.Vregisters[Nibs[2]]
                print(f"V{Nibs[1]} &= V{Nibs[2]}")
            elif Nibs[3] == 0x3:  # 8XY3: Set VX to VX ^ VY
                print("Xor")
                self.Vregisters[Nibs[1]] ^= self.Vregisters[Nibs[2]]
                print(f"V{Nibs[1]} ^= V{Nibs[2]}")
            elif Nibs[3] == 0x6:  # 8XY6: Shift VX right by 1
                print("Shift right")
                self.Vregisters[15] = self.Vregisters[Nibs[1]] & 0x1
                self.Vregisters[Nibs[1]] >>= 1
                print(f"V{Nibs[1]} >>= 1")
            elif Nibs[3] == 0x7:  # 8XY7: Set VX to VY - VX
                print("Minus")
                self.Vregisters[15] = 0 if self.Vregisters[Nibs[2]] > self.Vregisters[Nibs[1]] else 1
                self.Vregisters[Nibs[1]] = self.Vregisters[Nibs[2]] - self.Vregisters[Nibs[1]]
                print(f"V{Nibs[1]} = V{Nibs[2]} - V{Nibs[1]}")
            elif Nibs[3] == 0xE:  # 8XYE: Shift VX left by 1
                print("Shift left")
                self.Vregisters[15] = (self.Vregisters[Nibs[1]] >> 7) & 0x1
                self.Vregisters[Nibs[1]] <<= 1
                print(f"V{Nibs[1]} <<= 1")
            else:
                print(f"Unknown opcode: {opcode}")
        elif Nibs[0] == 0x9:  # 9XY0: Skip next instruction if VX does not equal VY
            print("Skip not equal")
            if self.Vregisters[Nibs[1]] != self.Vregisters[Nibs[2]]:
                self.PC += 1
        elif Nibs[0] == 0xA:  # ANNN: Set I to the address NNN
            self.Iregister = (Nibs[1] << 8) + (Nibs[2] << 4) + Nibs[3]
            print(f"I = {self.Iregister}")
        elif Nibs[0] == 0xB:  # BNNN: Jump to address NNN + V0
            self.PC = (Nibs[1] << 8) + (Nibs[2] << 4) + Nibs[3] + self.Vregisters[0]
            print(f"Jump to address V0 + {self.Iregister}")
        elif Nibs[0] == 0xC:  # CXNN: Set VX to the result of a bitwise and operation on a random number and NN
            self.Vregisters[Nibs[1]] = (Nibs[2] << 4) + Nibs[3]
            print(f"V{Nibs[1]} = Random & {(Nibs[2] << 4) + Nibs[3]}")
        elif Nibs[0] == 0xD:  # DXYN: Draw sprite at (VX, VY) with width 8 pixels and height N pixels
            Xpos = self.Vregisters[Nibs[1]] % self.ScreenW
            Ypos = self.Vregisters[Nibs[2]] % self.ScreenH
            height = Nibs[3]
            self.Vregisters[15] = 0  # Collision detection (VF)

            for sprite_row in range(height):
                sprite_data = self.memory[self.Iregister + sprite_row]
                for sprite_bit in range(8):
                    if sprite_data & (0b10000000 >> sprite_bit):
                        screen_x = (Xpos + sprite_bit) % self.ScreenW
                        screen_y = (Ypos + sprite_row) % self.ScreenH
                        if self.Screen[screen_y][screen_x] == '#':
                            self.Screen[screen_y][screen_x] = ' '  # Collision: clear pixel
                            self.Vregisters[15] = 1
                        else:
                            self.Screen[screen_y][screen_x] = '#'
            self.DrawScreen()

        elif Nibs[0] == 0xE:
            if Nibs[2] == 0x9 and Nibs[3] == 0xE:  # EX9E: Skip next instruction if key stored in VX is pressed
                key = self.Vregisters[Nibs[1]]
                # Implement key press check here
                print(f"Skip next if key in V{Nibs[1]} is pressed")
            elif Nibs[2] == 0xA and Nibs[3] == 0x1:  # EXA1: Skip next instruction if key stored in VX is not pressed
                key = self.Vregisters[Nibs[1]]
                # Implement key not pressed check here
                print(f"Skip next if key in V{Nibs[1]} is not pressed")
            else:
                print(f"Unknown opcode: {opcode}")
        elif Nibs[0] == 0xF:
            if Nibs[2] == 0x0 and Nibs[3] == 0x7:  # FX07: Set VX to the value of the delay timer
                self.Vregisters[Nibs[1]] = self.DelayTimer
                print(f"V{Nibs[1]} = Delay Timer")
            elif Nibs[2] == 0x0 and Nibs[3] == 0xA:  # FX0A: Wait for a key press, store the value of the key in VX
                key = None
                # Implement key press wait here
                self.Vregisters[Nibs[1]] = key
                print(f"Wait for key press and store in V{Nibs[1]}")
            elif Nibs[2] == 0x1 and Nibs[3] == 0x5:  # FX15: Set the delay timer to VX
                self.DelayTimer = self.Vregisters[Nibs[1]]
                print(f"Delay Timer = V{Nibs[1]}")
            elif Nibs[2] == 0x1 and Nibs[3] == 0x8:  # FX18: Set the sound timer to VX
                self.SoundTimer = self.Vregisters[Nibs[1]]
                print(f"Sound Timer = V{Nibs[1]}")
            elif Nibs[2] == 0x1 and Nibs[3] == 0xE:  # FX1E: Add VX to I
                self.Iregister += self.Vregisters[Nibs[1]]
                print(f"I += V{Nibs[1]}")
            elif Nibs[2] == 0x2 and Nibs[3] == 0x9:  # FX29: Set I to the location of the sprite for the character in VX
                self.Iregister = self.Vregisters[Nibs[1]] * 5  # Assuming each character sprite is 5 bytes
                print(f"I = Sprite location for V{Nibs[1]}")
            elif Nibs[2] == 0x3 and Nibs[3] == 0x3:  # FX33: Store the binary-coded decimal representation of VX at I, I+1, and I+2
                value = self.Vregisters[Nibs[1]]
                self.memory[self.Iregister] = value // 100
                self.memory[self.Iregister + 1] = (value // 10) % 10
                self.memory[self.Iregister + 2] = value % 10
                print(f"Store BCD of V{Nibs[1]} at I")
            elif Nibs[2] == 0x5 and Nibs[3] == 0x5:  # FX55: Store V0 to VX (including VX) in memory starting at address I
                for reg_idx in range(Nibs[1] + 1):
                    self.memory[self.Iregister + reg_idx] = self.Vregisters[reg_idx]
                print(f"Store V0 to V{Nibs[1]} in memory at I")
            elif Nibs[2] == 0x6 and Nibs[3] == 0x5:  # FX65: Fill V0 to VX (including VX) with values from memory starting at address I
                for reg_idx in range(Nibs[1] + 1):
                    self.Vregisters[reg_idx] = self.memory[self.Iregister + reg_idx]
                print(f"Fill V0 to V{Nibs[1]} with memory values starting at I")
            else:
                print(f"Unknown opcode: {opcode}")
        else:
            print(f"Unknown opcode: {opcode}")

    def Fetch(self):
        Nibble1 = self.memory[self.PC]
        Nibble2 = self.memory[self.PC + 1]
        self.PC += 2
        return Nibble1, Nibble2

    def Execute(self):
        self.Decode()

    def LoadROM2(self):
        with open("roms/IBM Logo.ch8", 'rb') as f:
            rom_data = f.read()
        start_address = self.PC  # CHIP-8 programs start at address 0x200
        for i, byte in enumerate(rom_data):
            self.memory[start_address + i] = byte

    def DrawScreen(self):
        for row in self.Screen:
            for col in row:
                print(col, end=' ')
            print()

cpu = CPU()
cpu.LoadROM2()
while True:
    cpu.Execute()
