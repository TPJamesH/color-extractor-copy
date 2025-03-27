import webcolors

def closest_color(requested_color):
    min_colors = {}
    for name in webcolors.names("css3"):
        r,g,b = webcolors.name_to_rgb(name)
        rd = (r - requested_color[0]) ** 2
        gd = (g - requested_color[1]) ** 2
        bd = (b - requested_color[2]) ** 2
        min_colors[(rd+gd+bd)] = name
    return min_colors[min(min_colors.keys())]

def get_color_name(rgb_tuple):
    try:
        hex = webcolors.rgb_to_hex(rgb_tuple)
        return webcolors.hex_to_name(hex)
    except ValueError:
        return closest_color(rgb_tuple)
    
def denormalize(rgb_tuple):
    return tuple(int(value * 255) for value in rgb_tuple)