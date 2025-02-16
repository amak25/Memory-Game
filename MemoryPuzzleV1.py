import random, pygame, sys
from pygame.locals import *

#Base Game Confiduration
FPS = 30 #Game frames per second
WindowWidth = 1280  #Window width
WindowHeight = 720  #Window height
RevealSpeed = 6 #Sliding and cover #
BoxSize = 100 #Box height and width (Pixels)
GapSize = 34  #Gap size between boxes (Pixels)

#Board Configuration
BoardWidth = 4 #Number of columns
BoardHeight = 4 #Number of rows
assert(BoardWidth * BoardHeight) % 2 == 0, 'Board needs even number of boxes set' #Ensures board is evenly set or program crashes
XMargin = int((WindowWidth - (BoardWidth * (BoxSize + GapSize))) / 2)
YMargin = int((WindowHeight - (BoardHeight * (BoxSize + GapSize))) / 2)

#Color Configuration (R,G,B)
Gray = (100,100,100)
Red = (255,0,0)
Blue = (0,0,255)
Yellow = (255,255,0)
DarkPurple = (102,0,102)
Orange = (255, 128, 0)
White = (255,255,255)
Green = (0,255,0)
Magenta = (255,51,153)
LimeGreen = (229,255,204)
LightBlue = (204, 229, 255)
Black = (0, 0, 0)
BeigeYellow = (235, 187, 110)

BackgroundColor = Gray
LightBackGroundColor = BeigeYellow
BoxColor = Black
BoxHighlightColor = LightBlue

#Game Objects
Donut = 'donut'
Square = 'square'
Diamond = 'diamod'
Lines = 'lines'
Oval = 'oval'

AllShapes = (Donut, Square, Diamond, Lines, Oval)
AllColors = (Red, Blue, Yellow, DarkPurple, Magenta, LimeGreen, LightBlue)
assert len(AllShapes) * len(AllColors) * 2 >= BoardWidth * BoardHeight, "Board Size exceeds number of defined shapes and colors"

#Main Function
def main():
    global FPSCLOCK, DISPLAYSURFACE
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURFACE = pygame.display.set_mode((WindowWidth, WindowHeight))
    
    MouseX = 0 #Stores x coordinate of mouse event
    MouseY = 0 #Stores y coordinate of mouse event
    pygame.display.set_caption('Memory Game')
    
    MainBoard = getRandomizedBoard() #Returns data structure that represents state of the board
    RevealedBoxes = generateRevealedBoxesData(False) #Returns data structure that represent covered boxes
    
    #Game Start Animation
    firstSelection = None  #Stores (x,y) of the first box clicked
    DISPLAYSURFACE.fill(BackgroundColor)
    StartGameAnimation(MainBoard)
    
    #Main Game Loop
    while True:   #Maintains Game State
        MouseClicked = False
        
        DISPLAYSURFACE.fill(BackgroundColor) #Draws window
        DrawBoard(MainBoard, RevealedBoxes)
        
        for event in pygame.event.get(): #Event handling loop
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE): #Quits game when user hits escape key
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION: #Changes MouseX and MouseY values when a user moves the mouse within window
                MouseX, MouseY = event.pos
            elif event.type == MOUSEBUTTONUP:
                MouseX, MouseY = event.pos
                MouseClicked = True
                
        #Checking which box the mouse cursor is over
        BoxX, BoxY = GetBoxAtPixel(MouseX, MouseY) #Board Coordinates of the box that the mouse coordinates are over
        if BoxX != None and BoxY != None: #Triggers when BoxX and BoxY both have 'none' values or when the MouseX and MouseY match the positions of one of the boxes
            #Mouse is currently over a box
            if not RevealedBoxes[BoxX][BoxY]: #Highlights Box if it hasn't already been uncovered to indicate to the User that they can click on it
                DrawHighlightBox(BoxX, BoxY)
            if not RevealedBoxes[BoxX][BoxY] and MouseClicked: #Checks for whether a mouse cusrsor is over a covered box and if the mouse has been clicked
                RevealBoxesAnimation(MainBoard, [(BoxX, BoxY)]) #Calls Box Reveal Animation for clicked box location
                RevealedBoxes[BoxX][BoxY] = True #Set the box as 'revealed' and updates game state
                
                if firstSelection == None: #Current box was the first box clicked
                    firstSelection = (BoxX, BoxY)
                else: #Current box was the second box clicked
                    #Check if there is a match between the two icons
                    icon1shape, icon1color = GetShapeAndColor(MainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = GetShapeAndColor(MainBoard, BoxX,BoxY)
                    
                    #Handles mismatched pair of icons 
                    if icon1shape != icon2shape or icon1color != icon2color: #Checks if either the shapes or colors of two icons don't match
                        # Icons don't match. Re-cover up both selections
                        pygame.time.wait(1000) # 1000 miliseconds = 1sec #Gives user a chance to see icon shape and color
                        CoverBoxesAnimation(MainBoard, [(firstSelection[0],firstSelection[1])])#,(BoxX, BoxY)])
                        CoverBoxesAnimation(MainBoard, [(BoxX, BoxY)])
                        RevealedBoxes[firstSelection[0]][firstSelection[1]] = False #Covers up first selction box
                        RevealedBoxes[BoxX][BoxY] = False
                    elif HasWon(RevealedBoxes): #Check if all pairs found
                        GameWonAnimation(MainBoard)
                        pygame.time.wait(2000)
                        
                        #Reset the board
                        MainBoard = getRandomizedBoard()
                        pygame.time.wait(2000) ####
                        RevealedBoxes = generateRevealedBoxesData(False) 
                        
                        #Show the fullt unrevealed board for 3 seconds
                        pygame.time.wait(1000) ####
                        DrawBoard(MainBoard, RevealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(3000)
                        
                        #Replay the start game animation
                        StartGameAnimation(MainBoard)
                    firstSelection = None #Resets firstSelection variable
                    
        #Redraw the screen and wait a clock tick.
        pygame.display.update()
        FPSCLOCK.tick(FPS)

#Revealed Boxes Data Structure
def generateRevealedBoxesData(val): #Creates a list of lists of Boolean values
    RevealedBoxes = []
    for i in range(BoardWidth):
        RevealedBoxes.append([val] * BoardHeight) #Creates the columns and appends them to RevealedBoxes
    return RevealedBoxes


#Board Data Structure
def getRandomizedBoard():
    #Get a list of every possible shape in every possible color
    icons = []
    for color in AllColors:
        for shape in AllShapes:
            icons.append((shape, color))
    
    #Shuffling and Truncating the List of All Icons
    random.shuffle(icons) # Randomize the order of the icons list
    NumIconsUsed = int(BoardWidth * BoardHeight / 2) #Calculates how many icons are needed
    icons = icons[:NumIconsUsed] * 2 # make two of each
    random.shuffle(icons)
    
    #Placong the Icons on the board #Create the board data structure, with randomly placed icons
    board = []
    for x in range(BoardWidth):
        column = []
        for y in range(BoardHeight):
            column.append(icons[0])
            del icons[0] # remove the icons as we assign them
        board.append(column)
    return board

def SplitIntoGroupsOf(GroupSize, TheList):
    #Splits a list into a list of lists, where the inner lists have at most GroupSize Number of items
    result = []
    for i in range(0, len(TheList), GroupSize):
        result.append(TheList[i:i + GroupSize])
    return result

#Coordinate conversian of Cartesian to Pixel Coordinates
def LeftTopCoordsOfBox(BoxX, BoxY):
    #Convert board coordinates to pixel coordinates
    left = BoxX * (BoxSize + GapSize) + XMargin
    top = BoxY * (BoxSize + GapSize) + YMargin
    return(left, top)

#Converting from Pixel Coordinates to Box Coordinates
def GetBoxAtPixel(x, y):
    for BoxX in range(BoardWidth):
        for BoxY in range(BoardHeight):
            left, top = LeftTopCoordsOfBox(BoxX, BoxY)
            BoxRect = pygame.Rect(left, top, BoxSize, BoxSize) #Rect objects have collidepoints that return True if they are interacted with
            if BoxRect.collidepoint(x, y):
                return(BoxX, BoxY)
    return(None, None)

#Drawing the icon, and syntactic suguar
def DrawIcon(shape, color, BoxX, BoxY):
    quarter = int(BoxSize * 0.25) # syntactic sugar
    half = int(BoxSize * 0.5) # Syntactic sugar
    
    left, top = LeftTopCoordsOfBox(BoxX, BoxY) # get pixel coords from board coards
    
    if shape == Donut:
        pygame.draw.circle(DISPLAYSURFACE, color, (left + half, top + half), half - 5)
        pygame.draw.circle(DISPLAYSURFACE, BackgroundColor, (left + half, top + half), quarter - 5)
        
    elif shape == Square:
        pygame.draw.rect(DISPLAYSURFACE, color, (left + quarter, top + quarter, BoxSize - half, BoxSize - half))
        
    elif shape == Diamond:
        pygame.draw.polygon(DISPLAYSURFACE, color, ((left + half, top), (left + BoxSize - 1, top + half), (left + half, top + BoxSize - 1), (left, top + half)))
        
    elif shape == Lines:
        for i in range(0, BoxSize, 4):
            pygame.draw.line(DISPLAYSURFACE, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAYSURFACE, color, (left + i, top + BoxSize - 1), (left + BoxSize - 1, top + i))
            
    elif shape == Oval:
        pygame.draw.ellipse(DISPLAYSURFACE, color, (left, top + quarter, BoxSize, half))
        
#Getting a Board Space's Icon's Shape and Color
def GetShapeAndColor(board, BoxX, BoxY):
    # shape value for x, y spot is stored in board[x][y][0]
    # color value for x, y spot is stored in board[x][y][1]
    return board[BoxX][BoxY][0], board[BoxX][BoxY][1]

#Draw Box Cover
def DrawBoxCovers(board, boxes, coverage):
    # Draws boxes being covered/revealed. "boxes" is a list of two-item lists, which gave the x & y spot of the box
    for Box in boxes:
        left, top = LeftTopCoordsOfBox(Box[0], Box[1])
        pygame.draw.rect(DISPLAYSURFACE, BackgroundColor, (left, top, BoxSize, BoxSize)) #Draws background color and rectangle for cover
        shape, color = GetShapeAndColor(board, Box[0], Box[1])
        DrawIcon(shape, color, Box[0], Box[1])
        if coverage > 0: #Only draw the cover if there is an coverage
            pygame.draw.rect(DISPLAYSURFACE, BoxColor, (left, top, coverage, BoxSize))
    pygame.display.update() #Triggers cover animation
    FPSCLOCK.tick(FPS)
    

#Revealing and Covering Animations
def RevealBoxesAnimation(board, BoxesToReveal):
    # Do the 'box reveal" animation
    for coverage in range(BoxSize, (-RevealSpeed) - 1, -RevealSpeed):
        DrawBoxCovers(board, BoxesToReveal, coverage)

def CoverBoxesAnimation(board, BoxesToCover):
    # Do the "box cover" animation
    for coverage in range(0, BoxSize + RevealSpeed, RevealSpeed):
        DrawBoxCovers(board, BoxesToCover, coverage)
        
#Drawing Entire Board
def DrawBoard(board, revealed):
    #Draws all of the boxes in their covered or revealed state
    for BoxX in range(BoardWidth):
        for BoxY in range(BoardHeight):
            left, top = LeftTopCoordsOfBox(BoxX, BoxY)
            if not revealed[BoxX][BoxY]:
                #Draw covered box
                pygame.draw.rect(DISPLAYSURFACE, BoxColor, (left, top, BoxSize, BoxSize))
            else:
                # Draw the (revealed) icon
                shape, color = GetShapeAndColor(board, BoxX, BoxY)
                DrawIcon(shape, color, BoxX, BoxY)
                
#Drawing Highlight
def DrawHighlightBox(BoxX, BoxY):
    left, top = LeftTopCoordsOfBox(BoxX, BoxY)
    pygame.draw.rect(DISPLAYSURFACE, BoxHighlightColor, (left - 5, top - 5, BoxSize + 10, BoxSize + 10), 4) #Creates colored outline to help user recognize a covered box is selectable
    
    
#Start Game Animation
def StartGameAnimation(board):
    # Randomly reveal the boxes 8 at a time
    CoveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BoardWidth):
        for y in range(BoardHeight):
            boxes.append((x, y))
    random.shuffle(boxes)
    BoxGroups = SplitIntoGroupsOf(8, boxes)
    
    # Revealing and covering the groups of boxes
    DrawBoard(board, CoveredBoxes)
    for BoxGroup in BoxGroups:
        RevealBoxesAnimation(board, BoxGroup) #Temporarily reveals box cover
        CoverBoxesAnimation(board, BoxGroup) #Covers box back up

#Game Won Animation
def GameWonAnimation(board):
    #Flash the Background Color when the player has won
    CoveredBoxes = generateRevealedBoxesData(True)
    color1 = LightBackGroundColor
    color2 = BackgroundColor
    
    for i in range(13):
        color1, color2 = color2, color1 # swap colors
        DISPLAYSURFACE.fill(color1)
        DrawBoard(board, CoveredBoxes)
        pygame.display.update()
        pygame.time.wait(600)
        
        
#Determinig if Player has won game
def HasWon(RevealedBoxes):
    # Returns True if all the boxes have been revealed, otherwise returns False
    for i in RevealedBoxes:
        if False in i:
            return False #Returns false as long as there are still covered 
    return True


# Main Function
if __name__ == '__main__':
    main()
        
        