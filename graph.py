from operator import indexOf
import os
import random

from PIL import Image, ImageDraw, ImageFont

import costlib
import graphutils

# Get the current working directory
filepath = os.path.abspath(os.path.dirname(__file__))

# Cos for some reason unknown to god, random has the same seed every time. So just use a true random string as the seed
random.seed(os.urandom(32))

cost = 50


def fontloader(size=30):
    """fontloader Returns a font based on the given size.

    Parameters
    ----------
    size : int, optional
        The size of the font, by default 30

    Returns
    -------
    PIL Font
        A PIL font with the given font size
    """
    return ImageFont.truetype(f"{filepath}/static/font.ttf", size=size)


def hsv_to_rgb(h: float, s: float, v: float) -> tuple:
    """I have no clue how this works, blame stackoverflow\n
    It converts a HSV color mapping to an RGB. We have this so we can loop through the hue value and get a color PIL can use"""
    if s == 0.0:
        v *= 255
        return (v, v, v)
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p, q, t = (
        int(255 * (v * (1.0 - s))),
        int(255 * (v * (1.0 - s * f))),
        int(255 * (v * (1.0 - s * (1.0 - f)))),
    )
    v *= 255
    i %= 6
    if i == 0:
        return (v, t, p)
    elif i == 1:
        return (q, v, p)
    elif i == 2:
        return (p, v, t)
    elif i == 3:
        return (p, q, v)
    elif i == 4:
        return (t, p, v)
    elif i == 5:
        return (v, p, q)


def color(inp: int) -> tuple:
    """Using the current loop number, generates a HSL value then converts it into RGB to create a rainbow effect

    Parameters
    ----------
    inp : int
        The loop number

    Returns
    -------
    tuple
        RGB value
    """
    if inp > 360:
        inp = inp - 360
    r, g, b = hsv_to_rgb(inp / 360, 0.7, 1)
    return round(r), round(g), round(b), 255


def create(_data: list) -> Image:
    """Creates a PIL image as a replacement for matplotlib which does not work on linux python 3.10

    Parameters
    ----------
    _data : list
        A list of 2 element tuples with the first element being the x value (number of loops)
        and the second element being the y value (price)
        \n\tMay look like this:\n\t
        [(0, 55.2), (1, 56.3), (2, 55.9)]

    Returns
    -------
    Image
        A PIL image of the graph
    """
    if len(_data) == 1:
        # If there is only one value, just return that value as an image
        _img = Image.new("RGB", (100, 100), (46, 49, 54))
        # Se up the drawing thingy
        draw = ImageDraw.Draw(_img, "RGBA")
        # Write the current price
        draw.text(
            (5, 35),
            "$" + str(round(_data[0][1], 2)),
            font=fontloader(25),
            fill=(255, 255, 255),
        )
    else:
        # Separate the data into the x and y values
        times = []
        points = []
        for x in _data:
            times.append(x[0])
            points.append(x[1])
        print(points[-1])
        Y_max = 50
        # Set up the image
        _img = Image.new("RGB", (1000, 300), (46, 49, 54))
        # Work out how far to space each point on the x axis
        # Changed from 900 to 950, subtract 1 from len(points) as first index is 0
        x_spacing = 950 / (len(points) - 1)
        # Get the range of values
        y_range = max(points) - min(points)
        # Work out the y spacing
        y_spacing = (250 - Y_max) / y_range  # Changed from 200 to 250
        # Set up the drawing tool
        draw = ImageDraw.Draw(_img, "RGBA")

        # Find the average of the points
        avg = sum(points) / len(points)

        # Solution to going off screen
        # The drawing of the points assumes the min value is 0,
        # so to make that true i am subtracting the min value from every point
        y_min = min(points)
        # This is here so the true max value is kept when drawing in the scale, same for min
        point_max = max(points)
        for i in range(len(points)):
            points[i] -= y_min

        # Draw the Y axis on both sides
        draw.line(((24, Y_max), (24, 275)))
        draw.line(((975, Y_max), (975, 275)))
        # Plot a marker on both sides of the y axis at intervals determined by the y_spacing
        # Each marker on the y axis is $5
        for x in range(Y_max, 275, round(y_spacing * 5)):
            draw.point((25, x), fill=(255, 255, 255))
            draw.point((23, x), fill=(255, 255, 255))
            draw.point((976, x), fill=(255, 255, 255))
            draw.point((974, x), fill=(255, 255, 255))
            draw.line(((24, x), (975, x)), fill=(255, 255, 255, 25))

        # Draw the x axis
        draw.line(((25, 275), (975, 275)))
        # Plot a marker on the x axis at intervals determined by the x_spacing
        # (each marker on the x axis is 5 loops)
        for x in range(25, 975, round(x_spacing * 5)):
            draw.point((x, 274), fill=(255, 255, 255))
            draw.point((x, 276), fill=(255, 255, 255))
            draw.line(((x, Y_max), (x, 275)), fill=(255, 255, 255, 25))

        # Set the default "last" point to the bottom left corner

        # Loop through the points
        for i, x in enumerate(points):
            if indexOf(enumerate(points), (i, x)) == 0:
                last = (25, 275 - (x * y_spacing))
                # Draw a line from the last point drawn to the current point
                # with the color determined by the color function

                # Using some random thing I found on stackoverflow to make the lines smoother with anti aliasing
            graphutils.draw_line_antialiased(
                draw,
                _img,
                i * x_spacing + 25,
                275 - (x * y_spacing),
                last[0],
                last[1],
                color(times[i]),
            )
            # Save the dot's position as the last point
            last = (i * x_spacing + 25, 275 - (x * y_spacing))
        draw.line(
            ((25, 275 - (avg * y_spacing)), (975, 275 - (avg * y_spacing))),
            fill=(255, 255, 255, 100),
        )

        # Write the max and min values on the left hand side
        draw.text(
            (0, 280),
            "$" + str(round(y_min, 1)),
            font=fontloader(10),
            fill=(255, 255, 255),
        )
        draw.text(
            (0, Y_max - 15),
            "$" + str(round(point_max, 1)),
            font=fontloader(10),
            fill=(255, 255, 255),
        )
        text = f"""Min: ${round(y_min,2)}    Max: ${round(point_max, 2)}    Average: ${round(avg,2)}    Current price: ${_data[-1][1]}    Current loop: {times[-1]+1}"""

        draw.text((50, 10), text, font=fontloader(
            16), fill=(255, 255, 255))
        # Resize it with some anti-aliasing to help clean it up
        _img = _img.resize((1000, 300), resample=Image.ANTIALIAS)
    # Return the image
    return _img


if __name__ == "__main__":
    # If we run the file directly, create a random graph
    data = []
    for a in range(1000):
        cost = costlib.gencost(cost)
        data.append((a, cost))
    # Note: Around 1500 points the x spacing drops to 0 when rounded so won't work
    img = create(data[-288:])
    img.show()
