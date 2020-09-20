# @TheWorldFoundry

import pygame
import random
import math

class Colour:
    def __init__(self):
        self.colours = {
            "black": (0x05,0x03,0x09,0xff),
            "white": (0xff,0xff,0xff,0xff),
            "green": (0x00, 0xa0, 0x00, 0xff),
            "red": (0xa0, 0x00, 0x00, 0xff),
            "brown": (0x70, 0x60, 0x70, 0xff),
            "transparent": (0x00,0x00,0x00,0xff),
            "world_background": (0x80,0x70,0x90,0xff)
        }

    def get(self, key):
        if key not in self.colours:
            # Issue a new random colour if we didn't find the requested one
            self.colours[key] = (128+random.randint(0,127), 128+random.randint(0,127), 128+random.randint(0,127), 255)
        return self.colours[key]

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
        self.colour_background = Colour().get("world_background")
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

class Thing(object):
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
            newColour = Colour().get("random")
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

class Butterfly(Thing):
    def __init__(self, display, name, position_limits):
        position = random.randint(0, display.surface.get_width()),random.randint(0, display.surface.get_height())
        radius = random.randint(4,32)
        super(Butterfly,self).__init__(display.world, position, radius, name)
        self.position_limits = position_limits

        display.world.add_element(self)

        # Animation hints
        self.facing = random.randint(0,359) # Initialise facing a random direction - Degrees
        # Geometry
        self.main_wing = []
        self.sub_wing = []
        self.body = []
        self.antennae = []

        self.main_wing, self.sub_wing, self.body, self.antennae = self.create_geometry()

        c = Colour()
        self.colours = []
        for i in xrange(0,random.randint(3,21)):
            self.colours.append(c.get("random"+str(i)))

        self.texture = self.plot_wing()
        self.texture_body = self.plot_body()
        self.wings_up = False
        self.img_render_buffer = pygame.Surface((self.texture.get_width(), self.texture.get_height()), pygame.SRCALPHA)

    def plot_wing(self):
        #

        bounds = self.get_rect()
        minx, miny, w, h = bounds
        cw = w>>1
        ch = h>>1

        img = pygame.Surface((w,h),pygame.SRCALPHA)

        points = []
        for px, py in self.sub_wing:
            px = px*float(cw)+cw
            py = py*float(ch)+ch
            points.append((px, py)) # Scaled to the dimensions of the image, and offset from centre
        pygame.draw.polygon(img, self.colours[1], points, 0)
        pygame.draw.polygon(img, self.colours[0], points, 1)


        points = []
        for px, py in self.main_wing:
            px = px*float(cw)+cw
            py = py*float(ch)+ch
            points.append((px, py)) # Scaled to the dimensions of the image, and offset from centre
        pygame.draw.polygon(img, self.colours[1], points, 0)
        pygame.draw.polygon(img, self.colours[0], points, 1)

        img2 = pygame.transform.flip(img, False, True)

        img.blit(img2, (0,0))

        pygame.image.save(img, "butterfly_left_side_"+self.name+".png")
        return img

    def plot_body(self):
        #

        bounds = self.get_rect()
        minx, miny, w, h = bounds
        cw = w>>1
        ch = h>>1

        img = pygame.Surface((w,h),pygame.SRCALPHA)

        points = []
        for px, py in self.body:
            px = px*float(cw)+cw
            py = py*float(ch)+ch
            points.append((px, py)) # Scaled to the dimensions of the image, and offset from centre
        pygame.draw.polygon(img, self.colours[0], points, 0)

        points = []
        for px, py in self.antennae:
            px = px*float(cw)+cw
            py = py*float(ch)+ch
            points.append((px, py)) # Scaled to the dimensions of the image, and offset from centre
        pygame.draw.lines(img, self.colours[2], False, points)



        img2 = pygame.transform.flip(img, False, True)

        img.blit(img2, (0,0))

        pygame.image.save(img, "butterfly_left_side_body"+self.name+".png")
        return img

    def create_geometry(self):
        # Main left wing, if oriented right along the 0 degrees line

        main = [
                (0.0, 0.0), (0.2, 0.0), (0.9, 0.8), (1.0, 0.9), (0.9, 1.0), (0.2, 0.8),
                 (0.1, 0.7), (0.0, 0.0)
        ]

        # Sub left wing, if oriented right along the 0 degrees line

        sub = [
            (0.0, 0.0), (0.1,0.6), (0.0, 0.8), (-0.3, 0.96), (-0.5, 0.9), (-0.8, 0.6),
            (-1.0, 0.3), (-0.9, 0.2), (0.0, 0.0)
        ]

        # Body segments, if oriented right along the 0 degrees line
        body = [
            (0.4, 0.0), (0.38, 0.1), (-0.96, 0.06), (-1.9, 0.0), (0.4, 0.0)
        ]

        antennae = [
            (0.4, 0.05), (0.6, 0.2), (1.0, 0.4)
        ]

        return main, sub, body, antennae


    def update(self):
        self.age += 1

        if self.physics.check_collides(self.position_limits, self.get_rect()):
            x, y = self.position
            x += random.randint(-1, 1)
            y += random.randint(-1, 1)
            self.position = x,y

            if random.randint(1,40) == 1:
                if self.wings_up:
                    self.wings_up = False
                else:
                    self.wings_up = True

            if random.randint(1,10) == 1:
                self.facing = (self.facing + random.randint(-15,15))%360


        elif self.targeted is None and self.selected is None:
            self.alive = False # Offscreen... FOREVER!
            self.targeted = False
            self.selected = False
            self.wings_up = False

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
            cw = w>>1
            ch = h>>1

            # Draw the wings and the body

            # Work out what the plot locations of the creature are based on scales, transforms and rotations


            self.img_render_buffer.fill((0,0,0,0))

            self.img_render_buffer.blit(self.texture_body, (0,0)) # Body


            wings = self.texture
            offset = 0
            if self.wings_up == True:
                wings = pygame.transform.scale(self.texture, (w, h>>1))
                offset = (h>>2)
            self.img_render_buffer.blit(wings, (0, 0+offset)) # Wings

            cw = minx+cw
            ch = miny+ch

            final_img = pygame.transform.rotate(self.img_render_buffer, self.facing)
            minx = cw-(final_img.get_width()>>1)
            miny = ch-(final_img.get_height()>>1)

            display.surface.blit(final_img, (minx, miny))

            # pygame.draw.rect(display.surface, self.getColourPrimary(), (minx, miny, w, h))

class Player:
    def __init__(self):
        self.score = 0
        self.inventory = [ Jar(), Jar(), Jar(), Jar()]
        self.stats = Statistics()

class Jar():
    def __init__(self):
        self.contains = None
        self.uses = 0
        self.colour = Colour().get("black")

    def place_in(self, thing):
        # Replace the contents of the jar with the nominated thing
        # If there was something in the jar to start with, returns that thing

        result = self.contains
        if self.contains is None:
            self.contains = thing
        self.uses += 1

        return result

    def draw(self, display, rect):
        # Render this jar within the nominated rectangle
        # ToDo: Replace with art asset

        colour = self.colour

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

class Statistics:
    def __init__(self):
        self.select_fail = 0
        self.select_success = 0

class Tools:
    def __init__(self, display, name, rect):
        self.rect = rect
        print self.rect
        self.name = name
        self.alive = True
        self.colour_background = Colour().get("brown")
        self.colour_border = Colour().get("black")
        display.world.add_element(self)

    def get_height(self):
        x,y,w,h = self.rect
        return h

    def update(self):
        pass

    def draw(self, display):
        display.surface.fill(self.colour_background,self.rect)
        pygame.draw.rect(display.surface, self.colour_border, self.rect, 2)

    def handle_event_click(self, pos):
        click_x, click_y = pos

        ox, oy, w, h = self.rect

        if ox <= click_x < ox+w and oy <= click_y < oy+h:
            return True # Within bounds

    def draw_highlight(self, display, colour):
        pass

def main_loop():
    display = Display(World("Butterflies"), (800,800), (0,0))
    ui_colours = Colour()
    tools = Tools(display, "Toolbar", (0, display.surface.get_height()-(display.surface.get_height()>>3),
                                       display.surface.get_width(), display.surface.get_height()>>3))

    display_world_region = (0,0,display.surface.get_width(),display.surface.get_height()-tools.get_height())

    for i in xrange(0,random.randint(10,100)):
        Butterfly(display, ("Thing"+str(i)), display_world_region)

    # Main loop
    player = Player()

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
        if selected is not None and selected.alive:
            selected.draw_highlight(display, ui_colours.get("red") )  # Red
        if targeted is not None and targeted.alive:
            targeted.draw_highlight(display, ui_colours.get("green") )  # Green

        for event in display.update():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEMOTION:
                mousepos = event.pos
                if selected is not None:
                    selected.position = mousepos
                    print selected.position
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 1 == Left
                    for e in display.world.get_elements():
                        if e.alive:
                            if( e.handle_event_click(event.pos) ):
                                selected = e
                                e.selected = True
                                player.stats.select_success += 1
                                break
                if event.button == 3:  # 3 == Right
                    for e in display.world.get_elements():
                        if e.alive:
                            if( e.handle_event_click(event.pos) ):
                                targeted = e # Keep a record of who is selected. Overwrite duplicates.
                                e.targeted = e
                                if targeted == selected:
                                    selected.selected = None
                                    selected = None
                                    targeted.targeted = None
                                    targeted = None
                                player.stats.select_success += 1
                                break
            else:
                print event # Placeholder



if __name__ == '__main__':
    main_loop()

