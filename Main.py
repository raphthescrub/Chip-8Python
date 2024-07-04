from cleanEMU import CPU
import pygame

cpu = CPU()
cpu.LoadROM()  # Example ROM

# Simulate fetch-decode-execute cycle
while True:  # Execute 3 instructions for example
    cpu.Execute()