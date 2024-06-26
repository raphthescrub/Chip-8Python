from cleanEMU import CPU

cpu = CPU()
cpu.LoadROM()  # Example ROM

# Simulate fetch-decode-execute cycle
for i in range(1000):  # Execute 3 instructions for example
    cpu.Execute()