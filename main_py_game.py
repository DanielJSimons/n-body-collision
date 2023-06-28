import pygame
import numpy as np
from itertools import combinations

pygame.init()

#Set up screen and pygame clock
width, height = 1000, 1000
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

#These have been taken from my gravity simulation repo
pygame.font.init()  #Initialize the font module
timer_font = pygame.font.Font(None, 48)  #Define the font and size for the timer text  

#Define the rectangle parameters
rect_pos = (20, 10)  #Position of the top-left corner of the rectangle
rect_size = (400, 60)  #Width and height of the rectangle
rect_color = pygame.Color("White")  #Color of the rectangle
rect_thickness = 2  #Thickness of the rectangle outline

#Defining number of particles and separating into a quadrant for the colour scheme later on
n_part = 300
r = np.random.random((2, n_part))

ixtr = (r[0] > 0.5) & (r[1] > 0.5)
ixtl = (r[0] <= 0.5) & (r[1] > 0.5)
ixbr = (r[0] > 0.5) & (r[1] <= 0.5)
ixbl = (r[0] <= 0.5) & (r[1] <= 0.5)

#Array of id's for all particles
ids = np.arange(n_part)

#Creating an array of zeros for x and y velocities
v = np.zeros((2, n_part))
center_x = width / 2
center_y = height / 2

#Calculate the direction vector towards the center
direction_x = center_x - r[0] * width
direction_y = center_y - r[1] * height

#Calculate the magnitude of the direction vector
magnitude = np.sqrt(direction_x**2 + direction_y**2)

#Set the absolute velocity value
absolute_velocity = 800  # Change this value to your desired absolute velocity

#Normalize the direction vector and multiply by the absolute velocity
v[0] = (direction_x / magnitude) * absolute_velocity
v[1] = (direction_y / magnitude) * absolute_velocity

#Generating all possible combinations of pairs for the ids of all particles
id_pairs = np.asarray(list(combinations(ids, 2)))

#Radius of particles set
radius = 0.005
#Working out whether particles collide given their x and y distance from each other, if this is less than 2r then the particles collide.
id_pairs_collide = id_pairs[np.sqrt(((r[0][id_pairs[:, 0]] - r[0][id_pairs[:, 1]]) ** 2 + (r[1][id_pairs[:, 0]] - r[1][id_pairs[:, 1]]) ** 2)) < 2 * radius]

v1 = v[:, id_pairs_collide[:, 0]]
v2 = v[:, id_pairs_collide[:, 1]]
r1 = r[:, id_pairs_collide[:, 0]]
r2 = r[:, id_pairs_collide[:, 1]]


#Defining some functions for motion and velocities between the pairs. This could be moved to a separate .py file but we only have 4 so I perceive it to be acceptable to leave these here.
#Function for returning the difference in x between pairs in a flattened array using .ravel()
def get_delta_pairs(x, id_pairs):
    return np.diff(np.array([x[id_pairs[:, 0]], x[id_pairs[:, 1]]]).T, axis=1).ravel()

#Returns an array for the definite total distance between pairs
def get_deltad_pairs(r, id_pairs):
    return np.sqrt(get_delta_pairs(r[0], id_pairs) ** 2 + get_delta_pairs(r[1], id_pairs) ** 2)

#Figuring out the new velocities of particles once they have collided. Fairly simple linear algebra
def new_vel(v1, v2, r1, r2):
    v1new = v1 - ((v1 - v2) * (r1 - r2)).sum(axis=0) / np.sum((r1 - r2) ** 2, axis=0) * (r1 - r2)
    v2new = v2 - ((v1 - v2) * (r1 - r2)).sum(axis=0) / np.sum((r2 - r1) ** 2, axis=0) * (r2 - r1)
    return v1new, v2new

#Defining the motion of the particles. 
#rs & vs being the positions and velocities of particles running for the total time ts as defined.
def motion(r, v, id_pairs, ts, dt, d_cutoff):
    rs = np.zeros((ts, r.shape[0], r.shape[1]))
    vs = np.zeros((ts, v.shape[0], v.shape[1]))
    # Initial State
    rs[0] = r.copy()
    vs[0] = v.copy()
    for i in range(1, ts):
        ic = id_pairs[get_deltad_pairs(r, id_pairs) < d_cutoff]    #Here we implement a cutoff between particles to improve efficiency.
        v[:, ic[:, 0]], v[:, ic[:, 1]] = new_vel(v[:, ic[:, 0]], v[:, ic[:, 1]], r[:, ic[:, 0]], r[:, ic[:, 1]])    #Updating new velocities using new_vel

        v[0, r[0] > 1] = -np.abs(v[0, r[0] > 1])
        v[0, r[0] < 0] = np.abs(v[0, r[0] < 0])
        v[1, r[1] > 1] = -np.abs(v[1, r[1] > 1])
        v[1, r[1] < 0] = np.abs(v[1, r[1] < 0])         #Here we reverse the velocities of any particles that touch the side of the wall in that given direction. For example if a particle hits the left wall only x velocity is reversed. Totally elastic collision.

        r = r + v * dt      #Here we are updating the new displacement over time.
        rs[i] = r.copy()
        vs[i] = v.copy()   #copying this to the empty arrays of rs vs 
    return rs, vs


rs, vs = motion(r, v, id_pairs, ts=10000, dt=0.000004, d_cutoff=2 * radius)    #Defining some parameters for the simulation

#Defining the colours of each particle type
white_color = (255, 255, 255)
orange_color = (255, 165, 0)
yellow_color = (255, 255, 0)
red_color = (255, 0, 0)
circle_radius = int(radius * width)

running = True
frame = 0
timer_started = False  #Flag to track if the timer has started

#Starting pygame event
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((0, 0, 0)) #Filling out a black background for consistency 

    if not timer_started:
        #Check if all particle sprites are visible on the screen -  This was necessary as the timer was previously starting at a time before the sprites were loaded on the surface, an increased number of sprites meant the larger the inaccuracy in the timer.
        if np.all(rs[frame][0] > 0) and np.all(rs[frame][0] < 1) and np.all(rs[frame][1] > 0) and np.all(rs[frame][1] < 1):
            start_time = pygame.time.get_ticks()  # Start the timer
            timer_started = True

    current_time = pygame.time.get_ticks()
    elapsed_time = current_time - start_time       #Some simple timing calculations

    xwhite, ywhite = rs[frame][0][ixtr], rs[frame][1][ixtr]    #Defining variables xwhite and ywhite from the initial frame, x and y coordinates and which quadrant they are in.
    xorange, yorange = rs[frame][0][ixtl], rs[frame][1][ixtl]
    xyellow, yyellow = rs[frame][0][ixbl], rs[frame][1][ixbl]
    xred, yred = rs[frame][0][ixbr], rs[frame][1][ixbr]

    for x, y in zip(xwhite, ywhite):
        pygame.draw.circle(screen, white_color, (int(x * width), int(y * height)), circle_radius)    #Drawing the particles using the variabels just defined above.
    for x, y in zip(xorange, yorange):
        pygame.draw.circle(screen, orange_color, (int(x * width), int(y * height)), circle_radius)
    for x, y in zip(xyellow, yyellow):
        pygame.draw.circle(screen, yellow_color, (int(x * width), int(y * height)), circle_radius)
    for x, y in zip(xred, yred):
        pygame.draw.circle(screen, red_color, (int(x * width), int(y * height)), circle_radius)

    if timer_started:
        timer_text = timer_font.render(f"Time Elapsed (s): {elapsed_time / 1000:.2f}", True, pygame.Color("white"))    #Rendering the timer text.
    else:
        timer_text = timer_font.render("Loading...", True, pygame.Color("white"))    #Conservative else to let the user know that the program is loading.

    screen.blit(timer_text, (35, 25))   #Applying the timer text to the front of the pygame screen, allowing particles to move freely underneath.

    pygame.draw.rect(screen, rect_color, (*rect_pos, *rect_size), rect_thickness)     #Drawing the rectangle for the timer box. I would like to make this dynamic in the future but this would alternate size with the changing digits in my attempt.

    pygame.display.flip()
    clock.tick(30)  # 30 FPS
    frame += 1
    if frame == len(rs):
        frame = 0

pygame.quit()
