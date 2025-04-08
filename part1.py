# Group#: B27
# Student Names: Pan Tisapramotkul, Joshan Gill

"""
    This program implements a variety of the snake 
    game (https://en.wikipedia.org/wiki/Snake_(video_game_genre))
"""

import threading
import queue        #the thread-safe queue from Python standard library

from tkinter import Tk, Canvas, Button
import random, time

class Gui():
    """
        This class takes care of the game's graphic user interface (gui)
        creation and termination.
    """
    def __init__(self):
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial gamer score.
        """
        #some GUI constants
        scoreTextXLocation = 60
        scoreTextYLocation = 15
        textColour = "white"
        #instantiate and create gui
        self.root = Tk()
        self.canvas = Canvas(self.root, width = WINDOW_WIDTH, 
            height = WINDOW_HEIGHT, bg = BACKGROUND_COLOUR)
        self.canvas.pack()
        #create starting game icons for snake and the prey
        self.snakeIcon = self.canvas.create_line(
            (0, 0), (0, 0), fill=ICON_COLOUR, width=SNAKE_ICON_WIDTH)
        self.preyIcon = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=ICON_COLOUR, outline=ICON_COLOUR)
        #display starting score of 0
        self.score = self.canvas.create_text(
            scoreTextXLocation, scoreTextYLocation, fill=textColour, 
            text='Your Score: 0', font=("Helvetica","11","bold"))
        #binding the arrow keys to be able to control the snake
        for key in ("Left", "Right", "Up", "Down"):
            self.root.bind(f"<Key-{key}>", game.whenAnArrowKeyIsPressed)

    def gameOver(self):
        """
            This method is used at the end to display a
            game over button.
        """
        gameOverButton = Button(self.canvas, text="Game Over!", 
            height = 3, width = 10, font=("Helvetica","14","bold"), 
            command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)
    

class QueueHandler():
    """
        This class implements the queue handler for the game.
    """
    def __init__(self):
        self.queue = gameQueue
        self.gui = gui
        self.queueHandler()
    
    def queueHandler(self):
        '''
            This method handles the queue by constantly retrieving
            tasks from it and accordingly taking the corresponding
            action.
            A task could be: game_over, move, prey, score.
            Each item in the queue is a dictionary whose key is
            the task type (for example, "move") and its value is
            the corresponding task value.
            If the queue.empty exception happens, it schedules 
            to call itself after a short delay.
        '''
        try:
            while True:
                task = self.queue.get_nowait()
                if "game_over" in task:
                    gui.gameOver()
                elif "move" in task:
                    points = [x for point in task["move"] for x in point]
                    gui.canvas.coords(gui.snakeIcon, *points)
                elif "prey" in task:
                    gui.canvas.coords(gui.preyIcon, *task["prey"])
                elif "score" in task:
                    gui.canvas.itemconfigure(
                        gui.score, text=f"Your Score: {task['score']}")
                self.queue.task_done()
        except queue.Empty:
            gui.root.after(100, self.queueHandler)


class Game():
    '''
        This class implements most of the game functionalities.
    '''
    def __init__(self):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue = gameQueue
        self.score = 0

        #starting length and location of the snake
        #note that it is a list of tuples, each being an
        # (x, y) tuple. Initially its size is 5 tuples.       
        self.snakeCoordinates = [(455, 55), (465, 55), (475, 55),
                                 (485, 55), (495, 55)]
        #initial direction of the snake
        self.direction = "Left"
        self.gameNotOver = True
        self.createNewPrey()

    def superloop(self) -> None: 
        """
            This method implements a main loop
            of the game. It constantly generates "move" 
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
        SPEED = 0.15     #speed of snake updates (sec)
        while self.gameNotOver:
            self.move()
            time.sleep(SPEED)

    def whenAnArrowKeyIsPressed(self, e) -> None:
        """ 
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on 
            the key that was pressed by the gamer.
            Use as is.
        """
        currentDirection = self.direction
        #ignore invalid keys
        if (currentDirection == "Left" and e.keysym == "Right" or 
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return
        self.direction = e.keysym

    def move(self) -> None:
        """ 
            This method implements what is needed to be done
            for the movement of the snake.
            It generates a new snake coordinate. 
            If based on this new movement, the prey has been 
            captured, it adds a task to the queue for the updated
            score and also creates a new prey.
            It also calls a corresponding method to check if 
            the game should be over. 
            The snake coordinates list (representing its length 
            and position) should be correctly updated.
        """
        # Calculate new head position based on current direction
        new_head = self.calculateNewCoordinates()
        # Insert the new head position at the front of the snake's body
        self.snakeCoordinates.insert(0, new_head)

        # Determine bounding boxes for the snake's head and prey
        snake_half_width = SNAKE_ICON_WIDTH / 2

        prey_coords = gui.canvas.coords(gui.preyIcon)

        # Calculate the bounding box for the prey
        prey_box = (
            prey_coords[0],
            prey_coords[1],
            PREY_ICON_WIDTH 
        )

        # Calculate the bounding box for the snake's head
        snake_box = (
            self.snakeCoordinates[0][0] - snake_half_width,
            self.snakeCoordinates[0][1] - snake_half_width,
            SNAKE_ICON_WIDTH)

        def is_box_inside(inner_box: tuple[float, float, float], outer_box: tuple[float, float, float]) -> bool:
            """
            Checks whether 'inner' box is completely within 'outer' box.

            Each box is represented as (x, y, width).
            The check is inclusive of boundaries.
            """
            x1, y1, w1 = inner_box
            x2, y2, w2 = outer_box

            margin = (SNAKE_ICON_WIDTH - PREY_ICON_WIDTH)/2 # to account for pixel rounding errors

            return (
                (x2 - x1) <= margin and 
                (y2 - y1) <= margin and
                (x2 + w2 - x1 + w1) >= margin and
                (y2 + w2 - y1 + w1)  >= margin
            )

        # Determine if prey was eaten by checking box containment
        if SNAKE_ICON_WIDTH >= (PREY_ICON_WIDTH):
            prey_eaten = is_box_inside(prey_box, snake_box) 
        else:
            prey_eaten = is_box_inside(snake_box, snake_box)

        if prey_eaten:
            # Increase score and generate a new prey
            # Do not have to remove tail because we need to simulate snake growing 
            self.score += 1
            self.createNewPrey()
        else:
            # If no prey was eaten, remove tail to simulate movement
            self.snakeCoordinates.pop()

        # Send updated score and movement to the queue
        self.queue.put_nowait({"score": self.score})
        self.queue.put_nowait({"move": self.snakeCoordinates})

        # check if the game should be over 
        self.isGameOver(self.snakeCoordinates)

    def calculateNewCoordinates(self) -> tuple: 
        """
            This method calculates and returns the new 
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of 
            head of the snake.
            It is used by the move() method.    
        """
        # Get the head coordinates of the snake
        headX, headY = self.snakeCoordinates[0]

        if self.direction == 'Up': # If up add head on top
            new_head = (headX, headY-10)
        elif self.direction == 'Down': # If down add head to the bottom
            new_head = (headX, headY+10)
        elif self.direction == 'Left': # If left add head to the left
            new_head = (headX-10, headY)
        elif self.direction == 'Right': # If right add head to the right
            new_head = (headX+10, headY)

        # return new head of the snake 
        return new_head 

    def isGameOver(self, snakeCoordinates) -> None: 
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        head_x, head_y = snakeCoordinates[0]

        # Check if the snake's head is out of bounds or collides with itself
        if (
            head_x < 0 or head_x > WINDOW_WIDTH or
            head_y < 0 or head_y > WINDOW_HEIGHT or
            (head_x, head_y) in snakeCoordinates[1:]
        ):
            self.gameNotOver = False
            self.queue.put({"game_over": True}) # Add game over task to the queue

    def createNewPrey(self) -> None: 
        """ 
            This methods picks an x and a y randomly as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). [you need to replace 5 with a constant]
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        THRESHOLD = 15   #sets how close prey can be to borders
        Prey_half_width = PREY_ICON_WIDTH / 2  

        # Generate random coordinates for prey within the window
        while True:
            x = random.randint(THRESHOLD, WINDOW_WIDTH - THRESHOLD)
            y = random.randint(THRESHOLD, WINDOW_HEIGHT - THRESHOLD)

            # Ensure prey do not spawn on snake coordinates
            if all(abs(x - sx) > SNAKE_ICON_WIDTH and abs(y - sy) > SNAKE_ICON_WIDTH for sx, sy in self.snakeCoordinates):
                break
        
        # Calculate the rectangle coordinates for the prey
        coords = (x - Prey_half_width, y - Prey_half_width, x + Prey_half_width, y + Prey_half_width)
        self.queue.put({"prey": coords})


if __name__ == "__main__":
    #some constants for our GUI
    WINDOW_WIDTH = 500           
    WINDOW_HEIGHT = 300 
    SNAKE_ICON_WIDTH = 15
    PREY_ICON_WIDTH = 10 # constant PREY_ICON_WIDTH     

    BACKGROUND_COLOUR = "green"   #you may change this colour if you wish
    ICON_COLOUR = "yellow"        #you may change this colour if you wish

    gameQueue = queue.Queue()     #instantiate a queue object using python's queue class

    game = Game()        #instantiate the game object

    gui = Gui()    #instantiate the game user interface
    
    QueueHandler()  #instantiate the queue handler    
    
    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's own event loop
    gui.root.mainloop()