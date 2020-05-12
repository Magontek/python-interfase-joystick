import pygame
import sys
import time
import serial

#----------------------------Serie-------------------------

arduino = serial.Serial('COM7', 115200)
time.sleep(2)
arduino.write(b'mv')

input_string=['-','-','-','-','-','-','-','-','-','-']


cont=0

letras=['a','b','c','d','e']

#---------------------------------ejes----------------

eje_acumulador=[90,90,90,90,90]
eje_acum_old=[90,90,90,90,90]

eje_multiplicador=[1,0.5,1,2,2]

#----------------------------Pantalla------------------
# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')


# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((500, 700))

pygame.display.set_caption("Controlador del brazo de 5 ejes")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates.
clock = pygame.time.Clock()

# Initialize the joysticks.
pygame.joystick.init()

# Get ready to print.
textPrint = TextPrint()

# -------- Main Program Loop -----------
while not done:
    #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.
        elif event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        elif event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")

    #
    # DRAWING STEP
    #
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
    textPrint.reset()

    # Get count of joysticks.
    joystick_count = pygame.joystick.get_count()

    textPrint.tprint(screen, "Number of joysticks: {}".format(joystick_count))
    textPrint.indent()

    # For each joystick:
    i=0
    joystick = pygame.joystick.Joystick(i)
    joystick.init()

    textPrint.tprint(screen, "Joystick {}".format(i))
    textPrint.indent()

        # Get the name from the OS for the controller/joystick.
    name = joystick.get_name()
    textPrint.tprint(screen, "Joystick name: {}".format(name))

    # Usually axis run in pairs, up/down for one, and left/right for
     # the other.
    axes = joystick.get_numaxes()
    textPrint.tprint(screen, "Number of axes: {}".format(axes))
    textPrint.indent()

    for i in range(axes):
        axis = joystick.get_axis(i)
        eje_acumulador[i]=eje_acumulador[i]+round(axis*eje_multiplicador[i], 3)
        textPrint.tprint(screen, "Axis {} value: {:>6.3f}".format(i, axis))
        textPrint.tprint(screen, "Acum {} value: {:>6.3f}".format(i, eje_acumulador[i]))
    textPrint.unindent()

    buttons = joystick.get_numbuttons()
    textPrint.tprint(screen, "Number of buttons: {}".format(buttons))
    textPrint.indent()

    for i in range(buttons):
        button = joystick.get_button(i)
        textPrint.tprint(screen, "Button {:>2} value: {}".format(i, button))
    textPrint.unindent()

    hats = joystick.get_numhats()
    textPrint.tprint(screen, "Number of hats: {}".format(hats))
    textPrint.indent()

    # Hat position. All or nothing for direction, not a float like
    # get_axis(). Position is a tuple of int values (x, y).
    for i in range(hats):
        hat = joystick.get_hat(i)
        textPrint.tprint(screen, "Hat {} value: {}".format(i, str(hat)))
        eje_acumulador[4]=eje_acumulador[4]+(1*hat[0])
        textPrint.tprint(screen, "Acum 5 value: {:>6.3f}".format(eje_acumulador[4]))
    textPrint.unindent()

    textPrint.unindent()
    textPrint.tprint(screen, "----Serial----".format(hats))
    while arduino.in_waiting > 0:
        for i in range(9):
            input_string[i]=input_string[i+1]
        print("reading...")
        s_time= time.time()
        input_string[9]=arduino.readline()
        e_time= s_time-time.time()
        print("Lag {}".format(e_time))
    for i in range(10):
        textPrint.tprint(screen, "{}".format(str(input_string[i])))

    

    #
    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
    #

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 20 frames per second.
    clock.tick(20)

    if cont==1:
        cont=0
        out_string = "s"
        for i in range(5):
            out_string +="{:>4.2f}".format(eje_acumulador[i])+" "
            #print (out_string)
            #time.sleep(1)
        arduino.write(out_string.encode())
    else:
        cont += 1

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
arduino.close()
pygame.quit()
