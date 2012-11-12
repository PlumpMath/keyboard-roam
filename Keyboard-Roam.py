# Keyboard-Roam.py
#
# Authors: Jeff and Stephen Barr

# Based on Tut-Roaming-Ralph.py with credits as follows:
#
#   Author: Ryan Myers
#   Models: Jeff Styers, Reagan Heller
#

# Per the table below, the keyboard is mapped in to 6 sections.
# Actions are bound to the sections as follows:
#
# Section 1 - Camera left
# Section 2 - Camera right
# Section 3 - Move forward
# Section 4 - Move backward
# Section 5 - Spawn a new bunny
# Section 6 - Move Ralph or camera (arrows)
#

import direct.directbase.DirectStart
from panda3d.core import CollisionTraverser,CollisionNode,AudioSound
from panda3d.core import CollisionHandlerQueue,CollisionRay
from panda3d.core import Filename,AmbientLight,DirectionalLight
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Vec3,Vec4,BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
import random, sys, os, math, string

SPEED = 0.5
PI = 3.14159
random.seed(1)

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)

class World(DirectObject):

    def __init__(self):
        
        self.keyMap = {"arrow_left":0, "arrow_right":0, "arrow_up":0, "arrow_down":0,
                       "cam-left":0, "cam-right":0,
                       "make-bunny":0, "do-something":0,
                       "ignore":0}
        base.win.setClearColor(Vec4(0,0,0,1))

        # Track all of the bunnies
        self.bunnies = []

        # Post the instructions

        self.title = addTitle("Keyboard Roaming")
        self.inst1 = addInstructions(0.95, "[Shift+ESC]: Quit")
        self.inst2 = addInstructions(0.90, "[Left Arrow]: Rotate Ralph Left")
        self.inst3 = addInstructions(0.85, "[Right Arrow]: Rotate Ralph Right")
        self.inst4 = addInstructions(0.80, "[Up Arrow]: Run Ralph Forward")
        self.inst4 = addInstructions(0.75, "[Down Arrow]: Run Ralph Backward")
        self.inst6 = addInstructions(0.70, "[A]: Rotate Camera Left")
        self.inst7 = addInstructions(0.65, "[S]: Rotate Camera Right")
        
        # Set up the environment
        #
        # This environment model contains collision meshes.  If you look
        # in the egg file, you will see the following:
        #
        #    <Collide> { Polyset keep descend }
        #
        # This tag causes the following mesh to be converted to a collision
        # mesh -- a mesh which is optimized for collision, not rendering.
        # It also keeps the original mesh, so there are now two copies ---
        # one optimized for rendering, one for collisions.  

        self.environ = loader.loadModel("models/world")      
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)
        
        # Create the main character, Ralph

        ralphStartPos = self.environ.find("**/start_point").getPos()
        self.ralph = Actor("models/ralph",
                                 {"run":"models/ralph-run",
                                  "walk":"models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setScale(0.3)
        self.ralph.setPos(ralphStartPos)

        # Create a floater object.  We use the "floater" as a temporary
        # variable in a variety of calculations.
        
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        # Shift+ESC key exits
        self.accept("shift-escape", sys.exit)

        # Tke keyboard is divided into six sections or tiles:
        #
        #         1                   2
        #  +----------------+  +-------------+
        #  | f1 ... F5      |  | F6 ... F12  |              
        #  +----------------+  +-------------+
        #
        #         3                         4
        #  +----------------+  +-------------------------+
        #  | ` 1 2 3 4 5 6  |  | 7 8 9 0 - = BACKSPACE   |
        #  | Q W E R T Y    |  |   Y U I O P [ ] \       |
        #  | A S D F G      |  | H J K L ; ' ENTER       |
        #  | Z X C V B      |  | N M , . /               |
        #  | CTRL WIN ALT   |  | SPACE ALT WIN MENU CTRL |
        #  +----------------+  +-------------------------+
        #
        #            5
        #  +----------------------+
        #  | PRT SCR PAUSE        |
        #  | INSERT HOME PAGEUP   |
        #  | DELETE END PAGEDOWN  |
        #  +----------------------+

        #             6
        #  +----------------------+
        #  | UP LEFT DOWN RIGHT   |
        #  +----------------------+
        #

        Section1 = ["f1", "f2", "f3", "f4", "f5"]

        Section2 = ["f6", "f7", "f8", "f9", "f10", "f11", "f12"]
        
        Section3 = ["`", "1", "2", "3", "4", "5", "6",
                    "q", "w", "e", "r", "t", "y",
                    "a", "s", "d", "f", "g",
                    "lshift", "z", "x", "c", "v", "b"]

        Section4 = ["7", "8", "9", "0", "backspace",
                    "y", "u", "i", "o", "p", "[", "]", "\\",
                    "h", "j", "k", "l", ";", "'", "enter",
                    "n", "m", ",", ".", "/", "rshift"]

        Section5 = ["print_screen", "scroll_lock", "pause",
                    "insert", "home", "page_up",
                    "delete", "end", "page_down"]

        Section6 = ["arrow_left", "arrow_right",
                    "arrow_up", "arrow_down"]

        # Map each section
        action = "cam-left"
        for k in Section1:
            self.accept(k,                    self.setKey, [action, 1])
            self.accept("shift-" + k,         self.setKey, [action, 1])
            self.accept(k + "-up",            self.setKey, [action, 0])
            self.accept("shift-" + k + "-up", self.setKey, [action, 0])

        action = "cam-right"
        for k in Section2:
            self.accept(k,                    self.setKey, [action, 1])
            self.accept("shift-" + k,         self.setKey, [action, 1])
            self.accept(k + "-up",            self.setKey, [action, 0])
            self.accept("shift-" + k + "-up", self.setKey, [action, 0])

        action = "arrow_up"
        for k in Section3:
            self.accept(k,                    self.setKey, [action, 1])
            self.accept("shift-" + k,         self.setKey, [action, 1])
            self.accept(k + "-up",            self.setKey, [action, 0])
            self.accept("shift-" + k + "-up", self.setKey, [action, 0])

        action = "arrow_down"
        for k in Section4:
            self.accept(k,                    self.setKey, [action, 1])
            self.accept("shift-" + k,         self.setKey, [action, 1])
            self.accept(k + "-up",            self.setKey, [action, 0])
            self.accept("shift-" + k + "-up", self.setKey, [action, 0])

        action = "make-bunny"
        for k in Section5:
            self.accept(k,                    self.setKey, [action, 1])
            self.accept("shift-" + k,         self.setKey, [action, 1])
            self.accept(k + "-up",            self.setKey, [action, 0])
            self.accept("shift-" + k + "-up", self.setKey, [action, 0])

        for k in Section6:
            self.accept(k,                    self.setKey, [k, 1])
            self.accept("shift-" + k,         self.setKey, [k, 1])
            self.accept(k + "-up",            self.setKey, [k, 0])
            self.accept("shift-" + k + "-up", self.setKey, [k, 0])

        taskMgr.add(self.move,"moveTask")

        # Game state variables
        self.isMoving = False

        # Set up the camera
        
        base.disableMouse()
        base.camera.setPos(self.ralph.getX(),self.ralph.getY()+10,2)
        
        # We will detect the height of the terrain by creating a collision
        # ray and casting it downward toward the terrain.  One ray will
        # start above ralph's head, and the other will start above the camera.
        # A ray may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.

        self.cTrav = CollisionTraverser()

        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0,0,1000)
        self.ralphGroundRay.setDirection(0,0,-1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.ralphGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.ralphGroundColNp = self.ralph.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0,0,1000)
        self.camGroundRay.setDirection(0,0,-1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

        # Uncomment this line to see the collision rays
        #self.ralphGroundColNp.show()
        #self.camGroundColNp.show()
       
        # Uncomment this line to show a visual representation of the 
        # collisions occuring
        #self.cTrav.showCollisions(render)
        
        # Create some lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.3, .3, .3, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(-5, -5, -5))
        directionalLight.setColor(Vec4(1, 1, 1, 1))
        directionalLight.setSpecularColor(Vec4(1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))

        # Set up some sounds
        self.runSound   = base.loader.loadSfx("sounds/54779__bevangoldswain__running-hard-surface.wav")
        self.bumpSound  = base.loader.loadSfx("sounds/31126__calethos__bump.wav")
        self.spawnSound = base.loader.loadSfx("sounds/51710__bristolstories__u-chimes3.mp3")
    
    #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value
    
    # Lines the bunnies up behind Ralph
    def positionBunnies(self):
        ralphH = self.ralph.getH() * (3.1415927 / 180.0)
        X = self.ralph.getX()
        Y = self.ralph.getY()
        print "Ralph at " + str(X) + ", " + str(Y) + ", heading " + str(ralphH)

        dX = math.cos(ralphH + PI/2.0)
        dY = math.sin(ralphH + PI/2.0)
        i = 1
        for bunny in self.bunnies:
            bX = X + (dX * 2 * i)
            bY = Y + (dY * 2 * i)
            bunny.setX(bX)
            bunny.setY(bY)
            print "    Bunny at " + str(bX) + ", " + str(bY)
            bunny.setZ(self.ralph.getZ() + 0.5 + random.random())
            bunny.lookAt(self.ralph)
            i = i + 1
        print

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):

        # Ignore certain keys
        if (self.keyMap["ignore"]!=0):
            self.keyMap["ignore"] = 0
            print("Ignoring key...")

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.

        base.camera.lookAt(self.ralph)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())

        # save ralph's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = self.ralph.getPos()

        # If a move-key is pressed, move ralph in the specified direction.
        
        if (self.keyMap["arrow_left"]!=0):
            self.ralph.setH(self.ralph.getH() + 300 * globalClock.getDt())
            self.positionBunnies()

        if (self.keyMap["arrow_right"]!=0):
            self.ralph.setH(self.ralph.getH() - 300 * globalClock.getDt())
            self.positionBunnies()

        if (self.keyMap["arrow_up"]!=0):
            self.ralph.setY(self.ralph, -50 * globalClock.getDt())
            self.positionBunnies()

        if (self.keyMap["arrow_down"]!=0):
            self.ralph.setY(self.ralph, 50 * globalClock.getDt())
            self.positionBunnies()

        # If an object creation key is pressed, create an object of the desired type
        if (self.keyMap["make-bunny"]!=0):
            self.keyMap["make-bunny"] = 0           # Avoid multiplying like rabbits!
            if (self.spawnSound.status() != AudioSound.PLAYING):
                self.spawnSound.play()
            new_bunny = Actor("models/Bunny2")
            new_bunny.reparentTo(render)
            new_bunny.setScale(0.3)
            self.bunnies.append(new_bunny)
            self.positionBunnies()

        # Handle the catch-all do-something keys
        if (self.keyMap["do-something"]!=0):
            self.keyMap["do-something"] = 0
            print "Something!"

        # If ralph is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if (self.keyMap["arrow_up"]!=0) or (self.keyMap["arrow_down"]!=0) or (self.keyMap["arrow_left"]!=0) or (self.keyMap["arrow_right"]!=0):
            if self.isMoving is False:
                self.ralph.loop("run")
                self.isMoving = True
                if (self.runSound.status() != AudioSound.PLAYING):
                    self.runSound.play()
        else:
            if self.isMoving:
                self.ralph.stop()
                self.ralph.pose("walk",5)
                self.isMoving = False
                self.runSound.stop()

        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.

        camvec = self.ralph.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 10.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
            camdist = 10.0
        if (camdist < 5.0):
            base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
            camdist = 5.0

        # Now check for collisions.

        self.cTrav.traverse(render)

        # Adjust ralph's Z coordinate.  If ralph's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.

        entries = []
        for i in range(self.ralphGroundHandler.getNumEntries()):
            entry = self.ralphGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.ralph.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.ralph.setPos(startpos)
            if (self.bumpSound.status() != AudioSound.PLAYING):
                self.bumpSound.play()

        # Keep the camera at one foot above the terrain,
        # or two feet above ralph, whichever is greater.
        
        entries = []
        for i in range(self.camGroundHandler.getNumEntries()):
            entry = self.camGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+1.0)
        if (base.camera.getZ() < self.ralph.getZ() + 2.0):
            base.camera.setZ(self.ralph.getZ() + 2.0)
            
        # The camera should look in ralph's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above ralph's head.
        
        self.floater.setPos(self.ralph.getPos())
        self.floater.setZ(self.ralph.getZ() + 2.0)
        base.camera.lookAt(self.floater)

        return task.cont


w = World()
run()

