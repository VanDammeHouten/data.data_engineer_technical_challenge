"""
Bounding box model.
"""

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
    name: str = None  # Name of the image the box is from (optional)
    @staticmethod
    def from_absolute_coordinates(x_min, y_min, x_max, y_max, image_width, image_height,name=None):
        """
        Create a BoundingBox from absolute pixel coordinates.
        """
        return BoundingBox(
            x=x_min / image_width,
            y=y_min / image_height,
            width=(x_max - x_min) / image_width,
            height=(y_max - y_min) / image_height,
            name=name
        )

    @staticmethod
    def from_centroid(x, y, width, height,name=None):
        """
        Create a BoundingBox from centroid coordinates.
        """
        return BoundingBox(x=x-width/2, y=y-height/2, width=width, height=height,name=name)

    def calculate_iou(self, other: "BoundingBox") -> float:
        """
        Calculate the Intersection over Union (IoU) between this bounding box and another.
        IoU measures the overlap between two bounding boxes as a ratio of the intersection area
        to the union area.

        Args:
            other: Another BoundingBox instance to compare with

        Returns:
            float: IoU score between 0 and 1, where:
                  0 = no overlap
                  1 = perfect overlap
        """
        # Calculate coordinates of intersection rectangle
        x_left = max(self.x, other.x)
        y_top = max(self.y, other.y)
        x_right = min(self.x + self.width, other.x + other.width)
        y_bottom = min(self.y + self.height, other.y + other.height)

        # If there is no overlap, return 0
        if x_right < x_left or y_bottom < y_top:
            return 0.0

        # Calculate intersection area
        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        # Calculate union area
        box1_area = self.width * self.height
        box2_area = other.width * other.height
        union_area = box1_area + box2_area - intersection_area

        return intersection_area / union_area

    def to_absolute_coordinates(self, image_width, image_height):
        """
        Convert the bounding box to absolute pixel coordinates.
        """
        return (
            int(self.x * image_width),
            int(self.y * image_height),
            int((self.x + self.width) * image_width),
            int((self.y + self.height) * image_height)
        )

    def to_absolute_centroid(self, image_width, image_height):
        """
        Convert the bounding box to absolute pixel coordinates.
        """
        return (
            int((self.x + self.width/2 )* image_width),
            int((self.y + self.height/2 )* image_height)
        )
