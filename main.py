import cv2
from screeninfo import get_monitors
import mss
import numpy as np
import keyboard
import win32api, win32con
import ctypes
import time
import math
import random
import colorsys

max_x_SCREEN_SIZE = 0
max_y_SCREEN_SIZE = 0
for m in get_monitors():
    if (m.x+m.width) > max_x_SCREEN_SIZE:
        max_x_SCREEN_SIZE = m.x+m.width
    if (m.y+m.height) > max_y_SCREEN_SIZE:
        max_y_SCREEN_SIZE = m.y+m.height
FULL_SCREEN_SIZE = (max_x_SCREEN_SIZE, max_y_SCREEN_SIZE)

def hsv_to_hsl(h, s, v):
    l = 0.5 * v  * (2 - s)
    s = v * s / (1 - math.fabs(2*l-1))
    return [h, s, l]

def GetFrame(x,y,w,h):
	with mss.mss() as sct:
		monitor = {"top": y, "left": x, "width": w, "height": h}
		sct_img = sct.grab(monitor)
		return np.asarray(sct_img)[:,:,:3]

def getScreenshot():
    return GetFrame(0,0,FULL_SCREEN_SIZE[0],FULL_SCREEN_SIZE[1]).astype(np.uint8).copy()
        
def readImg(imgDir):
    return cv2.imread(imgDir).astype(np.uint8)[:,:,:3]

def getImginImg(template, matchTo, returnTresh=False):
    template_height, template_width, template_channels = template.shape
    matchTo_height, matchTo_width, matchTo_channels = matchTo.shape
    res = cv2.matchTemplate(matchTo,template,cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)    
    ## enable for testing
    '''
    print(min_val)
    print(max_val)
    print(min_loc)
    print(max_loc)
    print(template.shape)
    while True:
        res = matchTo.copy()
        cv2.rectangle(res, min_loc, (min_loc[0] + template.shape[1], min_loc[1] + template.shape[0]), (255,0,255), 2)
        cv2.imshow('r', res)
        cv2.waitKey(100)
    '''
    print(min_val)
    if returnTresh:
        return min_val
    if min_val>700000:
        return ((False, False), (False, False))
    return (min_loc, (min_loc[0] + template_width, min_loc[1] + template_height))
    
    
BRUSH_CONTROL_OFFSET = (85, 108)
COLOR_CONTROL_OFFSET = (125, 108)

OUTER_WINDOW_OFFSET = (53, 82)
OUTER_WINDOW_SIZE = (502, 502)

BUILD_WINDOW_OFFSET = (50, 50)
BUILD_WINDOW_OFFSET = (BUILD_WINDOW_OFFSET[0] + OUTER_WINDOW_OFFSET[0], BUILD_WINDOW_OFFSET[1] + OUTER_WINDOW_OFFSET[1])
BUILD_WINDOW_SIZE = (400, 400)

BRUSH_SCALE_MAX = (85, 156)
BRUSH_SCALE_MIN = (85, 485)

COLOR_HUE_MAX = (85, 164) #156 includes gray
COLOR_HUE_MIN = (85, 485)
    
    
def drawControls(img):
    img = img.copy()
    cv2.circle(img, BRUSH_CONTROL_OFFSET, 14, (255, 0, 255), -1)
    cv2.circle(img, COLOR_CONTROL_OFFSET, 14, (0, 2, 255), -1)
    
    cv2.rectangle(img, OUTER_WINDOW_OFFSET, 
                 (OUTER_WINDOW_OFFSET[0] + OUTER_WINDOW_SIZE[0], OUTER_WINDOW_OFFSET[1] + OUTER_WINDOW_SIZE[1]),
                 (255,255,0), 3)
                 
    cv2.rectangle(img, BUILD_WINDOW_OFFSET, 
                 (BUILD_WINDOW_OFFSET[0] + BUILD_WINDOW_SIZE[0], BUILD_WINDOW_OFFSET[1] + BUILD_WINDOW_SIZE[1]),
                 (255,0,0), 3)

    if controlsOpen():
        cv2.line(img, BRUSH_SCALE_MIN, BRUSH_SCALE_MAX, (0,255,0), 8)
        cv2.line(img, (COLOR_CONTROL_OFFSET[0], BRUSH_SCALE_MIN[1]), (COLOR_CONTROL_OFFSET[0], BRUSH_SCALE_MAX[1]), (255,0,0), 8)

    return img
    
def mousedown():
    ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0) # left down
    
def mouseup():
    ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0) # left up
    
def click(delay = 0.05):
    mousedown()
    time.sleep(delay)
    mouseup()
    
def moveMouse(x, y):
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(x/1920*65535.0), int(y/1080*65535.0))
    
BrushControlOpen = False
def toggleBrushControl():
    moveMouseInWindow(BRUSH_CONTROL_OFFSET[0], BRUSH_CONTROL_OFFSET[1])
    click(delay = 0.01)
    time.sleep(0.02)
    
def openBrushControls():
    global BrushControlOpen
    toggleBrushControl() # might need to switch from color control
    while (not controlsOpen()) and (not keyboard.is_pressed("q")):
        toggleBrushControl()
    BrushControlOpen = True
        
def closeBrushControls():
    global BrushControlOpen
    while (controlsOpen()) and (not keyboard.is_pressed("q")):
        toggleBrushControl()
    BrushControlOpen = False
    
def setBrushSize(x):
    height = ((BRUSH_SCALE_MAX[1]-BRUSH_SCALE_MIN[1])*x) + BRUSH_SCALE_MIN[1]
    openBrushControls()
    moveMouseInWindow(85, height)
    time.sleep(0.01)
    click(delay = 0.01)
    time.sleep(0.01)
    closeBrushControls()
        
ColorControlOpen = False
def toggleColorControl():
    moveMouseInWindow(COLOR_CONTROL_OFFSET[0], COLOR_CONTROL_OFFSET[1])
    click(delay = 0.01)
    time.sleep(0.02)
    
def openColorControls():
    global ColorControlOpen
    toggleColorControl() # might need to switch from brush control
    while (not controlsOpen()) and (not keyboard.is_pressed("q")):
        toggleColorControl()
    ColorControlOpen = True
        
def closeColorControls():
    global ColorControlOpen
    while (controlsOpen()) and (not keyboard.is_pressed("q")):
        toggleColorControl()
    ColorControlOpen = False
    
def setColorHueFloat(x):
    height = ((COLOR_HUE_MAX[1]-COLOR_HUE_MIN[1])*x) + COLOR_HUE_MIN[1]
    openColorControls()
    moveMouseInWindow(85, height)
    time.sleep(0.01)
    click(delay = 0.01)
    time.sleep(0.01)
    closeColorControls()
    
def setColorLightnessFloat(x):
    height = ((COLOR_HUE_MAX[1]-COLOR_HUE_MIN[1])*x) + COLOR_HUE_MIN[1]
    openColorControls()
    moveMouseInWindow(125, height)
    time.sleep(0.01)
    click(delay = 0.01)
    time.sleep(0.01)
    closeColorControls()
    
def setColor(Hue, Lightness):
    setColorHueFloat(Hue)
    setColorLightnessFloat(Lightness)
    
def drawDotScale(x, y):
    drawDot(x*BUILD_WINDOW_SIZE[0], y*BUILD_WINDOW_SIZE[1])
        
    
    
topBarImg = readImg("./reference/topBar.png")
screenshot = getScreenshot()

loc = getImginImg(topBarImg, screenshot)
if not loc[0][0]:
    exit("img not found")
loc = loc[0]
loc = [loc[0], loc[1]]
windowSize = [854, 600]
topbarOffset = [-3, -4]
loc[0] = loc[0]+topbarOffset[0]
loc[1] = loc[1]+topbarOffset[1]

def moveMouseInWindow(x,y):
    global loc
    moveMouse(x+loc[0], y+loc[1])
    
def drawDot(x, y):
    global loc
    global BUILD_WINDOW_OFFSET
    moveMouse(x+loc[0]+BUILD_WINDOW_OFFSET[0], y+loc[1]+BUILD_WINDOW_OFFSET[1])
    click(delay = 0.01)
    
def controlsOpen():
    global loc
    time.sleep(0.01)
    windowImg = GetFrame(loc[0], loc[1], windowSize[0], windowSize[1])
    if (windowImg[135][65] < 35).all():
        return (windowImg[135][65] > 20).all()
    return False

    
    
    
DRAWING = "pythonLogo.png"
    
toDraw = cv2.imread("./reference/" + DRAWING)

def round(x):
    if x%1 < 0.5:
        return int(math.floor(x))
    return int(math.ceil(x))


    
    
def getHSLofImgAtScale(x, y):
    global toDraw
    template_height, template_width, template_channels = toDraw.shape
    pixX = round(x*template_width) - 1
    pixY = round(y*template_height) - 1
    if pixX < 0:
        pixX = 0
    if pixY < 0:
        pixY = 0
    [b, g, r] = toDraw[pixY, pixX]
    pix = [r, g, b] = [r/255, g/255, b/255]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return (h, s, l)
    
closeColorControls()

setBrushSize(0.075)
setColorLightnessFloat(0)
   
hsv = [112, 100, 77.35]   
hsl = hsv_to_hsl(hsv[0]/360, hsv[1]/100, hsv[2]/100)

setColor(hsl[0], hsl[2])

## DO DRAWING ##
grid_size = 70
FilledList = np.zeros((grid_size, grid_size))

HUE_SIMILARITY = 0.1
LIT_SIMILARITY = 0.1

def xyFilled(x, y):
    return FilledList[y, x]

def drawAllForHSL(h, s, l):
    global FilledList
    toFill = []
    
    for y in range(grid_size):
        for x in range(grid_size):
            xS = x/(grid_size-1)
            yS = y/(grid_size-1)
            hue, sat, lit = getHSLofImgAtScale(xS, yS)
            if abs(hue-h) < HUE_SIMILARITY:
                if abs(lit-l) < LIT_SIMILARITY: #if similar to requested color
                    if not xyFilled(x, y):
                        toFill.append([x, y])
    print("filling: " + str(len(toFill)) + " / " + str(grid_size**2))
    setColor(h, l)
    for p in toFill:
        if keyboard.is_pressed("q"):
            exit('you hit "q"')
        xS = p[0]/(grid_size-1)
        yS = p[1]/(grid_size-1)
        drawDotScale(xS, yS)
        FilledList[p[1], p[0]] = 1

while (FilledList == False).any(): #while not placed all pixles
    Drawn = False
    y=0
    for yRow in FilledList:
        x=0
        for xVal in yRow: #loop through the list
            if (not xVal) and (not Drawn): #if this value has not been dealt with
                xS = x/(grid_size-1)
                yS = y/(grid_size-1)
                hue, saturation, lightness = getHSLofImgAtScale(xS, yS)
                drawAllForHSL(hue, saturation, lightness)
                Drawn = True
            x+=1
        y+=1