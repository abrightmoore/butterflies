# @TheWorldFoundry

import pygame
import random
import math
import os

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
        icon_size = 64
        position = random.randint(0, display.surface.get_width()),random.randint(display.surface.get_height()>>1, display.surface.get_height())
        radius = random.randint(icon_size>>1,128)
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
        jitter = 0.1
        self.main_wing = self.jitter(self.main_wing, jitter)
        self.sub_wing = self.jitter(self.sub_wing, jitter)

        c = Colour()
        self.colours = []
        for i in xrange(0,random.randint(3,21)):
            if random.randint(1,10) == 1:
                keys = c.colours.keys()
                self.colours.append(c.get(keys[random.randint(0,len(keys)-1)]))
            else:
                self.colours.append(c.get("random"+str(i)))

        self.pattern_scaler = 0.00001 + random.random() * 0.01
        self.texture = self.plot_wing()
        self.texture_body = self.plot_body()

        if os.path.exists("samples"):
            sample = pygame.Surface((self.texture.get_width(),self.texture.get_height()),pygame.SRCALPHA)
            sample.blit(self.texture_body,(0,0))
            sample.blit(self.texture, (0, 0))

            pygame.image.save(pygame.transform.rotate(sample,90), "samples/butterfly_"+self.name+str(random.randint(1000000000,9999999999))+".png")


        self.wings_up = False
        self.img_render_buffer = pygame.Surface((self.texture.get_width(), self.texture.get_height()), pygame.SRCALPHA)

        self.img_cache = None


        icon = pygame.Surface((self.texture.get_width(), self.texture.get_height()), pygame.SRCALPHA)
        icon.blit(self.texture_body, (0, 0))
        icon.blit(self.texture, (0, 0))
        self.icon = pygame.transform.scale(pygame.transform.rotate(icon,90),(icon_size,icon_size))

    def draw_highlight(self, display, colour):
        ox, oy = display.position

        # Only draw this Thing if the Thing is within the display
        bounds = self.get_rect()
        #print "draw",bounds
        if self.physics.check_collides((ox, oy, display.width, display.height), bounds):
            #print "Drawing",self.name
            minx, miny, w, h = bounds
            # pygame.draw.rect(display.surface, colour, (minx, miny, w, h), 2)
            pygame.draw.circle(display.surface, colour, (int(minx+(w>>1)), int(miny+(h>>1))), (w>>1), random.randint(1,4))


    def jitter(self, points, amount):
        result = []
        for (x, y) in points:
            x = x * 0.9
            y = y * 0.9
            x += (random.random() * amount * float(random.randint(-1, 1)))
            y += (random.random() * amount * float(random.randint(-1, 1)))
            # print x,y

            # Clamp
            if x > 1.0: x = 1.0
            elif x < -1.0: x = -1.0
            if y > 1.0: y = 1.0
            elif y < 0.0: y = 0.0
            result.append((x,y))

        return result

    def plot_wing(self):
        #

        bounds = self.get_rect()
        minx, miny, w, h = bounds
        cw = w>>1
        ch = h>>1

        img = pygame.Surface((w,h),pygame.SRCALPHA)
        img1 = pygame.Surface((w, h), pygame.SRCALPHA)
        img2 = pygame.Surface((w, h), pygame.SRCALPHA)

        points = []
        for px, py in self.sub_wing:
            px = px*float(cw)+cw
            py = py*float(ch)+ch
            points.append((px, py)) # Scaled to the dimensions of the image, and offset from centre
        pygame.draw.polygon(img1, self.colours[1], points, 0)
        points_sub = points

        points = []
        for px, py in self.main_wing:
            px = px*float(cw)+cw
            py = py*float(ch)+ch
            points.append((px, py)) # Scaled to the dimensions of the image, and offset from centre
        pygame.draw.polygon(img2, self.colours[1], points, 0)
        points_main = points

        offsetx = random.randint(-100,100)
        offsety = random.randint(-100, 100)
        for x in xrange(0, img.get_width()):
            for y in xrange(ch, ch+(img.get_height()>>1)):
                R,G,B,A = img1.get_at((x,y))
                if A is not 0:
                    dx = x-cw+offsetx
                    dy = y-ch+offsety
                    val = abs(dx*dy*self.pattern_scaler)
                    colhere = self.colours[(int(val)%(len(self.colours)-2))+1]
                    img1.set_at((x,y),colhere)

        offsetx = random.randint(-100,100)
        offsety = random.randint(-100, 100)
        for x in xrange(0, img.get_width()):
            for y in xrange(ch, ch+(img.get_height()>>1)):
                R,G,B,A = img2.get_at((x,y))
                if A is not 0:
                    dx = x-cw+offsetx
                    dy = y-ch+offsety
                    val = abs(dx*dy*self.pattern_scaler)
                    colhere = self.colours[(int(val)%(len(self.colours)-2))+1]
                    img2.set_at((x,y),colhere)



        pygame.draw.polygon(img1, self.colours[0], points_sub, 1)
        pygame.draw.polygon(img2, self.colours[0], points_main, 1)
        img.blit(img1, (0,0))
        img.blit(img2, (0,0))

        if False: # Ignore - complications in implementation for now
            spot_col = self.colours[random.randint(0,len(self.colours)-1)]
            col_black = Colour().get("black")
            if self.size > 16:
                for i in xrange(0,random.randint(5,18)): # Spots!
                    radius = random.randint(3,8)
                    # print radius
                    posx = random.randint(cw>>1, 3*(cw>>1))
                    posy = random.randint(0, ch>>1)
                    r2 = radius*radius
                    for x in xrange(posx-radius, posx+radius+1):
                        dx = x - posx
                        for y in xrange(posy - radius, posy + radius + 1):
                            if 0 <= x < img.get_width() and 0 <= y < img.get_height():
                                R, G, B, A = img.get_at((x, y))
                                if A is not 0:
                                    # print "Hello"
                                    dy = y-posy
                                    d2 = dx*dx+dy*dy
                                    if d2 < r2:
                                        img.set_at((x, y), col_black)
                                    elif d2 == r2:
                                        img.set_at((x, y), col_black)



        img3 = pygame.transform.flip(img, False, True)

        img.blit(img3, (0,0))

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

        # pygame.image.save(img, "butterfly_left_side_body"+self.name+".png")
        return img

    def create_geometry(self):
        # Main left wing, if oriented right along the 0 degrees line

        main = [
                (-0.2, 0.0), (0.2, 0.0), (0.9, 0.8), (1.0, 0.9), (0.9, 1.0), (0.2, 0.8),
                 (0.1, 0.7), (-0.2, 0.0)
        ]

        # Sub left wing, if oriented right along the 0 degrees line

        sub = [
            (-0.02, 0.0), (0.05,0.6), (0.0, 0.8), (-0.3, 0.96), (-0.5, 0.9), (-0.8, 0.6),
            (-1.0, 0.3), (-0.9, 0.2), (-0.02, 0.0)
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
            delta = self.size>>4
            if delta < 2:
                delta = 2
            x += random.randint(-delta, delta)
            y += random.randint(-delta, delta)

            self.position = x, y

            if random.randint(1,40) == 1:
                self.img_cache = None
                if self.wings_up:
                    self.wings_up = False
                else:
                    self.wings_up = True

            if random.randint(1,10) == 1:
                self.img_cache = None
                self.facing = (self.facing + random.randint(-15,15))%360

            if self.selected or self.targeted:
                self.wings_up = False
                self.img_cache = None

        else:
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
            final_img = self.img_cache # Avoid rotation if we can
            if final_img is None: # Rebuild the butterfly
                # Work out what the plot locations of the creature are based on scales, transforms and rotations
                self.img_render_buffer.fill((0,0,0,0))

                self.img_render_buffer.blit(self.texture_body, (0,0)) # Body

                wings = self.texture
                offset = 0
                if self.wings_up == True:
                    wings = pygame.transform.scale(self.texture, (w, h>>1))
                    offset = (h>>2)
                self.img_render_buffer.blit(wings, (0, 0+offset)) # Wings

                final_img = pygame.transform.rotate(self.img_render_buffer, self.facing)
                self.img_cache = final_img

            cw = minx+cw
            ch = miny+ch

            minx = cw-(final_img.get_width()>>1)
            miny = ch-(final_img.get_height()>>1)

            display.surface.blit(final_img, (minx, miny))

            # pygame.draw.rect(display.surface, self.getColourPrimary(), (minx, miny, w, h))

class Player:
    def __init__(self):
        self.score = 0
        self.inventory = [ Jar(), Jar(), Jar(), Jar()]
        self.stats = Statistics()
        self.position = (0,0)
        self.direction = 0
        self.speed = 0

    def add_score(self, score):
        self.score += score

    def draw(self, display):
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

        fontlist = pygame.font.get_fonts()

        self.initialised = False
        self.surface = self.initialiseDisplay(self.world.get_description())
        self.labelfont = pygame.font.SysFont(fontlist[0], 32)  #random.randint(0,len(fontlist)-1)], 32)
        self.labelfontbig = pygame.font.SysFont(fontlist[0], 64)  #random.randint(0,len(fontlist)-1)], 64)


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
        # print self.rect
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
    logo_img = pygame.image.load("WF4_t_w.png")
    logo = logo_img
    logo_shrink = 0
    logo_max_shrink = logo_img.get_width()>>1
    ui_colours = Colour()

    if False: # Ignore for now - more ambitious game than my time allows in the jam period
        tools = Tools(display, "Toolbar", (0, display.surface.get_height()-(display.surface.get_height()>>3),
                                           display.surface.get_width(), display.surface.get_height()>>3))

        display_world_region = (0,0,display.surface.get_width(),display.surface.get_height()-tools.get_height())

    display_world_region = (0,0,display.surface.get_width(),display.surface.get_height())

    particles = []
    scoreticles = []

    MAX_ITEMS = 30

    for i in xrange(0,random.randint(10,50)):
        Butterfly(display, ("Thing"+str(i)), display_world_region)

    # Main loop
    pygame.mixer_music.load("ABMusic.mp3")
    pygame.mixer_music.play(-1)


    player = Player()

    keepGoing = True
    iterationCount = 0

    selected = None
    targeted = None

    instructions_done = False

    targets = []
    mousepos = -999,-999 # Default
    while keepGoing:

        if iterationCount > 300 and logo_shrink < logo_max_shrink:
            logo = pygame.transform.scale(logo_img,(logo_img.get_width()-logo_shrink, logo_img.get_height()-logo_shrink))
            logo_shrink += 1
        if iterationCount % 10000 == 0:
            print "Number of elements",len(display.world.elements)

        iterationCount += 1

        potentials = display.world.get_elements()
        if iterationCount %500 == 0:
            if random.randint(1, 10) == 1 and len(targets) > 0:
                targets.pop(0)
            if len(potentials) > 0:
                potential = potentials[random.randint(0, len(potentials) - 1)]
                if potential.alive and potential not in targets:
                    targets.append(potential)  # Add a new target

        if len(potentials) < MAX_ITEMS:
            if random.randint(1,100) == 1:
                Butterfly(display, ("Butterfly"), display_world_region)



        # Tick the world
        # print "Ticking",len(display.world.elements)
        display.world.tick()

        # Draw the world
        #print "Drawing",len(display.world.elements)
        # Object rendering
        display.draw()
        # Special UI hints to the player
        if selected is not None and selected.alive:
            selected.draw_highlight(display, (136, 255, 242, random.randint(30,170)) )  # Red
        if targeted is not None and targeted.alive:
            targeted.draw_highlight(display, ui_colours.get("green") )  # Green

        cursor_x = 2
        newTargets = []
        for s in targets:
            # Draw targeting object
            if s.icon is not None and s.alive:
                display.surface.blit(s.icon,(cursor_x, 2))

                if instructions_done == False: # Hint for the player
                    s.draw_highlight(display, (136, 255, 242, random.randint(30, 170)))
                    pygame.draw.line(display.surface, (136, 255, 242, random.randint(30, 170)), (0,s.icon.get_height()+2), (display.surface.get_width()>>1,s.icon.get_height()+2))

                # Is there a match?
                if s.physics.check_collides(s.get_rect(), (cursor_x,2,s.icon.get_width(),s.icon.get_height())):
                    # print "Matched!"
                    score = s.size*10
                    centre_pos = (cursor_x+(s.icon.get_width()>>1),(s.icon.get_height()>>1))
                    # print len(targets)
                    if len(targets) == 1:
                        score = score+score
                        score_img = display.labelfont.render("! CLEAR BONUS x2 !", 1, (255, 255, 255, 255))
                        scoreticles.append((((display.surface.get_width()>>1)-(score_img.get_width()>>1),score_img.get_height()>>1), 0.6, score_img))
                    player.add_score(score)

                    score_img = display.labelfont.render(str(int(score)), 1, (255, 255, 255, 255))
                    scoreticles.append((centre_pos, 0.3, score_img ))

                    s.alive = False

                    if len(particles) < 30:
                        for i in xrange(0, random.randint(5,15)):
                            particles.append((centre_pos, 0.3-random.random()*(0.6), 0.1-random.random()*0.2))
                else:
                    newTargets.append(s)
                cursor_x += 2 + s.icon.get_width()
        targets = newTargets

        newParticles = []
        for p in particles:
            (x, y), dx, dy = p
            pygame.draw.circle(display.surface, (255, 255, 255, 255), (int(x),int(y)), random.randint(2,5), 0)
            x += dx
            y += dy
            dy += 0.01
            if 0 <= x < display.surface.get_width() and 0 <= y < display.surface.get_height():
                newParticles.append(((x,y), dx, dy))
        particles = newParticles

        newScores = []
        for s in scoreticles:
            (x,y), dy, score_img = s
            y += dy
            dy += 0.01
            if y < display.surface.get_height():
                display.surface.blit(score_img,(x,y))
                newScores.append(((x,y),dy,score_img))
        scoreticles = newScores


        # HUD

        scorelabel_w = display.labelfontbig.render(str(int(player.score)), 1, (255, 255, 255, 255))
        scorelabel_b = display.labelfontbig.render(str(int(player.score)), 1, (0, 0, 0, 128))
        slw = scorelabel_w.get_width()
        slh = scorelabel_w.get_height()
        display.surface.blit(scorelabel_b, ((display.surface.get_width()>>1)-(slw>>1), display.surface.get_height()-slh))
        display.surface.blit(scorelabel_w,
                             ((display.surface.get_width() >> 1) - (slw >> 1)-4, display.surface.get_height() - slh-4))

        if iterationCount == 500 or ((iterationCount %800 == 0) and instructions_done == False): # Repeat if no click
            score_img = display.labelfont.render("Left click select & move to match butterflies", -20, (136, 255, 242, random.randint(30,170)))
            scoreticles.append((((display.surface.get_width() >> 1) - (score_img.get_width() >> 1),
                                 64), 0.6, score_img))
            score_img = display.labelfont.render("Rick click to release", -20, (136, 255, 242, random.randint(30,170)))
            scoreticles.append((((display.surface.get_width() >> 1) - (score_img.get_width() >> 1),
                                 96), 0.6, score_img))

        display.surface.blit(logo, (display.surface.get_width()-logo.get_width(),0))

        # Event loop

        for event in display.update():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEMOTION:
                mousepos = event.pos
                if selected is not None:
                    selected.position = mousepos
                    # print selected.position
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # 1 == Left
                    instructions_done = True
                    for e in display.world.get_elements():
                        if e.alive:
                            if( e.handle_event_click(event.pos) ):
                                selected = e
                                e.selected = True
                                player.stats.select_success += 1
                                break
                if event.button == 3:  # 3 == Right
                    if selected is not None:
                        selected.selected = False
                        selected = None
            else:
                pass
                # print event # Placeholder



if __name__ == '__main__':
    main_loop()

