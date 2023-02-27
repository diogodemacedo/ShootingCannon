# Assignment 1
# Program functionality description:
# The following program displays a (2000m broad and 1000m high) field with a blue canon (20m wide, 16m high) positioned
# 200m from the left side of the field. The scaling factor is 0.5, thus the window is 1000 pixels x 500 pixels.
# The cannon's upper left corner is at position (200m,16m) and has a barrel representing the projectiles initial
# velocity (84,84) m/s. The canon is continuously firing a projectile (from the center of the cannon) starting with the
# initial velocity. The projectile is effected by gravity. When the projectile exits the field, it is repositioned to
# the center of the cannon and refired.

# Scientific Computing - Roskilde University
# Diogo de Macedo

# import pygame and sys modules
import pygame
import sys
import random

# initialize pygame
pygame.init()


### colors ###
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (0,0,255)
RED = (255,0,0)

# define a frame rate:
frames_per_second = 60

# Initialize Real world
g = 9.8  # Gravitational acceleration (m/s**2)

# time
# visualization speedup
speedup = 8     #in order to reduce waiting time for impact we speed up by increasing the timestep
t = 0.0  # time in seconds
dt = (1 / frames_per_second)*speedup  # time increment in seconds


width = 2000.0   # Position of wall to the right and width of the coordinate system
height = 1000.0  # Height of the coordinate system
x_grid = 100 # the interval of x-axis grid of the coordinate system
y_grid = 100  # the interval of y-axis grid of the coordinate system

scale_real_to_screen = 0.5 # scale from the real-world to the screen-coordinate system

# conversion from real-world coordinates to pixel-coordinates
def convert(real_world_x, real_world_y, scale=scale_real_to_screen, real_world_height=height):
    # calculate the pixel coordinates from the real-world coordinates and the scale
    x_pixel = int(real_world_x) * scale
    y_pixel = int(real_world_height - real_world_y) * scale - 1
    return (x_pixel, y_pixel)

def to_real_convert(pixel_world_x, pixel_world_y, scale=scale_real_to_screen, real_world_height=height):
    return pixel_world_x/scale, (screen_height-pixel_world_y)/scale-1 #Inverse function of the one before.#Converts from pixel to real world



# initialize real world cannon(s):
# ================================
# The values for the cannon is kept in a dictionary called cannon1. The correctness of some of the functions depend
# on the cannon to have the specified keys defined (you can add other key-value pairs). The intention is that you
# can create extra cannons, i.e., dictionaries with the same keys and different values, and add those to the
# players-list.

# 315.0 m/s Cannonball, e.g., https://www.arc.id.au/CannonBallistics.html
# 120 m/s small gun https://en.wikipedia.org/w/index.php?title=Muzzle_velocity&oldid=970936654

cannon_width, cannon_height = 20, 16
cannon1 = {"x": 200,
           "y": 0+cannon_height,
           "vx": 84.85, # ≈ 120 m/s angle 45
           "vy": 84.85, # ≈ 120 m/s angle 45
           "width": cannon_width,
           "height": cannon_height,
           "color": BLUE,
           'ball_radius': 10 # radius in meters
            }
# more players
players = [cannon1]

def calc_init_ball_pos(cannon):
    # finds the center of the cannon
    return (cannon['x'] + cannon['width']/2, cannon['y'] - cannon['height']/2)

def draw_cannon(surface,cannon):
    # draw the cannon (the barrel will be the length of the initial velocity of the ball
    pygame.draw.rect(surface,cannon['color'], (convert(cannon['x'],cannon['y']),(cannon['width']*scale_real_to_screen,cannon['height']*scale_real_to_screen)))
    cannon_center = calc_init_ball_pos(cannon)
    vel_start = convert(cannon_center[0], cannon_center[1])
    vel_end = convert(cannon_center[0] + cannon['vx'], cannon_center[1]+cannon['vy'])
    pygame.draw.line(surface, cannon['color'], vel_start, vel_end, 2)

def is_inside_field(real_world_x,real_world_y,field_width=width): #Detect when the canon ball has left the field
    # there is no ceiling
    return (real_world_x > 0 and real_world_x < field_width and real_world_y > 0)

# create screen:
# 1. specify screen size
screen_width, screen_height = int(width*scale_real_to_screen), int(height*scale_real_to_screen)
# 2. define screen
screen = pygame.display.set_mode((screen_width, screen_height))
# 3. set caption
pygame.display.set_caption("Projectile motion cannon")

# update pygames clock use the framerate
clock = pygame.time.Clock()


## draw real-world grid on screen
def draw_grid(surface, color, real_x_grid,real_y_grid,real_width=width, real_height=height):
    # vertical lines
    for i in range(int(real_width / real_x_grid)):
        pygame.draw.line(surface, color, convert(i * real_x_grid, 0),  convert(i * real_x_grid, real_height))
    # horizontal lines
    for i in range(int(real_height / y_grid)):
        pygame.draw.line(surface, color, convert(0 , i * real_y_grid ), convert(real_width, i * real_y_grid))

# game loop truth value
running = True
turn = 0
round_counter= 0 #counts the number of rounds, stops after 5 rounds
random_number=random.randint(-15,15) #generates a random number that will be used to model the wind force

# initialize the projectile's: color, pixel velocity and pixel position according to the current player
(x,y) = calc_init_ball_pos(players[turn])
vx = players[turn]['vx']  # x velocity in meters per second
vy = players[turn]['vy']  # y velocity in meters per second
ball_color = players[turn]['color']
ball_radius = players[turn]['ball_radius']

# this function will initialize the global variables of the projectile to be those of the players cannon  (similar to the initializing above)
def change_player(): #All the things that will happen when you change player.
    # Technical comment concerning the "global"  :
    # we need to tell the program that we want to update the global variables. If we did not, the program would instead
    # think that we are working with some other variables with the same name.s
    global players, turn, shooting, x, y, vx, vy, ball_color,ball_radius, round_counter
    turn = (turn + 1) % len(players)   # will rotate through the list of players
    (x, y) = calc_init_ball_pos(players[turn])
    vx = players[turn]['vx']
    vy = players[turn]['vy']
    ball_color = players[turn]['color']
    ball_radius = players[turn]['ball_radius']
    shooting=False #The cannon does not shoot every time the player gets changed
    round_counter += 1
    print("Player 1, DONE")
# game loop:
shooting = False
while (running):

    # loop over events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shooting=True
                random_number=random.randint(-15,15)
        if event.type == pygame.MOUSEBUTTONDOWN:
            x_pix_m,y_pix_m = pygame.mouse.get_pos()
            real_mouse_x, real_mouse_y=to_real_convert(x_pix_m,y_pix_m)
            vx= real_mouse_x-cannon1["x"]
            vy= real_mouse_y-cannon1["y"]
            cannon1["vx"]= real_mouse_x-cannon1["x"]
            cannon1["vy"]= real_mouse_y-cannon1["y"]

    if round_counter >= 5: #Ends the game after 5 rounds have been completed
            running = False

    # check whether the ball is outside the field
    if not(is_inside_field(x,y)):
       change_player() # if there is only one player, the ball will restart at that players center


    # game logic
    # draw a background using screen.fill()
    screen.fill(BLACK)

    # draw grid
    draw_grid(screen,RED,x_grid,y_grid,width,height)

    # draw the player's cannon
    draw_cannon(screen, cannon1)

    # convert the real-world coordinates to pixel-coordinates
    (x_pix, y_pix) = convert(x, y)
    ball_radius_pix = round(scale_real_to_screen * ball_radius)

    # draw ball using the pixel coordinates
    pygame.draw.circle(screen,ball_color,(x_pix,y_pix),ball_radius_pix)

    # print time passed, position and velocity
    # print(f"time: {t}, pos: ({x,y}), vel: ({vx,vy}, pixel pos:({x_pix},{y_pix}))")

    # update time passed, the ball's real-world acceleration, velocity, position for the next time_step
    # Apply gravitational acceleration

    if random_number > 0:
        pygame.draw.line(screen,ball_color,(400,400),(500,400))
        pygame.draw.line(screen,ball_color,(480,380),(500,400))
        pygame.draw.line(screen,ball_color,(480,420),(500,400))
    elif random_number < 0:
        pygame.draw.line(screen,ball_color,(400,400),(500,400))
        pygame.draw.line(screen,ball_color,(400,400),(420,380))
        pygame.draw.line(screen,ball_color,(400,400),(420,420))

    mass = 1 #kg
    if shooting:
        vx_wind=random_number
        D=0.1 #drag coeff value for air

        F_drag_x = -D * (vx - vx_wind)
        v_drag_x = F_drag_x * dt
        vx = vx + v_drag_x

        F_drag_y=-D*vy
        v_drag_y = F_drag_y/mass*dt
        vy = (vy - g * dt)+v_drag_y






    # Update positions from velocities
        x = x + vx * dt
        y = y + vy * dt


    # redraw the screen
    pygame.display.flip()

    # Limit the framerate (must be called in each iteration)
    clock.tick(frames_per_second)

# after the game loop
pygame.quit()
sys.exit()
