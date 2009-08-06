from gamera.core import RGBPixel  
def outline(rgb_img,cc,width=2.0,color=RGBPixel(255,0,0)):
    rgb_img.draw_hollow_rect((cc.offset_x,cc.offset_y),(cc.offset_x+cc.ncols,cc.offset_y+cc.nrows),color,width)
       
def outline_matched(rgb_img,needle,haystack):
    epsilon = 5
    bottom_ncols = needle.ncols-5
    top_ncols = needle.ncols+5
    for c in haystack:
        if c.ncols == needle.ncols and c.nrows == needle.nrows:
            outline(rgb_img,c)
