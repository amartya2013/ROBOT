from machine import UART, Pin, PWM
from time import sleep


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



for pwm in [PWM_1, PWM_2, PWM_3, PWM_4]:
    pwm.freq(100)


def back_right_forward(speed):
    IN_1.high()
    IN_2.low()
    duty = int((speed / 100) * 65535)
    PWM_1.duty_u16(duty)
    
    
def back_right_backward(speed):
    IN_1.low()
    IN_2.high()
    duty = int((speed / 100) * 65535)
    PWM_1.duty_u16(duty)
    
def back_left_forward(speed):
    IN_3.high()
    IN_4.low()
    duty = int((speed / 100) * 65535)
    PWM_2.duty_u16(duty)
    
def back_left_backward(speed):
    IN_3.low()
    IN_4.high()
    duty = int((speed / 100) * 65535)
    PWM_2.duty_u16(duty)
       
def front_right_forward(speed):
    IN_7.high()
    IN_8.low()
    duty = int((speed / 100) * 65535)
    PWM_3.duty_u16(duty)
   
    
def front_right_backward(speed):
    IN_7.low()
    IN_8.high()
    duty = int((speed / 100) * 65535)
    PWM_3.duty_u16(duty)
    
def front_left_forward(speed):
    IN_5.high()
    IN_6.low()
    duty = int((speed / 100) * 65535)
    PWM_4.duty_u16(duty)
    
def front_left_backward(speed):
    IN_5.low()
    IN_6.high()
    duty = int((speed / 100) * 65535)
    PWM_4.duty_u16(duty)
    
    
def stop_all():
    for pwm in [PWM_1, PWM_2, PWM_3, PWM_4]:
        pwm.duty_u16(0)

    for pin in [IN_1,IN_2,IN_3,IN_4,IN_5,IN_6,IN_7,IN_8]:
        pin.low()
   


def robot_forward(time, speed):
    back_right_forward(speed)
    back_left_forward(speed)
    front_right_forward(speed)
    front_left_forward(speed)
    sleep(time)
    stop_all()
    
def robot_backward(time, speed):
    back_right_backward(speed)
    back_left_backward(speed)
    front_right_backward(speed)
    front_left_backward(speed)
    sleep(time)
    stop_all()

def robot_right(time, speed):
    back_right_backward(speed)
    front_right_forward(speed)
    back_left_forward(speed)
    front_left_backward(speed)
    sleep(time)
    stop_all()

def robot_left(time, speed):
    back_right_forward(speed)
    front_right_backward(speed)
    back_left_backward(speed)
    front_left_forward(speed)
    sleep(time)
    stop_all()

    
    


# UART0 on Pico
uart = UART(0, baudrate=9600, tx=0, rx=1)

print("Loopback Test Started")

# Send and receive test
while True:
    test_message = b"HELLO\n"
    uart.write(test_message)    # Send message
    sleep(0.1)

    if uart.any():
        data = uart.read()
        if data:
            filtered = "".join([chr(b) for b in data if 32 <= b <= 126])
            
            # Optional: normalize text
            filtered = filtered.lower().strip()
            print("Received:", filtered)
            if filtered != 'error':
                if filtered == 'forward':
                    robot_forward(1, 50)
                if filtered == 'right':
                    robot_right(1, 50)
                if filtered == 'backward':
                    robot_backward(1, 50)
                if filtered == 'left':
                    robot_left(1, 50)
        sleep(0.5)


