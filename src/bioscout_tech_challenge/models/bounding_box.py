from dataclasses import dataclass


@dataclass
class BoundingBox:
    """
    Class to represent a bounding box which is stored as x & y being the top left co-ordinates with width & height
    dictating how far to the 'right' and 'down' the bounding box should be drawn.
    """

    x: float  # Far Left value
    y: float  # Top of box Value
    width: float  # How wide the box is
    height: float  # How tall the box is top to bottom.
