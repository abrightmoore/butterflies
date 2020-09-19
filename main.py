# @TheWorldFoundry

import pygame
import random

class Physics:
    def __init__(self):
        pass

    def check_collides(self, rect_a, rect_b):
        ox_a, oy_a, w_a, h_a = rect_a
        ox_b, oy_b, w_b, h_b = rect_b

        # Assume we have collided, then prove if we haven't
        if ox_a + w_a -1 <= ox_b:
            return False
        elif ox_a >= ox_b + w_b:
            return False
        elif oy_a + h_a <= oy_b:
            return False
        elif oy_a >= oy_b + h_b:
            return False
        return True # Has collided

class World:
    def __init__(self, description):
        self.description = description
        self.elements = []
        self.colour_background = (0x90, 0xa0, 0x80)
        self.regions = []

    def get_description(self):
        return self.description

    def add_element(self, element):
        self.elements.append(element)

    def get_elements(self):
        return self.elements

    def tick(self):
        newElements = []
        for e in self.elements:
            if e.alive:
                e.update()
                newElements.append(e)
        self.elements = newElements


class Thing:
    def __init__(self, world, position, radius, name):
        self.alive = True
        self.world = world
        self.name = name
        self.position = position # Co-ordinates within the world
        self.velocity = [0.0, 0.0] # 2Direction (Radians), speed
        self.characteristics = {}
        self.animation = None
        self.age = 0
        self.size = radius
        self.physics = Physics()

        self.selected = False
        self.targeted = False

    def getColourPrimary(self):
        key = "ColourPrimary"
        if key not in self.characteristics:
            newColour = (128+random.randint(0,127), 128+random.randint(0,127), 128+random.randint(0,127), 255)
            self.characteristics[key] = newColour
        return self.characteristics[key]

    def get_rect(self):
        # Coordinates for the bounding box in the world
        ox, oy = self.position
        return (ox-self.size, oy-self.size, (self.size<<1), (self.size<<1))

    def handle_event_click(self, pos):
        click_x, click_y = pos

        ox, oy, w, h = self.get_rect()

        if ox <= click_x < ox+w and oy <= click_y < oy+h:
            return True # Within bounds

    def update(self):
        self.age += 1

    def draw(self, display):
        # Work out my position in the world, and how it maps onto the display
        ox, oy = display.position

        # Only draw this Thing if the Thing is within the display
        bounds = self.get_rect()
        #print bounds
        # print "draw",bounds
        if self.physics.check_collides((ox, oy, display.width, display.height), bounds):
            # print "Drawing",self.name
            minx, miny, w, h = bounds
            pygame.draw.rect(display.surface, self.getColourPrimary(), (minx, miny, w, h))

    def draw_highlight(self, display, colour):
        ox, oy = display.position

        # Only draw this Thing if the Thing is within the display
        bounds = self.get_rect()
        #print "draw",bounds
        if self.physics.check_collides((ox, oy, display.width, display.height), bounds):
            #print "Drawing",self.name
            minx, miny, w, h = bounds
            pygame.draw.rect(display.surface, colour, (minx, miny, w, h), 2)

class Display:
    def __init__(self, world, size, position):
        self.age = 0

        self.world = world
        self.size = size
        self.width, self.height = self.size
        self.position = position

        self.labelfont = None
        self.labelfontbig = None
        self.initialised = False
        self.surface = self.initialiseDisplay(self.world.get_description())

    def initialiseDisplay(self, description):
        print "Creating Surface and Window"
        pygame.init()
        surface = pygame.display.set_mode((self.width, self.height), pygame.SRCALPHA)
        print "Converting the surface to optimise rendering"
        surface.convert()
        print "Changing the caption"
        pygame.display.set_caption(description)
        self.labelfont = pygame.font.SysFont("monospace", 16)
        self.labelfontbig = pygame.font.SysFont("monospace", 32)
        pygame.key.set_repeat(100) # Milliseconds before new key event issued
        self.initialised = True
        return surface

    def draw(self):
        self.surface.fill(self.world.colour_background)
        for e in self.world.elements:
            if e.alive:
                e.draw(self)

    def update(self):
        self.age += 1
        unhandledEvents = []
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                # Clicked on a UI element?
                unhandledEvents.append(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll
                    unhandledEvents.append(event)
                if event.button == 5:  # Scroll
                    unhandledEvents.append(event)
                else:
                    unhandledEvents.append(event)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    unhandledEvents.append(event)
                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS or event.key == pygame.K_EQUALS:
                    unhandledEvents.append(event)

            else:
                unhandledEvents.append(event)

        pygame.display.update()

        return unhandledEvents

def main_loop():
    display = Display(World("Butterflies"), (800,800), (0,0))

    for i in xrange(0,10):
        thing = Thing(display.world,
                        (random.randint(0, display.surface.get_width()),random.randint(0, display.surface.get_height())),
                         random.randint(4,32), "Thing"+str(i))
        display.world.add_element(thing)
        print "New", thing.name, "at", thing.position

    # Main loop
    keepGoing = True
    iterationCount = 0

    selected = None
    targeted = None
    mousepos = -999,-999 # Default
    while keepGoing:
        if iterationCount % 10000 == 0:
            print "Number of elements",len(display.world.elements)
        iterationCount += 1

        # Tick the world
        # print "Ticking",len(display.world.elements)
        display.world.tick()

        # Draw the world
        #print "Drawing",len(display.world.elements)
        # Object rendering
        display.draw()
        # Special UI hints to the player
        if selected is not None:
            selected.draw_highlight(display, (0xa0, 0x00, 0x00, 0xff) )  # Red
        if targeted is not None:
            targeted.draw_highlight(display, (0x00, 0xa0, 0x00, 0xff) )  # Red

        for event in display.update():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEMOTION:
                mousepos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 1 == Left
                    for e in display.world.get_elements():
                        if e.alive:
                            if( e.handle_event_click(event.pos) ):
                                selected = e
                                e.selected = True
                                break
                if event.button == 3:  # 3 == Right
                    for e in display.world.get_elements():
                        if e.alive:
                            if( e.handle_event_click(event.pos) ):
                                targeted = e # Keep a record of who is selected. Overwrite duplicates.
                                e.targeted = e
                                break
            else:
                print event # Placeholder



if __name__ == '__main__':
    main_loop()

