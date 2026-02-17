from machine import Pin, PWM
from time import sleep


IN_1 = Pin(2, Pin.OUT)
IN_2 = Pin(3, Pin.OUT)
IN_3 = Pin(4, Pin.OUT)
IN_4 = Pin(5, Pin.OUT)
IN_5 = Pin(6, Pin.OUT)
IN_6 = Pin(7, Pin.OUT)
IN_7 = Pin(8, Pin.OUT)
IN_8 = Pin(9, Pin.OUT)



for pwm in [PWM_1, PWM_2, PWM_3, PWM_4]:
    pwm.freq(2000)


def back_right_forward():
    IN_1.high()
    IN_2.low()
    
def back_right_backward():
    IN_1.low()
    IN_2.high()
    
def back_left_forward():
    IN_3.high()
    IN_4.low()
    
def back_left_backward():
    IN_3.low()
    IN_4.high()
       
def front_right_forward():
    IN_7.high()
    IN_8.low()
   
    
def front_right_backward():
    IN_7.low()
    IN_8.high()
    
def front_left_forward():
    IN_5.high()
    IN_6.low()
    
def front_left_backward():
    IN_5.low()
    IN_6.high()
    
   


def robot_forward(time):
    back_right_forward()
    back_left_forward()
    front_right_forward()
    front_left_forward()
    sleep(time)
    IN_1.low()
    IN_2.low()
    IN_3.low()
    IN_4.low()
    IN_5.low()
    IN_6.low()
    IN_7.low()
    IN_8.low()
    
def robot_backward(time):
    back_right_backward()
    back_left_backward()
    front_right_backward()
    front_left_backward()
    sleep(time)
    IN_1.low()
    IN_2.low()
    IN_3.low()
    IN_4.low()
    IN_5.low()
    IN_6.low()
    IN_7.low()
    IN_8.low()

def robot_right(time):
    back_right_backward()
    front_right_backward()
    back_left_forward()
    front_left_forward()
    sleep(time)
    IN_1.low()
    IN_2.low()
    IN_3.low()
    IN_4.low()
    IN_5.low()
    IN_6.low()
    IN_7.low()
    IN_8.low()
    
def robot_left(time):
    back_left_backward()
    front_left_backward()
    back_right_forward()
    front_right_forward()
    sleep(time)
    IN_1.low()
    IN_2.low()
    IN_3.low()
    IN_4.low()
    IN_5.low()
    IN_6.low()
    IN_7.low()
    IN_8.low()
    

robot_right(5)

    
    





