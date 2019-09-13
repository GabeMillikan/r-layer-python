# r-layer-python
draw an r/layer submission based on an image file

# how to use
pretty much everything is arbitrary to fit my system, so good luck.
Important thigns to look at:
- min_val in "getImginImg()"
- all variables in snake case
- line 189 (topBarImg = readImg("./reference/topBar.png"))
- topBar.png must be re-screenshotted
- HUE_SIMILARITY and LIT_SIMILARITY are basically how complex the colors in the image will be. lower values = more color complexity = more time to draw
- grid_size is the number of points to draw per axis, so grid_size=10 means 100 pixels total. higher numbers take a lot of RAM, when grid_size = 70, chrome used approx. 6 GB of memory
- setBrushSize(x) on line 251 is the size of each dot, 0 <= x <= 1
