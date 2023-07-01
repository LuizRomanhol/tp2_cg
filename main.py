from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import model
import numpy as np
import math
import random

frame = 1
keys = {'a': False, 'd': False, 'w': False, 's': False, ' ': False, 'x': False}

class Coid:
    def __init__(self, color=[1, 0.75, 0.75], location=[0, 0, 0], velocity=[0, 0, 0]):
        self.location = location
        self.rotation = 0
        self.color = color
        self.colors = []
        self.v_rotation = 0
        self.pose = Pose([model.open_arms,model.closed_arms,model.neutral_arms],[0,1,0,1,0,1,0,1,0,1,0,1,2,2,2,2],8)
        self.colors = [self.color if x == model.skin_color else x for x in model.colors]        
        
    def get_geometry(self, frame):
        vertices = self.pose.get_pose(frame)
        return vertices, model.faces, self.colors, model.normals
        
    def render(self, frame):
        vertices, faces, colors, normals = self.get_geometry(frame)

        glPushMatrix()
        glTranslatef(self.location[0], self.location[1], self.location[2])  # Coloca o coid na posição self.location
        glRotatef(self.rotation, 0, 0, 1)
        glRotatef(self.v_rotation, -1, 0, 0)

        glBegin(GL_QUADS)

        for face_index, face in enumerate(faces):
            glColor3fv(colors[face_index])
            glNormal3fv(normals[face_index])
            for vertex_index in face:
                glVertex3fv(vertices[vertex_index])
        glEnd()

        glPopMatrix()
        
    def foward(self, amount):
        self.location = np.array(self.location) + rotate_vector([0,amount,0], self.rotation, self.v_rotation)
        
    def point(self, location):
        location2 = location
        location1 = self.location
        dx = location2[0] - location1[0]
        dy = location2[1] - location1[1]
        dz = location2[2] - location1[2]
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        self.rotation = angle_deg - 90
        v_angle_rad = math.atan2(dz, math.sqrt(dx**2 + dy**2))
        v_angle_deg = math.degrees(v_angle_rad)
        self.v_rotation = -v_angle_deg


class Object:
    def __init__(self, geometry, location=[0, 0, 0], size=2,color=np.array([1,2,1.5])):
        self.location = location
        self.size = 2
        self.geometry = geometry
        self.color = color

    def render(self):
        vertices, faces, normals = self.geometry

        glPushMatrix()
        glTranslatef(self.location[0], self.location[1], self.location[2])  # Coloca o coid na posição self.location
        glScalef(self.size, self.size, self.size)
        
        glBegin(GL_QUADS)
        for face_index, face in enumerate(faces):
            swil = random.randint(-1,1)
            color = vertices[face[0]][2]/10 + 0.35
            glColor3fv(self.color * color)

            glNormal3fv(normals[face_index])
            for vertex_index in face:
                glVertex3fv(vertices[vertex_index])
        glEnd()

        glPopMatrix()

class Pose:
    def __init__(self,poses,animation,delay):
        self.poses = poses 
        self.animation = animation
        self.pose_delay = delay
        self.random_delay = random.randint(0,len(self.animation)-1)
    def get_pose(self,frame):
        return self.poses[self.animation[(frame//self.pose_delay + self.random_delay)%len(self.animation)]]

def matriz_rotacao(eixo, angulo):
    eixo_normalizado = eixo / np.linalg.norm(eixo)
    x, y, z = eixo_normalizado
    radianos = np.radians(angulo)
    c = np.cos(radianos)
    s = np.sin(radianos)
    t = 1 - c
    matriz = np.array([[t*x*x + c, t*x*y - s*z, t*x*z + s*y],
                      [t*x*y + s*z, t*y*y + c, t*y*z - s*x],
                      [t*x*z - s*y, t*y*z + s*x, t*z*z + c]])
    return matriz
    
def rotate_vector(vector, horizontal_rotation, vertical_rotation):
    def horizontal_rotation_func(vector, angle):
        horizontal_axis = np.array([0, 0, 1])  # Eixo Z
        rotation_matrix = matriz_rotacao(horizontal_axis, angle)
        rotated_vector = np.dot(rotation_matrix, vector)
        return rotated_vector
    
    def vertical_rotation_func(vector, angle):
        projected_vector = np.array([vector[0], vector[1], 0])
        rotation_matrix = matriz_rotacao(np.array([0, 0, 1]), 90)
        rotated_vector = np.dot(rotation_matrix, projected_vector)
        w_vector = rotated_vector / np.linalg.norm(rotated_vector)
        rotation_matrix_w = matriz_rotacao(w_vector, angle)
        rotated_vector = np.dot(rotation_matrix_w, vector)
        return rotated_vector
    
    rotated_vector_horizontal = horizontal_rotation_func(vector, horizontal_rotation)
    rotated_vector_vertical = vertical_rotation_func(rotated_vector_horizontal, vertical_rotation)
    
    return rotated_vector_vertical

coids = []
tower = Object((model.tower_vertices, model.tower_faces, model.tower_normals),[0,0,0],2,np.array([1,2,1.5]))
algaes = []

def add_algae():
    color = 0.05
    background_color = np.array([color, color*2, color*1.5]) *2
    
    global algaes
    def rn():
        return random.randint(-4,24)
    algae_color = np.array([0,1,0.5])
    for i in range(random.randint(3,3)):
        a = rn()
        b = rn()
        max_j = random.randint(1,3)
        for j in range(max_j):
            color = (background_color*(max_j*(j+1)) + algae_color*(j+1))/ max_j
            algaes.append(Object((model.algae_vertices, model.algae_faces, model.algae_normals),[a,b,-16+2.65*j],3,color))

add_algae()
            
def add_coid():
    global coids
    def rn():
        return random.randint(0,10)/10
        
    color = rn()
    coid = Coid(color=[color*3, color*1.5, color], location=[rn(), rn(), rn()])  # O segundo coid permanece parado  
    coids.append(coid)

add_coid()
for i in range(8):
    add_coid()

def init():
    glEnable(GL_LIGHTING)  # Ativa a iluminação
    glEnable(GL_LIGHT0)  # Ativa a primeira fonte de luz

    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 1.0, 0.0, 0.0])  # Define a posição da luz (acima da cena)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1.0])  # Define a componente ambiente da luz
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.05, 0.05, 0.05, 1.0])  # Define a componente difusa da luz

    glEnable(GL_COLOR_MATERIAL)  # Habilita a opção para aplicar as cores
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    color = 0.05
    glClearColor(color, color*2, color*1.5, 0.0)
    glEnable(GL_DEPTH_TEST)


def display():
    global frame, coids, keys, tower#, algaes

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
#    glLoadIdentity()
#    gluPerspective(25, 1, 0.1, 150.0)
#    gluLookAt(-x, -x, x*1.25, 0, 0, 0, 0, 0, 1)
    glOrtho(-25, 25, -25, 25, -150.0, 150.0);

    gluLookAt(-50, -50, 62.5, 0, 0, 0, 0, 0, 1);    
    x = 50
    for coid in coids:
        coid.render(frame)
    
    for algae in algaes:
        algae.render()
    
    tower.render()
    draw_plane()
    
def move_main_coid():
    global coids
    main_coid = coids[0]
    if keys['d']:
        main_coid.rotation -= 5
    if keys['a']:
        main_coid.rotation += 5
    if keys['w']:
        main_coid.foward(0.5)
    if keys['s']:
        main_coid.foward(-0.5)
    if keys['x']:
        if main_coid.v_rotation < 90:
            main_coid.v_rotation += 5
    else:
        if main_coid.v_rotation > 0:
            main_coid.v_rotation -= 5
    if keys[' ']:
        if main_coid.v_rotation > -90:
            main_coid.v_rotation -= 5
    else:
        if main_coid.v_rotation < 0:
            main_coid.v_rotation += 5

def update(dt):        
    global frame, coids, keys
#    for coid in coids[1:]:
#        coid.point(coids[0].location)
#        coid.foward(0.05)

    move_main_coid()
    bounding_box = 3
    speed = 0.15
    for coid_1 in coids[1:]:
       for coid_2 in coids:
           distance_vector = np.array(coid_1.location) - np.array(coid_2.location)
           distance = np.linalg.norm(distance_vector)
           if distance > 0:
               unitary_distance_vector = distance_vector/distance
               if distance < bounding_box:
                   coid_1.location = coid_1.location + unitary_distance_vector * speed    
           else:
               coid_1.point(coids[0].location)
               coid_1.foward(0.1)
        
    frame += 1

    glutSwapBuffers()
    glutPostRedisplay()
    glutTimerFunc(16, update, 0)  # Chama a função update a cada 16ms (aproximadamente 60 FPS)

def keyboard(key, x, y):
    global keys

    if key == b'a':
        keys['a'] = True
    elif key == b'd':
        keys['d'] = True
    elif key == b'w':
        keys['w'] = True
    elif key == b's':
        keys['s'] = True
    elif key == b' ':
        keys[' '] = True
    elif key == b'x':
        keys['x'] = True


def keyboard_up(key, x, y):
    global keys

    if key == b'a':
        keys['a'] = False
    elif key == b'd':
        keys['d'] = False
    elif key == b'w':
        keys['w'] = False
    elif key == b's':
        keys['s'] = False
    elif key == b' ':
        keys[' '] = False
    elif key == b'x':
        keys['x'] = False

import numpy as np

def draw_plane():
    pass
#    n = 100
#    half_size = n / 2.0

#    glBegin(GL_QUADS)
#    glColor3f(0.20, 0.20, 0.20);
#    glVertex3f(-half_size, -half_size, 0.0)  # Canto inferior esquerdo
#    glVertex3f(half_size, -half_size, 0.0)   # Canto inferior direito
#    glVertex3f(half_size, half_size, 0.0)    # Canto superior direito
#    glVertex3f(-half_size, half_size, 0.0)   # Canto superior esquerdo
#    glEnd()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(750, 750)
    glutCreateWindow(b"Cubo Girando")
    init()
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutTimerFunc(16, update, 0)  # Inicia o timer para chamar a função update
    glutMainLoop()

if __name__ == "__main__":
    main()
