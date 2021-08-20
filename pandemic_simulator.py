# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 18:49:45 2020

@author: ricar
"""



import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import time
import random
import json


import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es

from model import *
from controller import Controller
    


Controller = Controller()  

# Getting the virus
virus = sys.argv[1]
with open(virus) as json_file:
    data = json.load(json_file)

    
    
if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 1000
    height = 700

    window = glfw.create_window(width, height, "Pandemic simulator", None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, Controller.on_key)
    
    
    # Connecting callback functions to handle mouse events:
    # - Cursor moving over the window
    # - Mouse buttons input
    # - Mouse scroll
    glfw.set_cursor_pos_callback(window, Controller.cursor_pos_callback)
    glfw.set_mouse_button_callback(window, Controller.mouse_button_callback)
    glfw.set_scroll_callback(window, Controller.scroll_callback)

    # Assembling the shader program (pipeline) with both shaders
    pipeline = es.SimpleTransformShaderProgram()
    texturePipeline = es.SimpleTextureTransformShaderProgram()
    
    
    # Telling OpenGL to use our shader program
    glUseProgram(texturePipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0,0,0, 1.0)

    # Creating shapes on GPU memory
    universe = Universe(data[0]['Radius'], data[0]['Contagious_prob'], data[0]['Death_rate'], data[0]['Initial_population'], data[0]['Days_to_heal'], 0.005)  
    Controller.toggle['universe'] = universe

    figure = Figure(universe.cardinality)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    t0 = glfw.get_time()
 
   
    
    while not glfw.window_should_close(window):
        t = glfw.get_time()
        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Drawing the shapes
        universe.update(t)
        universe.draw(pipeline, texturePipeline)
        figure.update(universe.healthPeople, universe.sickPeople, universe.deathPeople, universe.healedPeople)
        figure.draw(pipeline,texturePipeline)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    glfw.terminate()


