from Code import *
from out_of_bounds import *
from Math_trigonometry import *
import ast
import os





class Transformation():
    """
    Class for the entire Transformation from cartesian to spherical. 
    Used for running multiple instances and being able to control multiple calibrated lights at once.(not implemented yet)
    """
    def __init__(self, fixture_id, calibration_file, rectangle, out_of_bounds_instance):
        self.coordinates = []
        self.cart_x, self.cart_y = 0, 0
        self.cart_pan = 0
        self.cart_tilt = 0
        self.fixture_id = fixture_id
        self.calibration_file = calibration_file
        self.fixture_rectangle = rectangle
        self.selectionstate = False
        self.state = False
        self.out_of_bounds_instance = out_of_bounds_instance

    def get_cart_pan(self):
        
        return self.cart_pan

    def get_cart_tilt(self):
        
        return self.cart_tilt
    
    def create_coordinates_from_file(self):
        """
        Takes the content of the Calibration.txt file and converts it to a list of the 4 stage-corner coordinates.

        Input(no arguments):
            Calibration.txt file
        
        Returns:
            self.coordinates list
        """
        if self.coordinates == []:
            with open(self.calibration_file, "r") as file:

                lines = file.readlines()
                
                for line in lines:                          #iterates over lines in .txt file
                    line = line.rstrip("\n")                #removes newline character from string
                    
                    line_tuple = ast.literal_eval(line)     #converts string to tuple
                    self.coordinates.append(line_tuple)   
        return self.coordinates





    def translate_to_quadrilateral(self, corners):
        """
        Translates coordinates from a normalized 0-100 system to a quadrilateral defined by its corners.

        Args:
            corners: A list of four tuples representing the corners of the quadrilateral:
                    [(bottom_left_x, bottom_left_y), 
                    (bottom_right_x, bottom_right_y), 
                    (top_left_x, top_left_y), 
                    (top_right_x, top_right_y)]

        Input:
                The x and y values from the cartesian_movement() function

        Returns:
            A tuple (x, y) representing the translated coordinates in the quadrilateral's space.
        """
        self.cart_x, self.cart_y = rectangle_movement()[0], rectangle_movement()[1]
        input_x, input_y = self.cart_x, self.cart_y
        
        bl, br, tl, tr = corners
        
        # Interpolate along the bottom and top edges based on input_x
        bottom_x = bl[0] + (br[0] - bl[0]) * (input_x / 100)
        bottom_y = bl[1] + (br[1] - bl[1]) * (input_x / 100)
        top_x = tl[0] + (tr[0] - tl[0]) * (input_x / 100)
        top_y = tl[1] + (tr[1] - tl[1]) * (input_x / 100)

        # Interpolate between the bottom and top points based on input_y
        final_x = bottom_x + (top_x - bottom_x) * (input_y / 100)
        final_y = bottom_y + (top_y - bottom_y) * (input_y / 100)
        
        return final_x, final_y



    overflow = False

    def cartesian_to_spherical(self):
        """
        Transforms the interpolated values from the translate_to_quadrilateral 
        function to the spherical coordinate system.

        Input(already in the code, no arguments):
            Interpolated values from translate_to_quadrilateral() function.
            z: should be the same as in the spherical_to_cartesian() function for accurate results

        Returns:
            A tuple (cart_pan, cart_tilt) representing the transformed values in the spherical coordinate system(pan/tilt).
        """

        global state
        self.state = self.out_of_bounds_instance.out_of_bounds(self.cart_pan, self.cart_tilt)[0]
        self.cart_x, self.cart_y = self.translate_to_quadrilateral(self.create_coordinates_from_file())
        z = 4

        if self.state == False:             #checks where the moving head is positioned to adjust the mathematical functions so that it can seamlessly move to 
            if self.cart_y >= 0 and self.cart_x < 0:              #negative or positive values without weird jumps/inconsistencies
                r = (self.cart_x**2 + self.cart_y**2)**0.5
                self.cart_pan = (((Math_Trigo.arcsine(self.cart_x/r))+offset)+180)
                self.cart_tilt = -(Math_Trigo.arctan(r/z))
            elif self.cart_y < 0 and self.cart_x < 0:
                r = -((self.cart_x**2 + self.cart_y**2)**0.5)
                self.cart_pan = ((Math_Trigo.arcsine(self.cart_x/r))+offset)
                self.cart_tilt = (Math_Trigo.arctan(r/z))
            elif self.cart_y < 0 and self.cart_x > 0:
                r = -((self.cart_x**2 + self.cart_y**2)**0.5)
                self.cart_pan = ((Math_Trigo.arcsine(self.cart_x/r))+offset)
                self.cart_tilt = (Math_Trigo.arctan(r/z))
            elif self.cart_y >= 0 and self.cart_x > 0:
                r = -((self.cart_x**2 + self.cart_y**2)**0.5)
                self.cart_pan = -((Math_Trigo.arcsine(self.cart_x/r))+offset)
                self.cart_tilt = (Math_Trigo.arctan(r/z))
        elif self.state == True:
            if self.cart_y >= 0 and self.cart_x < 0:
                r = (self.cart_x**2 + self.cart_y**2)**0.5
                self.cart_pan = (((Math_Trigo.arcsine(self.cart_x/r))+offset)-180)
                self.cart_tilt = -(Math_Trigo.arctan(r/z))
            elif self.cart_y < 0 and self.cart_x < 0:
                r = -((self.cart_x**2 + self.cart_y**2)**0.5)
                self.cart_pan = (((Math_Trigo.arcsine(self.cart_x/r))+offset)-360)
                self.cart_tilt = (Math_Trigo.arctan(r/z))
            elif self.cart_y < 0 and self.cart_x > 0:
                r = -((self.cart_x**2 + self.cart_y**2)**0.5)
                self.cart_pan = ((Math_Trigo.arcsine(self.cart_x/r))+offset)
                self.cart_tilt = (Math_Trigo.arctan(r/z))
            elif self.cart_y >= 0 and self.cart_x > 0:
                r = -((self.cart_x**2 + self.cart_y**2)**0.5)
                self.cart_pan = -((Math_Trigo.arcsine(self.cart_x/r))+offset)
                self.cart_tilt = (Math_Trigo.arctan(r/z))




    def send_cartesian_OSC(self):
        """
        Sends the OSC command in the cartesian coordinate system and for the zoom and intensity values.
        
        Input(already in the code, no arguments): 
            cartesian value from cartesian_to_spherical() function
            zoom and intensity values from the light_parameters() function
        """
        global pan
        global tilt
        global state
        fixture_id = 301
        if self.cart_pan < 0:
            state = True
        elif self.cart_pan >= 0:
            state = False

        client.send_message("/gma3/cmd", f'Fixture {self.fixture_id} At {self.cart_pan} Attribute "Pan"; At {self.cart_tilt} Attribute "Tilt"; At {light_parameters.zoom} Attribute "Zoom"')
        pan = self.cart_pan
        tilt = self.cart_tilt

standard_rectangle = pyglet.shapes.Rectangle(0, 0, 0, 0, color=(255, 255, 255), batch=batch)  #rectangle instance for the fixture rectangle
transformer = Transformation(303,os.path.join(base_dir, 'Calibration_files', f'Calibration.txt'),standard_rectangle, outofboundser)      #class instance of Transformation class
