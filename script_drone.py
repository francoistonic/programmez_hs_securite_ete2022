import pygame
from socket import socket, AF_INET, SOCK_DGRAM

addr = '192.168.0.1'
lift_off = bytes.fromhex('66808080808080801c9c99')
landing = bytes.fromhex('66808080808080802cac99')


def mk_crc(cmd):
    cmd = bytes.fromhex(cmd)
    crc = 0
    for i in cmd:
        crc = i ^ crc
    return crc

def mk_cmd(tlr, tud, fb, rlr):

    ftlr = int((tlr + 1)*128) 
    ftud = 0xff - int((tud + 1)*128) 
    ffb  = 0xff - int((fb  + 1)*128) 
    frlr = int((rlr + 1)*128) 

    ftlr = ftlr if ftlr < 0x60 or ftlr > 0x90 else 0x80
    ftud = ftud if ftud < 0x60 or ftud > 0x90 else 0x80
    ffb  = ffb  if ffb  < 0x60 or ffb  > 0x90 else 0x80
    frlr = frlr if frlr < 0x60 or frlr > 0x90 else 0x80

    cmd = "{:02x}{:02x}{:02x}{:02x}8080800c".format(ftlr, ftud, ffb, frlr)
    crc = mk_crc(cmd)
    packet = "66{}{:02x}99".format(cmd, crc)
    print("{:02x} {:02x} {:02x} {:02x} -> {}".format(ftlr, ftud, ffb, frlr, packet))
    return packet



def main():
    pygame.init()

    clock = pygame.time.Clock()

    pygame.joystick.init()

    s = socket(AF_INET, SOCK_DGRAM)
    s.connect((addr, 50000))
    print("There are: {} joysticks".format(pygame.joystick.get_count()))
    idx = input("idx: ")
    stick = pygame.joystick.Joystick(int(idx))
    stick.init()
    while True:

        pygame.event.get()
        clock.tick(20)

        tilt_right_left  = stick.get_axis(0)
        tilt_up_down     = stick.get_axis(1)
        forward_backward = stick.get_axis(4)
        rotate_lr        = stick.get_axis(3)

        btn_a = stick.get_button(0)
        btn_b = stick.get_button(1)
        
        if btn_a:
            print("LIFT OFF")
            s.send(lift_off)

        elif btn_b:
            print("LANDING")
            s.send(landing)
        else:
            cmd = bytes.fromhex(mk_cmd(tilt_right_left, tilt_up_down, forward_backward, rotate_lr))
            s.send(cmd)
        




try:
    if __name__ == '__main__':
        main()
except KeyboardInterrupt:
    pass

pygame.quit()
