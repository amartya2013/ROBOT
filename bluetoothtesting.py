from machine import UART, Pin

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

buffer = bytearray()

while True:
    if uart.any():
        buffer += uart.read()

        # Keep processing while we have enough data
        while len(buffer) >= 8:

            # Find start byte
            if buffer[0] == 0xFF:
                packet = buffer[:8]
                buffer = buffer[8:]

                # Decode joystick

                if packet[6] == 1:
                    print('forward')
                if packet[6] == 4:
                    print('left')
                if packet[6] == 2:
                    print('backward')
                if packet[6] == 8:
                    print('right')
                if packet[5] == 4:
                    print('triange')
                if packet[5] == 8:
                    print('circle')
                if packet[5] == 16:
                    print('x')
                if packet[5] == 32:
                    print('square')
