import pygame
from picamera2 import Picamera2
from gpiozero import Motor, PWMOutputDevice
from time import sleep

# Motor A
motor1 = Motor(forward=26, backward=16)
enable1 = PWMOutputDevice(13)

# Motor B
motor2 = Motor(forward=5, backward=6)
enable2 = PWMOutputDevice(12)


motor3 = Motor(forward=23, backward=22)
enable3 = PWMOutputDevice(19)

motor4 = Motor(forward=17, backward=27)
enable4 = PWMOutputDevice(18)
            
def set_speed(speed):
    enable1.value = speed
    enable2.value = speed
    enable3.value = speed
    enable4.value = speed

def stop_all():
    motor1.stop()
    motor2.stop()
    motor3.stop()
    motor4.stop()
    
def forward(duration):
    motor1.forward()
    motor2.forward()
    motor3.forward()
    motor4.forward()
    set_speed(0.8)
    sleep(duration)
    stop_all()
    
def backward(duration):
    motor1.backward()
    motor2.backward()
    motor3.backward()
    motor4.backward()
    set_speed(0.8)
    sleep(duration)
    stop_all()
    
def left(duration):
    motor1.backward()
    motor2.forward()
    motor3.forward()
    motor4.backward()
    set_speed(0.8)
    sleep(duration)
    stop_all()
    
    
def right(duration):
    motor1.forward()
    motor2.backward()
    motor3.backward()
    motor4.forward()
    set_speed(0.8)
    sleep(duration)
    stop_all()
    
    

pygame.init()

# Window
screen = pygame.display.set_mode((600, 480))
pygame.display.set_caption("Pi Camera + Controls")

font = pygame.font.SysFont(None, 30)

# Camera setup
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

# Buttons
buttons = {
    "forward": pygame.Rect(270, 10, 100, 40),
    "backward": pygame.Rect(270, 430, 100, 40),
    "left": pygame.Rect(150, 220, 100, 40),
    "right": pygame.Rect(390, 220, 100, 40)
}

def draw_button(rect, text, mouse_pos):
    color = (0, 200, 0) if rect.collidepoint(mouse_pos) else (0, 120, 255)
    pygame.draw.rect(screen, color, rect, border_radius=8)

    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, label.get_rect(center=rect.center))

running = True
while running:
    # Capture frame
    frame = picam2.capture_array()
    if frame.shape[2] == 4:
        frame = frame[:,:,:3]

    # Convert to Pygame surface
    upside_down_frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    frame = pygame.transform.flip(upside_down_frame,False, True)

    # Draw camera
    screen.blit(frame, (0, 0))

    mouse_pos = pygame.mouse.get_pos()

    # Draw buttons
    for name, rect in buttons.items():
        draw_button(rect, name, mouse_pos)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for name, rect in buttons.items():
                if rect.collidepoint(event.pos):
                    print(name)
                    exec(f'{name}(0.1)')

    pygame.display.update()

picam2.stop()
pygame.quit()
