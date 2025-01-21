import os
import json
from Transformation_Class import Transformation
from Labels_Class import Labels
from out_of_bounds import *
from Code import *

class TransManager():
    def __init__(self):
        self.transformations = [] #list of transformation instances
        self.labels = []    #list of label instances
        self.out_of_bounds_instances = [] #list of out_of_bounds instances
        self.rectangles = []
        self.rectangle_labels = []
        self.load_state()
        self.fixture_rectangle = None
        self.fixture_label = None
        self.selected_rectangles = []
        

    def add_transformation(self, fixture_id, rectangle, x, y):
        """
        Adds a new transformation instance to the transformation list
        """

        calibration_file = os.path.join(base_dir, 'Calibration_files', f'Calibration_{(fixture_id)}.txt')
        out_of_bounds_instance = Out_of_bounds()
        self.out_of_bounds_instances.append(out_of_bounds_instance)

        transformation = Transformation(fixture_id, calibration_file, rectangle, out_of_bounds_instance)
        self.transformations.append(transformation)

        label = Labels(transformation, out_of_bounds_instance)
        label.pan_label.x = x
        label.pan_label.y = y
        label.pan_label.font_size = window.height // 60
        label.tilt_label.x = x
        label.tilt_label.y = y - window.height // 50
        label.tilt_label.font_size = window.height // 60
        self.labels.append(label)
        
        self.save_state()


    def create_calibration_file(self, fixture_id, lines):
        """
        Writes the fixture ID and the list of 4 stage-corner coordinates to a new Calibration_x.txt file
        """
        filename = os.path.join(base_dir, 'Calibration_files', f'Calibration_{fixture_id}.txt')
        with open(filename, 'w') as file:
            for line in lines:
                line = str(line) + "\n"
                file.write(line)
            
    def add_fixture_rectangle(self, fixture_id):
        """
        Adds a fixture rectangle and label to the interface
        """
        
        self.fixture_rectangle = pyglet.shapes.Rectangle(x_middle, y_middle, window.height//12.5, window.height//12.5, color=(85, 85, 85), batch=batch)
        self.fixture_label = pyglet.text.Label(
            f"{fixture_id}",
            font_name="helvetica",
            font_size=window.height // 45,
            bold = True,
            x=self.fixture_rectangle.x,
            y=self.fixture_rectangle.y,
            anchor_x="left",
            anchor_y="bottom",
            batch=batch
            
            )

        
    def position_fixture(self):
        """
        Handles the logic of the fixture position input step
        """
        if keys[key.RIGHT]:
            self.fixture_rectangle.x += window.width / 1920
            self.fixture_label.x = self.fixture_rectangle.x
        if keys[key.LEFT]:
            self.fixture_rectangle.x -= window.width / 1920
            self.fixture_label.x = self.fixture_rectangle.x
        if keys[key.UP]:
            self.fixture_rectangle.y += window.height / 1080
            self.fixture_label.y = self.fixture_rectangle.y
        if keys[key.DOWN]:
            self.fixture_rectangle.y -= window.height / 1080
            self.fixture_label.y = self.fixture_rectangle.y

    def save_fixture_position(self, fixture_id, x, y):
        f_id = int(fixture_id)
        self.fixture_rectangle.x = x
        self.fixture_rectangle.y = y
        self.fixture_label.x = x
        self.fixture_label.y = y
        self.add_transformation(f_id, self.fixture_rectangle, x, y)
        self.rectangles.append(self.fixture_rectangle)
        self.rectangle_labels.append(self.fixture_label)

    def update_all_labels(self):
        """
        Calls the update_labels() function of the Labels() Class for all label instances
        """
        for label in self.labels:
            label.update_labels()

    def check_out_of_bounds(self):
        """
        Calls the out_of_bounds() function of the Out_of_bounds() Class for all out_of_bounds instances
        """
        for out_of_bounds_instance in self.out_of_bounds_instances:
            out_of_bounds_instance.out_of_bounds()


    def on_mouse_press(self, x, y, button, modifiers):
        """
        Handles mouse press events to toggle the color of fixture rectangles
        """
        for transformation in self.transformations:
            rectangle = transformation.fixture_rectangle
            if rectangle.x <= x <= rectangle.x + rectangle.width and rectangle.y <= y <= rectangle.y + rectangle.height:
                if rectangle in self.selected_rectangles:
                    # Toggle back to original color
                    rectangle.color = (85, 85, 85)
                    self.selected_rectangles.remove(rectangle)
                    transformation.selectionstate = False
                else:
                    # Change to new color
                    transformation.selectionstate = True
                    rectangle.color = (35, 50, 80)
                    self.selected_rectangles.append(rectangle)
                    

    def save_state(self):
        """
        Saves the state of the transformations to a JSON file
        """
        state = {
            "fixture_ids": [transformation.fixture_id for transformation in self.transformations],
            "positions": [(rectangle.x/window.width, rectangle.y/window.height) for rectangle in self.rectangles]
        }
        json_name = os.path.join(base_dir, 'Calibration_files', 'state.json')
        os.makedirs(os.path.dirname(json_name), exist_ok=True)  # Ensure the directory exists
        with open(json_name, 'w') as file:
            json.dump(state, file)

    def load_state(self):
        """
        Loads the state of the transformations from a JSON file
        """
        try:
            json_name = os.path.join(base_dir, 'Calibration_files', 'state.json')
            with open(json_name, 'r') as file:
                state = json.load(file)
                for fixture_id, position in zip(state["fixture_ids"], state["positions"]):
                    self.add_fixture_rectangle(fixture_id)
                    self.save_fixture_position(fixture_id, position[0]*window.width, position[1]*window.height)
        except FileNotFoundError:
            pass

    def delete_transformation(self, index):
        """
        Deletes a specific transformation instance by its index
        """
        if 0 <= index < len(self.transformations):
            del self.transformations[index]
            del self.labels[index]
            del self.out_of_bounds_instances[index]
            self.save_state()

transmanager = TransManager()