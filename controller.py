"""
Contralor de la aplicación.
"""

import glfw
import sys


class Controller(object):

    def __init__(self):
        self.fill_polygon = True
        self.toggle = {}
        self.leftClickOn = False
        self.theta = 0.0
        self.mousePos = (0.0, 0.0)

    def set_toggle(self, tp, key):
        self.toggle[key] = tp

    def on_key(self, window, key, scancode, action, mods):        
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_SPACE:
            self.fill_polygon = not self.fill_polygon

        elif key == glfw.KEY_P:
            universe = self.toggle['universe']
            universe.graph()
            sys.exit()
        else:
            print('Unknown key')
  
    def cursor_pos_callback(self,window, x, y):
        self.mousePos = (x,y)
        
    def mouse_button_callback(self,window, button, action, mods):
        #glfw.MOUSE_BUTTON_1: left click
        #glfw.MOUSE_BUTTON_2: right click
        #glfw.MOUSE_BUTTON_3: scroll click
    
        if (action == glfw.PRESS or action == glfw.REPEAT):
        
            (x,y) = (glfw.get_cursor_pos(window))
            pass
                
        elif (action ==glfw.RELEASE):
            if (button == glfw.MOUSE_BUTTON_1):
                self.leftClickOn = False


    def scroll_callback(window, x, y):
        print("Mouse scroll:", x, y)

