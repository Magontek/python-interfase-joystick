import pygame
import sys
import time
import serial

#----------------------------Serie-------------------------
#Arduino es el objeto serie donde se escribe todo
#To-Do:
#1) permitir modificar el puerto y no conectar hasta apretar conectar

arduino = serial.Serial('COM7', 115200)
time.sleep(2)
arduino.write(b'mv') #Indico que funcione en modo verborragico asi tengo feedback de lo que hace el arduino

input_string=['-','-','-','-','-','-','-','-','-','-'] #Aca se almacena lo que va llegando por el puerto serie


cont=0
#Deprecated. Implemente la escritura de todos los numero a la vez
letras=['a','b','c','d','e'] 

#---------------------------------ejes----------------
#Variables que involucran los incremenos en los ejes y las velocidades de los incrementos

eje_acumulador=[90,90,90,90,90]
#Deprecated. De cuando esperaba cambios para enviar el dato
eje_acum_old=[90,90,90,90,90]

eje_multiplicador=[1,0.5,1,2,2]

#----------------------------Pantalla------------------
# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')


# Esta es la clase en donde se va escribir el texto en pantalla
# La robe del ejemplo de joystick del pygame
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

# Alto y ancho de la ventana
screen = pygame.display.set_mode((500, 700))

# Nombre de la pantalla
pygame.display.set_caption("Controlador del brazo de 5 ejes")

# Variable booleana para escapar del loop. Si se hace click en cerrar esto para a true
done = False

# Este clock es para actualizar la pantalla, pero tambien para la frecuencia de envio de los datos serie
clock = pygame.time.Clock()

# Inicializa los joysticks
pygame.joystick.init()

# Creo un objeto textprint para cargarle todo el texto
textPrint = TextPrint()

# -------- Main Program Loop -----------
while not done:
    #
    # Proceso los evnetos
    #
    # Posibles interracciones: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.
        # Estos no los uso pero me sirven para saber si se colgo el programa
        elif event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        elif event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")

    # Todo lo siguiente carga texto y dibuja la pantalla
    # Borro la pantalla
    screen.fill(WHITE)
    #Borro el texto de textprint
    textPrint.reset()

    # Se fija cuantos joiystics hay. Igual solo uso el primero
    #To-Do: permitir selecionar joistick con un menu o algo
    joystick_count = pygame.joystick.get_count()

    # Muestro cuantos joistciks hay conectados, asi se si le estoy errando al joystick
    textPrint.tprint(screen, "Number of joysticks: {}".format(joystick_count))
    textPrint.indent()

    # i en este caso es el numero de joistick que voy a usar
    i=0
    joystick = pygame.joystick.Joystick(i)
    joystick.init()

    textPrint.tprint(screen, "Joystick {}".format(i))
    textPrint.indent()

    # Imprimo el nombre del joistick.
    name = joystick.get_name()
    textPrint.tprint(screen, "Joystick name: {}".format(name))

    # Cantidad de ejes activos, el resto del programa supone 4
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

    # Leo todos los botones, todavia no lo uso pero estaba en el ejemplo
    for i in range(buttons):
        button = joystick.get_button(i)
        textPrint.tprint(screen, "Button {:>2} value: {}".format(i, button))
    textPrint.unindent()

    hats = joystick.get_numhats()
    textPrint.tprint(screen, "Number of hats: {}".format(hats))
    textPrint.indent()

    # Posicion del pob, da uno o cero, pero la variable es tipo int en forma de tupla (x, y)
    for i in range(hats):
        hat = joystick.get_hat(i)
        textPrint.tprint(screen, "Hat {} value: {}".format(i, str(hat)))
        eje_acumulador[4]=eje_acumulador[4]+(1*hat[0])
        textPrint.tprint(screen, "Acum 5 value: {:>6.3f}".format(eje_acumulador[4]))
    textPrint.unindent()

    textPrint.unindent()
    # Leo la informacion que llega por serie si es que llega
    # Desplaza todo el texto un lugar arriba y escribe la linea entrante abajo
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

    

    # Imprimo en pantalla todo lo que escribi, Solo se puede scribir cosas en pantalla hasta aca
    pygame.display.flip()

    # 20 FPS y de paso es la velocidad maxima de envio por el puerto serie
    clock.tick(20)

    #Divido el tiempo a la mitad, para enviar 10 datos por segundo
    # Transmitiendo a 115200 baudios deberia alcanzar para transmitir los 5 paquetes de datos
    if cont==1:
        cont=0
        out_string = "s"
        for i in range(5):
            out_string +="{:>4.2f}".format(eje_acumulador[i])+" "
        arduino.write(out_string.encode())
    else:
        cont += 1

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
arduino.close()
pygame.quit()
