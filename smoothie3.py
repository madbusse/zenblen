### Zenblen Internship Technical
### Smoothie Kiosk GUI
### Madeline Busse
### Sources consulted: 
    # https://www.pysimplegui.org/en/latest/
    # https://realpython.com/pysimplegui-python/
    # https://realpython.com/python-gui-with-wxpython/
    # https://www.tutorialspoint.com/pysimplegui/pysimplegui_text_element.htm
    # https://www.tutorialspoint.com/pysimplegui/pysimplegui_button_element.htm

# This smoothie kiosk uses class-based threading between the gui and backend.

# To run: "python3 smoothie3.py"

### Helpful notes
    # NB: BACKEND IS NON_FUNCTIONAL; just a prototype due to time constraints
        # Tkinter is non-threadable... consider using client/server instead?
    # wxPython allows dynamical layout of elements
    # PySimpleGUI uses nested Python lists to lay out its elements

### Further implementation would include:
    # adding a build your own smoothie option 
    # fixing "go back"/"order again" bug - "resuing layouts" error
    # add functionality to add multiple smoothies to order
    # add images of smoothies
    # add sound effects
    # get gui/backend integration working

### LIBRARIES
# using the PySimpleGUI package bc it integrates Tkinter, PyQt, wxPython, & Remi
# if not installed locally, run "python3 -m pip install pysimplegui"

# using PIL (Python Imaging Library) for image display
# if not installed locally, run "python3 -m pip install --upgrade pip"
#                               "python3 -m pip install --upgrade Pillow"

import PySimpleGUI as sg
from PIL import Image, ImageTk
import threading
import time

# Backend - prototype (not finished)
# having issues bc tkinter is "non-threadable" - consider alternate method
# perhaps client/server setup?
class SmoothieBackend:
    """ 
    Class for the Backend implementation of our Smoothie Kiosk.
    """
    def __init__(self):
        """
        Initialization for SmoothieBackend class.
        
        Inputs: None
        
        Outputs: None
        """
        # we will use a queue to track orders
        self.order_queue = []

        # track inventory in a dictionary, ingredient : quantity
        self.inventory = {
            'strawberries': 100,
            'bananas': 50,
            'orange juice': 20,
            'mango': 10,
            'blueberries': 300,
            'ice': 50,
            'greek yogurt': 20
        }

        # smoothie recipes, for keeping track of inventory
        # dictionary, ingredient : quantity
        self.strawb_recipe = {
            'strawberries': 5,
            'bananas': 1,
            'greek yogurt': 1,
            'ice': 1
        }
        self.mango_recipe = {
            'mango': 1,
            'bananas': 1,
            'ice': 1
        }
        self.multifruit_recipe = {
            'blueberries': 10,
            'strawberries': 5,
            'mango': 0.5,
            'greek yogurt': 1,
            'orange juice': 1
        }

        # track order counts in a dictionary, smoothie : qty ordered
        self.order_cts = {
            'strawberry smoothie': 0,
            'mango smoothie': 0,
            'multifruit smoothie': 0
        }
        # int for tracking profits
        self.profits = 0

    def process_orders(self):
        """
        Function for checking for and processing a smoothie order.
        Inputs: None
        Outputs: None
        """
        while True:
            # while queue is not empty, i.e. there is an order
            if self.order_queue:
                order = self.order_queue.pop(0) # order is str, smoothie name
                
                # increment order count
                self.order_cts[order] += 1
                
                # decrement inventory & increment profits, by smoothie type
                if order == 'Strawberry Smoothie':
                    self.profits += 5
                    for key, value in self.strawb_recipe.items():
                        self.inventory[key] -= value
                if order == 'Mango Smoothie':
                    self.profits += 4
                    for key, value in self.mango_recipe.items():
                        self.inventory[key] -= value
                if order == 'Multifruit Smoothie':
                    self.profits += 6
                    for key, value in self.multifruit_recipe_recipe.items():
                        self.inventory[key] -= value

    # need to call place_order function from gui, when a smoothie is ordered
    # smoothie = str, name of smoothie
    def place_order(self, smoothie):
        """
        Function for placing a smoothie order so it may be processed.
        Indirectly calls "process order" function by making queue non-empty.
        
        Inputs: smoothie, str, the name of the smoothie ordered in the gui.
        
        Outputs: None
        """
        self.order_queue.append(smoothie)

# GUI
class SmoothieGUI:
    """
    Class for the frontend/GUI implementation of our smoothie kiosk.
    """
    def __init__(self, backend):
        """
        Initialization function for GUI object.
        
        Inputs: backend, Class SmoothieBackend, a backend instance

        Outputs: None
        """
        # initialize gui with corresponding backend
        self.backend = backend

        # initialize attribute for current smoothie order
        self.current_order = None

        # setting up layouts for each screen
        self.screen_size = (500, 800)

        # loading in images of smoothies
        strawb_img = Image.open('strawb.png')
        strawb_img.thumbnail((400, 400))
        strawb_img.save('strawb_resize.png')
        orange_img = Image.open('orange.png')
        orange_img.thumbnail((400, 400))
        orange_img.save('orange_resize.png')
        
        # designing screen layouts
        
        # screen 1: welcome
        self.layout_welcome = [
            [sg.Text('Looking for a healthy pick-me-up? \n You are in luck! \n Grab a quick & delicious smoothie! \n Tap the smoothie to order.' \
                     , justification='center', font=('Baloo 2', 30))],
            [sg.Button(key="Next", image_filename="strawb_resize.png")]
        ]
        
        #screen 2: menu
        self.layout_menu = [
            [sg.Text('Smoothie Menu', font=('Baloo 2', 30))],
            [sg.Button('Strawberry Smoothie - $5'), sg.Button('Mango Smoothie - $4')],
            [sg.Button('Multifruit Smoothie - $6')],
            [sg.Text('Ingredients', font=('Baloo 2', 30))],
            [sg.Text('Strawberry Smoothie: strawberries, bananas, greek yogurt, ice.', font=('Baloo 2', 15))],
            [sg.Text('Mango Smoothie: mango, banana, ice.', font=('Baloo 2', 15))],
            [sg.Text('Multifruit Smoothie: strawberries, orange juice, blueberries, mango, greek yogurt.', font=('Baloo 2', 12))]
        ]
        
        # screen 3: placing order
        # we do not set up here bc the price is dependent on the smoothie being ordered,
        # so we will create this layout in a later function.
        self.layout_place_order = None
        
        # screen 4: making smoothie (progress bar)
        self.layout_making_smoothie = [
            [sg.Text('Making Your Smoothie...', font=('Baloo 2', 30))],
            [sg.ProgressBar(100, orientation='h', size=(20, 20), key='progressbar')],
        ]

        # screen 5: thank you
        self.layout_thank_you = [
            [sg.Text('Thank You for Your Order!', font=('Baloo 2', 30))],
            [sg.Text('Enjoy your smoothie :) \n Tap the smoothie to start a new order.', \
                     font=('Baloo 2', 20), justification="center")],
            [sg.Button(key="Return to Menu", image_filename="orange_resize.png")],
            [sg.Button('Exit')]
        ]

        # setting up intial window
        self.window = sg.Window('Smoothie Kiosk', layout=self.layout_welcome, \
                                size=self.screen_size, element_justification='c', finalize=True)

    def run(self):
        """
        Function for running the GUI and checking for events.

        Inputs: None

        Outputs: None
        """
        # main loop for gui
        while True:

            # checking for events (clicks)
            event, values = self.window.read()

            # window closed
            if event == sg.WINDOW_CLOSED:
                break

            # welcome -> menu
            elif event == 'Next':
                self.show_menu_screen()
            
            # smoothie selected
            elif event in ('Strawberry Smoothie - $5', 'Mango Smoothie - $4', 'Multifruit Smoothie - $6'):
                self.show_place_order_screen(event)
                self.current_order = event
            # elif event == 'Place Order':
            #     self.show_place_order_screen(self.current_order)
            
            # order placed
            elif event == 'Place Order':
                # communicate the order to the backend
                #smoothie = values['smoothie']
                #self.backend.place_order(smoothie)
                
                self.show_making_smoothie_screen()
            
            # go back
            elif event == 'Back':
                self.show_menu_screen()
            
            # place another order
            elif event == 'Return to Menu':
                self.current_order = None
                self.show_welcome_screen()
            
            # user exit
            elif event == 'Exit':
                break

        self.window.close()

    def show_welcome_screen(self):
        """
        Function for showing welcome screen.
        
        Inputs: None
        
        Outputs: None
        """
        self.window.close()
        self.window = sg.Window('Smoothie Kiosk', layout=self.layout_welcome, \
                                size=self.screen_size, element_justification='c', finalize=True)

    def show_menu_screen(self):
        """
        Function for showing menu screen.
        
        Inputs: None
        
        Outputs: None
        """
        self.window.close()
        self.window = sg.Window('Smoothie Kiosk', layout=self.layout_menu, \
                                size=self.screen_size, element_justification='c', finalize=True)

    def show_place_order_screen(self, smoothie):
        """
        Function for showing place order screen.
        
        Inputs: smoothie, str, the name of the smoothie ordered
        
        Outputs: None
        """
        self.window.close()
        
        # computing smoothie price
        price = None
        if smoothie == 'Strawberry Smoothie - $5':
            price = 5
        elif smoothie == 'Mango Smoothie - $4':
            price = 4
        elif smoothie == 'Multifruit Smoothie - $6': 
            price = 6
        str_price = str(price)
        
        # now that we know the price, we can design the layout
        self.layout_place_order = [
            [sg.Text('Place Your Order', font=('Baloo 2', 30))],
            [sg.Text('Total to Pay: $ ' + str_price, font=('Baloo 2', 20))],
            [sg.Button('Place Order'), sg.Button('Back')]
        ]
        self.window = sg.Window('Smoothie Kiosk', layout=self.layout_place_order, \
                                size=self.screen_size, element_justification='c', finalize=True)

    def show_making_smoothie_screen(self):
        """
        Function for showing smoothie in progress screen.
        
        Inputs: None
        
        Outputs: None
        """
        self.window.close()
        self.window = sg.Window('Smoothie Kiosk', layout=self.layout_making_smoothie, \
                                size=self.screen_size, element_justification='c', finalize=True)

        # progressbar - 5 seconds to make smoothie
        for i in range(101):
            time.sleep(0.05)
            self.window['progressbar'].update_bar(i)

        self.show_thank_you_screen()

    def show_thank_you_screen(self):
        """
        Function for showing thank you screen.
        
        Inputs: None
        
        Outputs: None
        """
        self.window.close()
        self.window = sg.Window('Smoothie Kiosk', layout=self.layout_thank_you, \
                                size=self.screen_size, element_justification='c', finalize=True)


if __name__ == '__main__':
    
    # setting color theme
    sg.theme('LightGreen4')

    #backend = SmoothieBackend()
    backend = None
    gui = SmoothieGUI(backend)
    gui.run()

    # commenting out threading bc of error due to tkinter:

    #backend_thread = threading.Thread(target=backend.process_orders)
    #gui_thread = threading.Thread(target=gui.run)

    #backend_thread.start()
    #gui_thread.start()

    #backend_thread.join()
    #gui_thread.join()
