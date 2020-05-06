import pygame
import sys
import time

pygame.joystick.init()

print pygame.joystick.get_count()

_joystick = pygame.joystick.Joystick(0)
_joystick.init()
print _joystick.get_init()
print _joystick.get_id()
print _joystick.get_name()
print _joystick.get_numaxes()
print _joystick.get_numballs()
print _joystick.get_numbuttons()
print _joystick.get_numhats()
print _joystick.get_axis(0)
