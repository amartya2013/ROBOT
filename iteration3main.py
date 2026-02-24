from machine import Pin, PWM, UART
from time import sleep
import utime

trigger = Pin(21, Pin.OUT)
echo = Pin(20, Pin.IN)
button = Pin(14, Pin.IN, Pin.PULL_DOWN)
led1 = Pin(17, Pin.OUT)
led2 = Pin(16, Pin.OUT)
IN_1 = Pin(2, Pin.OUT)
IN_2 = Pin(3, Pin.OUT)
IN_3 = Pin(4, Pin.OUT)
IN_4 = Pin(5, Pin.OUT)
IN_5 = Pin(6, Pin.OUT)
IN_6 = Pin(7, Pin.OUT)
IN_7 = Pin(8, Pin.OUT)
IN_8 = Pin(9, Pin.OUT)
PWM_1 = PWM(Pin(10))
PWM_2 = PWM(Pin(11))
PWM_3 = PWM(Pin(12))
PWM_4 = PWM(Pin(13))

def ultra():
   trigger.low()
   utime.sleep_us(2)
   trigger.high()
   utime.sleep_us(5)
   trigger.low()
   while echo.value() == 0:
       signaloff = utime.ticks_us()
   while echo.value() == 1:
       signalon = utime.ticks_us()
       
   timepassed = signalon - signaloff
   distance = (timepassed * 0.0343) / 2
   
   
   return int(distance)




for pwm in [PWM_1, PWM_2, PWM_3, PWM_4]:
    pwm.freq(500)

# --------- MOTOR CONTROL ---------

def stop_all():
    IN_1.low(); IN_2.low()
    IN_3.low(); IN_4.low()
    IN_5.low(); IN_6.low()
    IN_7.low(); IN_8.low()



def FR_forward(speed):
    IN_1.low()
    IN_2.high()
    PWM_3.duty_u16(int(speed/ 100 * 65536))
    
    
def FR_backward(speed):
    print("gh")
    IN_1.high()
    IN_2.low()
    PWM_3.duty_u16(int(speed/ 100 * 65535))
    
    
def FL_forward(speed):
    
    IN_3.low()
    IN_4.high()
    PWM_4.duty_u16(int(speed/ 100 * 65535))
    
    
def FL_backward(speed):
    IN_3.high()
    IN_4.low()
    PWM_4.duty_u16(int(speed/ 100 * 65535))
   
    
def BR_forward(speed):
    IN_7.low()
    IN_8.high()
    PWM_2.duty_u16(int(speed/ 100 * 65535))
    
    
def BR_backward(speed):
    IN_7.high()
    IN_8.low()
    PWM_2.duty_u16(int(speed/ 100 * 65535))
    
    
def BL_forward(speed):
    IN_5.low()
    IN_6.high()
    PWM_1.duty_u16(int(speed/ 100 * 65535))
    
    
def BL_backward(speed):
    IN_5.high()
    IN_6.low()
    PWM_1.duty_u16(int(speed/ 100 * 65535))
    

# --------- MECANUM MOVEMENTS ---------

def forward(time, speed):
    print("huu")
    FL_forward(speed)
    FR_forward(speed)
    BL_forward(speed)
    BR_forward(speed)
    sleep(time)
    stop_all()

def backward(time, speed):
    FL_backward(speed)
    FR_backward(speed)
    BL_backward(speed)
    BR_backward(speed)
    sleep(time)
    stop_all()

def right(time,speed):
    FL_forward(speed)
    BL_forward(speed)
    FR_backward(speed)
    BR_backward(speed)
    sleep(time)
    stop_all()

def left(time, speed):
    FR_forward(speed)
    BR_forward(speed)
    FL_backward(speed)
    BL_backward(speed)
    sleep(time)
    stop_all()





while True:
    if button.value():
        break

print("asd")
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
                    if ultra() > 20:
                        print('forward')
                        forward(0.3, 75)
                    else:
                        continue
                if packet[6] == 4:
                    print('left')
                    led2.value(1)
                    left(0.3, 75)
                    led2.value(0)
                if packet[6] == 2:
                    print('backward')
                    backward(0.3, 75)
                if packet[6] == 8:
                    print('right')
                    led1.value(1)
                    right(0.3, 75)
                    led1.value(0)
                if packet[5] == 4:
                    if ultra() > 50:
                        print('forward')
                        forward(1, 100)
                    else:
                        continue
                if packet[5] == 8:
                    print('circle')
                    led1.value(1)
                    right(1, 100)
                    led1.value(0)
                if packet[5] == 16:
                    print('x mode')
                    while True:
                        data = ultra()
                        print(data)
                        if data > 20:
                            forward(0.1, 55)
                            continue
                        if data >= 10 and data <= 20:
                            sleep(0.1)
                            continue
                        if data < 10:
                            backward(0.1, 55)
                            continue
                        if data < 5:
                            break
                        
                    
                if packet[5] == 32:
                    led2.value(1)
                    print('square')
                    left(1,100)
                    led2.value(0)

           
