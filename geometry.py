"""Geomtric objects and functions. Use the Point class for mainly, and other
functions are provided. If shapely is installed, it can be used for faster
C calculations.

TODO: Add more features to Points (COMPLETED)
      Speed up collision checks (COMPLETED with shapely module)
"""

from cmath import cos, sin
from math import atan2, degrees, hypot, pow, radians, sqrt
from operator import neg, pos
from random import random, randrange, uniform
from re import compile
from struct import unpack
from sys import modules
from typing import List, Tuple, cast

from arcade import Sprite, SpriteList, get_window, unschedule

from .color import BLACK

points = 0 # Number of points to create unique keysets
pi = 3.14159265358979

pointlist = []

PX = "px"
CM = "cm"
PT = "pt"
PC = "pc"
IN = "in"
MM = "mm"
CM = "cm"

__all__ = [
           "Point",
           "square",
           "cube",
           "parse_distance",
           "chance",
           "are_polygons_intersecting",
           "is_point_in_polygon",
           "check_collision",
           "get_distance",
           "get_closest",
           "rotate_point",
           "get_angle_degrees",
           "get_angle_radians",
           "degrees_to_radians",
           "convert_xywh_to_points",
           "points",
           "pi",
           "_check_collision"
          ]


class Point:
    """A named 2D Point. This is used in almost every x and y coordinate in
    Armies. Note that this does not have to be used for points, it can be used
    as vectors for gravity, velocity, and more. This was inspired by
    pymunk.vec2d.Vec2d.

    >>> point = Point(100, 100)
    >>> point.x, point.y
    100, 100
    >>> point["name"]
    1

    A Point supports operations, so you can perform many computations with
    Points. Take a look at the below example.

    >>> a = Point(5, 3)
    >>> b = Point(5, 3)
    >>> a + b
    10, 6

    It supports:
        - Addition
        - Subtraction
        - Multiplication
        - Division
        - Floor division

    Additionally, many features are implemented for extra functionality and
    ease of access.
    """

    def __init__(self, x, y, name=None):
        """Initialize a named object-oriented Point. Points support opertaions
        and are rich with features. When creating a Point, you can access its
        properties by its name and from a list. This way, you don't have to
        save Points as variables. Take a look at this.

        >>> Point(5, 3, name="My first Point")
        >>> for point in pointlist:
                if point.name == "My first Point":
                    print("Found Point!")

        Points are automatically saved as variables in a list called pointlist.

        x - x coordinate of Point
        y - y coordinate of Point
        name - unique name of Point (identifier). This is automatically
               generated with the number of Points created if not specified
               by this parameter.

        parameters: int, int, str

        properties:
            x - x coordinate of Point
            y - y coordinate of Point
            vx - horizontal velocity of Point
            vy - vertical velocity of Point
            name - unique keyname of Point
            data - map of properties
            length - length of the Point
            angle - angle of the Point

        methods:
            _get_length - get the current length of the Point (property)
            _get_angle - get the current angle of the Point (property)

            __call__ - return a tuple of the Point
            __getitem__ - return a value from key item of data
            __iter__ - return a list of the x and y coordinates
            __del__ - delete point and remove it from scheduling
            __add__ - add a Point or tuple to x and y coordinates
            __sub__ - subtract a Point or tuple to x and y coordinates
            __mul__ - multiply a number with x and y coordinates
            __truediv__ - divide a number with x and y coordinates
            __floordiv__ - floor divide a number with x and y coordinates

            get_distance - distance between another Point
            is_in_polygon - check if exists inside a polygon
            get_closest - closest Point given a list
            get_length - length of the Point
            get_squared_length - squared length of the Point
            get_nearest_point - nearest Point
            scale_to_length - scale the Point to a given length
            rotate - rotate the Point a certain radians
            normalize - normalized copy of the Point
            perpendicular - perpendicular Point (negative reciprocal)
            perpendicular_normal - perpendicular normalized Point
            dot - dot product of Point
            projection - project over another Point
            cross - cross product between another Point
            interpolate_to - interpolate between another Point
            to_basis - convert to basis (Linear Algebra)
            inverse - inverse of Point (flipped x and y coordinates)
            tuplize - return a tuplized version of the Point (x, y)
        """

        self.x = x
        self.y = y

        self.vx = 0
        self.vy = 0

        if not name:
            # Generate a unique keyset name for this point
            global points
            points += 1

            self.name = str(points)
        else:
            self.name = name

        global pointlist

        pointlist.append(self)

        self.data = {
            "x" : self.x,
            "y" : self.y,
            "name" : self.name
        }

    def _get_x(self):
        """Get the x position of the Point.

        returns: int
        """

    def _set_x(self, x):
        """Set the x position of the Point.

        x - x position of the Point

        parameters: int
        """

    def _get_y(self):
        """Get the y position of the Point.

        returns: int
        """

    def _set_y(self, y):
        """Set the y position of the Point.

        y - y position of the Point

        parameters: int
        """

    def _get_position(self):
        """Get the position of the Point as a tuple (self.x, self.y).

        returns: tuple (self.x, self.y)
        """

        return self.position

    def _set_position(self, position):
        """Set the position of the Point as a tuple (self.x, self.y).

        position - new position of Point

        parameters: int
        """

        self.x = position[0]
        self.y = position[1]

    def _get_length(self):
        """Property function of getting the length of the Point. This may not
        be set.

        returns: float
        """

        # Use math.pow for faster C functions
        return sqrt(pow(self.x, 2) + pow(self.y, 2))

    def _get_angle(self):
        """Get the current angle of the Point in radians.

        returns: float
        """

        if not self.get_squared_length():
            return 0

        return atan2(self.y, self.x)

    # x = property(_get_x, _set_x)
    # y = property(_get_y, _set_y)
    position = property(_get_position, _set_position)
    length = property(_get_length)
    angle = property(_get_angle)

    def __call__(self, *args, **kwds):
        """Return a tuplized version of the Point.

        >>> a = Point(5, 3)
        >>> a()
        5, 3

        returns: tuple (x and y coordinates)
        """

        return self.position

    def __getitem__(self, item):
        """Return a value from key item of data.

        >>> Point(5, 3)["x"]
        5

        item - key to find value

        parameters: str
        returns: str
        """

        self.data["x"] = self.x
        self.data["y"] = self.y
        self.data["name"] = self.name

        return self.data.get(item, False)

    def __iter__(self):
        """Return a list of the x and y coordinates.

        >>> iter(Point(5, 3))
        5, 3

        returns: list (x, y)
        """

        return [self.x, self.y]

    def __del__(self):
        """Delete Point and remove it from event scheduling.

        >>> a = Point(5, 3)
        >>> del a
        """

        try: unschedule(self.update)
        except AttributeError: pass # No scheduling... pretty mysterious

    ### MATHEMATICAL FUNCTIONS ###

    def __add__(self, point):
        """Add a Point or tuple to x and y coordinates.

        >>> Point(5, 3) + (6, 9)
        11, 12

        point - point to add coordinates

        parameters: Point or tuple
        returns: tuple
        """

        if isinstance(point, Tuple):
            self.x += point[0]
            self.y += point[1]

            return

        self.x += point.x
        self.y += point.y

        return self.position

    def __sub__(self, point):
        """Subtract a Point or tuple from x and y coordinates.

        >>> Point(5, 3) - Point(2, 1)
        3, 2

        point - point to subtract coordinates

        parameters: Point or tuple
        returns: tuple
        """

        if isinstance(point, Tuple):
            self.x -= point[0]
            self.y -= point[1]

            return

        self.x -= point.x
        self.y -= point.y

        return self.position

    def __mul__(self, value):
        """Multiply a float by x and y coordinates.

        >>> Point(5, 3) * 2.5
        12.5, 7

        value - value to multiply coordinates

        parameters: float
        returns: tuple
        """

        self.x *= value
        self.y *= value

        return self.position

    def __truediv__(self, value):
        """Divide x and y coordinates by value.

        >>> Point(5, 3) / 2
        2.5, 1.5

        value - value to divide coordinates

        parameters: float
        returns: tuple
        """

        self.x /= value
        self.y /= value

        return self.position

    def __floordiv__(self, value):
        """Floor divide x and y coordinates by value (integer division).

        >>> Point(5, 3) // 2
        2, 1

        value - value to floor divide coordinates
        returns: tuple
        """

        self.x //= value
        self.y //= value

        return self.position

    def __radd__(self, point):
        """Add a Point or tuple to x and y coordinates. This is a reversed
        addition.

        >>> (5, 3) + Point(5, 3)
        10, 6

        point - point to add coordinates

        parameters: Point or tuple
        returns: tuple
        """

        return self.__add__(point)

    def __rsub__(self, point):
        """Subtract a Point or tuple from x and y coordinates. This is a
        reversed subtraction.

        >>> (10, 3) - Point(5, 3)
        5, 0

        point - point to add coordinates

        parameters: Point or tuple
        returns: tuple
        """

        self.x = point.x - self.x
        self.y = point.y - self.y

        return self.position

    def __rmul__(self, value):
        """Multiply a float by x and y coordinates. This is a reversed
        multiplication.

        >>> 2 * Point(5, 3)
        10, 6

        value - value to multiply coordinates

        parameters: float
        returns: tuple
        """

        return self.__mul__(value)

    def __pos__(self):
        """Return the unary position (converting to positive).

        >>> + Point(-5, 3)
        5, 3

        returns: tuple
        """

        self.x = pos(self.x)
        self.y = pos(self.y)

        return self.position

    def __neg__(self):
        """Return the negatated position (converting to negative).

        >>> - Point(-5, 3)
        5, -3

        returns: tuple
        """

        self.x = neg(self.x)
        self.y = neg(self.y)

        return self.position

    def get_distance(self, point):
        """Get the distance between another Point. See get_distance for more
        information. You can use a name of a Point for this.

        point - Point to get distance

        parameters: Point or str or int
        returns: int - (distance between two points)
        """

        if isinstance(point, Point):
            return get_distance(self, point)
        else:
            return get_distance(self, pointlist[point])

    def is_in_polygon(self, polygon):
        """Check if the x and y coordinates exist in a polygon.

        polygon - polygon to check if x and y coordinates exist in

        parameters: int, int
        returns: bool (True or False if Point exists in polygon)
        """

        return is_point_in_polygon(self, polygon)

    def get_closest(self, list):
        """Get the closest Point from a list. See get_closest for more
        information.

        list - list to get closest object

        parameters: List (list of Points)
        returns: tuple ((closest, distance))
        """

        return get_closest(self, list)

    def get_squared_length(self):
        """Return the squared length of the vector.

        returns: int
        """

        return pow(self.x, 2) + pow(self.y, 2)

    def get_length(self):
        """Return the length of the vector.

        returns: int
        """

        return sqrt(pow(self.x, 2) + pow(self.y, 2))

    def get_nearest_point(self, list=None):
        """Return the nearest point and its distance. If a Point list is
        provided it will use it.

        list - list to get closest Point

        parameters: list or tuple
        returns: Point
        """

        global points

        pointlist = list or points

        return get_closest(self, pointlist)

    def get_angle_between(self, point):
        """Get the angle betewen this and another Point in radians.

        point - point to get angle between

        parameters: Point
        returns: float (in radians)
        """

        cross = self.x * point.y - self.y * point.x
        dot = self.x * point.x + self.y * point.y

        return atan2(cross, dot)

    def scale_to_length(self, length):
        """Scale the Point to the given length.

        length - scale length of the Point

        parameters: float
        returns: tuple
        """

        old = self.length

        self.x = self.x * length / old
        self.y = self.y * length / old

        return self.position

    def rotate(self, angle):
        """Rotate the Point a certain radians.

        angle - radians the Point should be rotated

        parameters: float
        """

        cosine = cos(angle)
        sine = sin(angle)

        self.x = self.x * cosine - self.y * sine
        self.y = self.x * sine + self.y * cosine

        return self.position

    def normalized(self):
        """Get a normalized copy of the Point

        NOTE: will return 0 if the length of the vector is 0

        return: tuple (self.x, self.y)
        """

        length = self.length

        if length != 0:
            return self / length
        return self.position

    def perpendicular(self):
        """Create a perpendicular Point. This is done by a negative
        reciprocal.

        returns: tuple (self.x, self.y)
        """

        self.x = -self.y
        self.y = self.x

        return self.position

    def perpendicular_normal(self):
        """Create a perpendicular normalized Point. This is done by dividing
        the negative reciprocal of the x and y coordinates by the length.

        returns: tuple (self.x, self.y)
        """

        length = self.length
        if length != 0:
            # Negative reciprocal

            self.x = -self.y / length
            self.y = self.x / length

        return self.position

    def dot(self, point):
        """The dot product between the Point and another.

        v1.dot(v2) → v1.× v2.x + v1.y × v2.y

        point - other Point to get the dot product

        parameters: Point
        returns: float
        """

        return float(self.x * point.x + self.y * point.y)

    def projection(self, point):
        """Project the Point over another Point (vector projection). This can
        also be called vector component or vector resolution.

        point - Point for the Point to be projected over

        parameters: Point
        returns: tuple (self.x, self.y)
        """

        length_squared = point.x * point.x + point.y * point.y

        if not length_squared:
            self.position = (0, 0)

        projected_length = self.dot(point)
        new = projected_length / length_squared

        self.x = point.x * new
        self.y = point.y * new

        return self.position

    def cross(self, point):
        """The cross product between the vector and other vector
            v1.cross(v2) → v1.x × v2.y — v1.y × v2.x

        Where is v1 is one vector and v2 another.

        point - other Point to get cross product

        parameters: Point
        returns: tuple (self.x, self.y)
        """

        return self.x * point.y - self.y * point.x

    def interpolate_to(self, point, range):
        """Interpolate another Point into the Point given a range. This is
        defined by:

        y = y₁ + (x — x₁) [(y₂ — y₁) ÷ (x₂ — x₁)]

        where...
        y	     linear interpolation value
        x	     independent variable
        x₁, y₁   values of the function at one point
        x₂, y₂   values of the function at another point

        See https://www.cuemath.com/interpolation-formula/ for details.

        point - Point to be interpolated into the Point
        range - range of the interpolation

        parameters: Point, float
        returns: tuple (self.x, self.y)
        """

        self.x = self.x + (point.x - self.x) * range
        self.y = self.y + (point.y - self.y) * range

        return self.position

    def to_basis(self, vector):
        """"Convert the Point to a basis given a vector. Learned in Linear
        Algebra.

        vector - vector of conversion. This is NOT a Point.

        parameters: multi-demensional list [(x, y), (x, y)]
        returns: tuple (self.x, self.y)
        """

        self.x = self.dot(vector[0]) / Point(*vector[0]).get_squared_length()
        self.y = self.dot(vector[1]) / Point(*vector[1]).get_squared_length()

        return self.position

    def inverse(self):
        """Find the inverse of the Point. This can be notated as

        f⁻¹(x) = ...

        X and y coordinates of the point are just flipped.
        """

        # This is necessary because the properties will change and trip each
        # other up

        x = self.x
        y = self.y

        self.y = x
        self.x = y
    def svg(self, factor=1, color=None, alpha=None):
        """Get an SVG (scalable vector graphic) image as a string for the
        Point.

        factor - scale factor for the SVG circle diameter. Defaults to 1.
        color - RGB color of the SVG circle as a tuple of three ints. Defaults
                to None
        alpha - scale of 0 to 255 for alpha channel of SVG circle. An alpha of
                255 is completely solid, and an alpha of 0 completely opaque.
                Defaults to 255.
        """

        if self.is_empty:
            return "<g />"

        color = color or BLACK

        if alpha is None:
            alpha = 0.6

        # return (
        #         f"<circle cx="{self.x}" cy="{self.y}" r="{3 * factor}" "
        #         f"stroke=\"#555555\" stroke-width=\"2\" fill=\"{color}\" opacity=\"{alpha}\">"
        # )

    def tuplize(self):
        """Return a tuplized Point of the x and y coordinates in (x, y).

        returns: tuple (x, y)
        """

        return self.position

    def update(self, delta):
        """Update the Point. This is called every tick of the update cycle.

        delta - time since the update function was last called

        parameters: float
        """

        self.x += self.vx
        self.y += self.vy


class Pointlist:

    def __init__(self, *points):
        """Create a pointlist. The purpose of a pointlist is so that multiple
        points can be updated and kept up-to-date without using much memory. It
        is useful in polygons.

        Using a pointlist would look like this:

        >>> a = Point(5, 3)
        >>> b = Point(5, 3)
        >>> c = Pointlist(a, b)

        A pointlist also has many internal features.
        >>> len(Pointlist(a, b, c, d, e))
        5

        points *- following variables of each Point

        parameters: *Point
        """

        self.list = points

    def __len__(self):
        """Get the length of the pointlist.

        returns: int
        """

        return len(self.list)

    def __getitem__(self, index):
        """Get a Point from the pointlist.

        index - index of Point

        parameters: int
        returns: Point
        """

        return self.list[index]

    def __setitem__(self, index, point):
        """Set am item's value from the pointlist.

        index - index of Point
        point - new Point to be added

        parameters: int, Point
        """

        self.list[index] = point


def square(value):
    """Calculate the squared value of a number. This forms a quadratic function,
    which is x².

    value - value to take to the power of two

    parameters: int
    returns: int
    """

    return pow(value, 2)

def cube(value):
    """Calculate the cubed value of a number. This forms a cubic function, which
    is x³.

    value - value to take to the power of three

    parameters: int
    returns: int
    """

    return pow(value, 3)

def parse_distance(distance, dpi=96):
    """Parse a distance string and return corresponding distance in pixels as
    an integer.

    TODO: make nested function formatting neater

    distance - distance unit supported
    dpi - resolution of display. Defaults to 96 and should usually be left as
          is.

    parameters: str, int
    returns: int
    """

    class DistanceDecodingError(Exception):
        """Distance decoding error.
        """

    def raise_distance_decoding_error(format, message=None):
        """Raise a distance decoding error. This is used internally by various
        distance geometric functions.

        format - unknown format or variable
        message - custom message

        parameters: str, str
        """

        message = message or \
                f"Unknown distance unit \"{format}\". Valid options are " \
                "\"px\", \"pt\", "  "\"pc\", \"in\", \"mm\", and \"cm\"."

        raise DistanceDecodingError(message)

    if isinstance(distance, int):
        return distance
    elif isinstance(distance, float):
        return int(distance)

    match = compile(r'([-0-9.]+)([a-zA-Z]+)').match(distance)

    if not match:
        raise_distance_decoding_error(distance)

    if not match:
        return 0

    value, unit = match.groups()
    value = float(value)

    if unit == PX: return int(value)
    elif unit == PT: return int(value * dpi / 72)
    elif unit == PC: return int(value * dpi / 6)
    elif unit == IN: return int(value * dpi)
    elif unit == MM: return int(value * dpi * 0.0393700787)
    elif unit == CM: return int(value * dpi * 0.393700787)

    else: raise_distance_decoding_error(distance)

def chance(value):
    """Return True or False in a 1-in-value chance.

    value - chance of returning True

    parameters: int
    returns: bool
    """

    if randrange(1, value + 1) == 2:
        return True
    else:
        return False

def are_polygons_intersecting(a, b, shapely=True):
    """Check if two polygons are intersecting. A polygon should be a tuple and
    a series of Points. Using a Pointlist may or may not work currently.

    a - first polygon bounding box of intersection check
    b - second polygon bounding box of intersection check
    shapely - use shapely for calculating geometry. If this is enabled and
              shapely is not installed, the regular functions will be used.
              Defaults to True.

    parameters: int, int
    returns: bool (True or False if polygons intersecting)
    """

    if shapely:
        if "shapely" in modules():
            from shapely import Polygon as Polygon_
            from shapely.speedups import enable, enabled

            if not enabled:
                enable()

            a = Polygon_(a)
            b = Polygon_(b)

            r2 = False
            r1 = a.intersects(b)

            if r1:
                r2 = a.touches(b)

            return r1 and not r2

    for polygon in (a, b):
        for i1 in range(len(polygon)):
            i2 = (i1 + 1) % len(polygon)

            projection_1 = polygon[i1]
            projection_2 = polygon[i2]

            normal = (projection_2[1] - projection_1[1],
                      projection_1[0] - projection_2[0])

            min_a, max_a, min_b, max_b = (None,) * 4

            for _polygon in a:
                projected = normal[0] * _polygon[0] + normal[1] * _polygon[1]

                if min_a is None or projected < min_a:
                    min_a = projected
                if max_a is None or projected > max_a:
                    max_a = projected

            for _polygon in b:
                projected = normal[0] * _polygon[0] + normal[1] * _polygon[1]

                if min_b is None or projected < min_b:
                    min_b = projected
                if max_b is None or projected > max_b:
                    max_b = projected

            if cast(float, max_a) <= cast(float, min_b) \
                or cast(float, max_b) <= cast(float, min_a):
                return False

    return True

def are_rects_intersecting(a, b):
    """Check if two Rects are intersecting. This is used only with the Rect
    defined in the widgets module, unless it has border properties, such as
    left, right, top, and bottom.

    a - first Rect to check for intersection
    b - second Rect to check for intersection

    parameters: Rect, Rect
    returns: bool
    """

    a_topright = (a.top, a.right)
    a_bottomleft = (a.bottom, a.left)
    b_bottomleft = (b.bottom, b.left)
    b_topright = (b.top, b.right)

    return not (a_topright.x < b_bottomleft.x or \
                a_bottomleft.x > b_topright.x or \
                a_topright.y < b_bottomleft.y or \
                a_bottomleft.y > b_topright.y
               )

def is_point_in_polygon(point, polygon, shapely=True):
    """Check if the given Point exists in a polygon (meaning that it is inside
    it). This use the shapely module if specified in the parameters. Depending
    on the system, shapely may make this slower or faster.

    If this is lagging, you may have a poor graphics card or GPU processor.
    Speedups for shapely are automatically enabled. This is basically telling
    shapely to use the faster Cython speedups.

    point - Point to check if in polygon
    polygon - polygon to check if Point coordinates exist in
    shapely - use shapely for calculating geometry. If this is enabled and
              shapely is not installed, the regular functions will be used.
              Defaults to True.

    parameters: int, int, bool
    returns: bool (True or False if Point exists in polygon)
    """

    length = len(polygon)
    inside = False
    p1x, p1y = polygon[0]

    if not length:
        return False

    if shapely:
        if "shapely" in modules():
            from shapely import Point as Point_
            from shapely import Polygon as Polygon_
            from shapely.speedups import enable, enabled

            if not enabled:
                enable()

            point = Point_(point.position)
            polygon = Polygon_(polygon)

            return polygon.contains(point)

    for i in range(length + 1):
        p2x, p2y = points[i % length]

        if point.y > min(p1y, p2y):
            if point.y <= max(p1y, p2y):
                if point.x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (point.y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x

                    # noinspection PyUnboundLocalVariable
                    if p1x == p2x or point.x <= xints:
                        inside = not inside

        p1x, p1y = p2x, p2y

    return inside

def _check_collision(a, b):
    """Internal function for checking collision of two objects. Used by
    check_collision.

    a - first object to check collision
    b - second object to check collision

    NOTE: you should never need to call this directly.
    NOTE: you must use an Object or a PhysicsObject. If you want to check
          collisions with other objects, use are_polygons_interecting with
          each object's hitbox. Note there are exceptions to these conditions.

          Using this with GUI widgets is not supported.

    parameters:
        a - Object or PhysicsObject
        b - Object or PhysicsObject
    returns: list (list of collisions)
    """

    collision_radius = a.collision_radius + b.collision_radius

    diff_x = a.position[0] - b.position[0]
    diff_x2 = square(diff_x)

    if diff_x2 > collision_radius * collision_radius:
        return False

    diff_y = a.position[1] - b.position[1]
    diff_y2 = square(diff_y)

    if diff_y2 > square(collision_radius):
        return False

    distance = diff_x2 + diff_y2
    if distance > square(collision_radius):
        return False

    try:
        intersection = are_polygons_intersecting(a.get_adjusted_hit_box(),
                                                 b.get_adjusted_hit_box())
    except ValueError:
        intersection = []

    return intersection

def get_nearby_sprites(object, list):
    """Internal function used by GPU collision check.

    object - object to get nearby objects
    list - list of nearby objects

    parameters: Object, PhysicsObject
    returns: list (list of objects selected by the transformation)
    """

    count = len(list)

    if not count:
        return []

    # Update the position and size to check
    ctx = get_window().ctx
    list._write_sprite_buffers_to_gpu()

    ctx.collision_detection_program["check_pos"] = object.x, object.y
    ctx.collision_detection_program["check_size"] = object.width, object.height

    # Ensure the result buffer can fit all the sprites (worst case)
    buffer = ctx.collision_buffer
    if buffer.size < count * 4:
        buffer.orphan(size=count * 4)

    # Run the transform shader emitting sprites close to the configured position and size.
    # This runs in a query so we can measure the number of sprites emitted.
    with ctx.collision_query:
        list._geometry.transform(  # type: ignore
            ctx.collision_detection_program,
            buffer,
            vertices=count,
        )

    # Store the number of sprites emitted
    emit_count = ctx.collision_query.primitives_generated

    # If no sprites emitted we can just return an empty list
    if not emit_count:
        return []

    # .. otherwise build and return a list of the sprites selected by the transform
    return [
        list[i]
        for i in unpack(f'{emit_count}i', buffer.read(size=emit_count * 4))
    ]

def check_collision(a, b, type=None, method=0):
    """Check for collisions between two things. Multiple datatypes are
    supported. You may use a Object or PhysicsObject, a SpriteList, or a List as
    parameters and it will calculate the collisions for you. Optionally, you can
    specify the collision type with the third type parameter. This can be used
    for optimization.

    Spatial hash is a new method developed by Python arcade for detecting
    collisions. This will speed up collisions with motionless objects, but will
    result with buggy moving with active, moving objects.

    Arcade divides the screen up into a grid. We can track which grid location
    each object overlaps, and put them in a hash map. For each grid location, we
    can quickly pull the object in that grid in a fast O* operation. When
    looking for object that collide with our target object, we only look at
    objects in sharing its grid location. This can reduce checks from 50,000 to
    just 3 or 4. If the object moves, we have to recalculate and re-hash its
    location, which reduces speed.

    The method parameter specifies the type of checking collisions:
        0: automatic select:
            - Spatial hashing if avaliable
            - GPU if 1,500+ objects
            - Simple
        1: Spatial hashing if avaliable
        2: GPU based (recommended with 1,500+ objects)
        3: Simple-check

    a - first item to check collision with
    b - second item to check collision with
    type - optional type of collsions

    parameters:
        a - Object or PhysicsObject,
        b - PhysicsObject or SpriteList or List
    returns: list (list of collisions)
    """

    single = False
    double = False
    triple = False

    if type:
        if type == Sprite: single = True
        elif type == SpriteList: double = True
        elif type == List: triple = True

    else:
        if isinstance(b, Sprite): single = True
        elif isinstance(b, SpriteList): double = True
        elif isinstance(b, List): triple = True

    if single:
        return _check_collision(a, b)

    elif double:
        if b.spatial_hash and (method == 1 or method == 0):
        # Spatial
            b_ = b.spatial_hash.get_objects_for_box(a)
        elif method == 3 or (method == 0 and len(b) <= 1500):
            b_ = b  # type: ignore
        else:
            # GPU transform
            b_ = get_nearby_sprites(a, b)  # type: ignore

        return [
            sprite
            for sprite in b_
            if a is not b and _check_collision(a, sprite)
        ]

    elif triple:
        list = []

        for b in b:
            for object in b:
                if a is not object and _check_collision(a, object):
                    list.append(object)

        return list

def get_distance(a, b):
    """Get the distance between two objects. Note that other data types may be
    used, as long as they have x and y properties.

    a - first object to get distance
    b - second object to get distance

    parameters: Point, Point
    returns: int
    """

    return hypot(a.x - b.x, a.y - b.y)

def get_distance_(a, b):
    """Get the distance between two objects. Note that other data types may be
    used, as long as they have x and y properties. This uses a different
    method:

    d = √(x₁ — x₂)²＋(y₁ — y₂)²

    NOTE: this method is less efficient than get_distance, as it uses more
          steps. But, they both yield the same result.

    >>> a = Point(5, 5)
    >>> b = Point(5, 3)
    >>> get_distance(a, b) is get_distance_(a, b)
    True

    a - first object to get distance
    b - second object to get distance

    parameters: Point, Point
    returns: int
    """

    # Use math.pow for faster C functions

    return sqrt(pow((a.x - b.x), 2) + pow((a.y - b.y), 2))

def get_closest(object, list, regular=True):
    """Get the closest object from a list to another object. Note that other
    data types can be used, as long as they work with get_distance (meaning
    they have x and y properties). A problem with this function is when having
    many objects (1,000 or more), this can take time cycling through a big loop of
    objects.

    object - object to get distance
    list - list to get closest object
    regular - method of getting distance. If regular is set to True, then the
              regular function for getting distance (get_distance) is used. If
              it is set to False, then the other function is called
              (get_distance_). As documented, it is recommended to leave this
              value as is. Defaults to True.

    parameters:
        object - Point
        list - List (list of Points)
        regular - bool

    returns: tuple ((closest, distance))
    """

    if regular:
        method = get_distance

    else:
        method = get_distance_

    if not list:
        return (object, 0)

    position = 0
    distance = method(object, list[position])

    for i in range(1, len(list)):
        _distance = method(object, list[i])

        if _distance < distance:
            position = i
            distance = _distance

    return list[position], distance

def rotate_point(point, center, degrees, precision=2):
    """Rotate a Point a certain degrees around a center. This just changes the
    Point's properties and returns the changed x and y values.

    point - Point to rotate around center
    center - center the Point rotates around
    degrees - angle to rotate
    precision - precision of the calculation. This usually does not need to be
                enhanced, but it is common to lower the value. Defaults to 2.

    parameters: Point, Point, int
    returns: tuple (x, y)
    """

    temp_x = point.x - center.x
    temp_y = point.y - center.y

    # now apply rotation
    radians_ = radians(degrees)
    cos_angle = cos(radians_)
    sin_angle = sin(radians_)

    x = temp_x * cos_angle - temp_y * sin_angle
    y = temp_x * sin_angle + temp_y * cos_angle

    # translate back
    precision = 2

    x = round(x + center.x, precision)
    y = round(y + center.y, precision)

    point.x = x
    point.y = y

    return x, y

def get_angle_degrees(a, b):
    """Get angle degrees between two Points.

    a - first Point to get angle degrees
    b - second Point to get angle degrees

    parameters: Point, Point
    returns: int
    """

    x_diff = b.x - a.x
    y_diff = b.y - a.y

    angle = degrees(atan2(x_diff, y_diff))

    return angle

def get_angle_radians(a, b):
    """Get angle radians between two Points.

    a - first Point to get angle radians
    b - second Point to get angle radians

    parameters: Point, Point
    returns: int
    """

    x_diff = b.x - a.x
    y_diff = b.y - a.y

    angle = atan2(x_diff, y_diff)

    return angle

def degrees_to_radians(degrees, digits=2):
    """Convert degrees to radians.

    degrees - degrees to be converted to radians
    digits - number of digits of the π value. Defaults to 2, or 3.14.

    parameters: int
    returns: int
    """

    return degrees * round(pi, digits) / 180

def convert_xywh_to_points(point, width, height):
    """Convert an rectangle with center points and dimensions to only points.
    These are labeled as x1, y1, x2, y2. This can be used for widgets, because
    most of them only have rectangular bounding boxes.

    point - center Point of rectangle
    width - width of rectangle
    height - height of rectangle

    parameters: Point, int, int
    returns: tuple (x1, y1, x2, y2)
    """

    # Note this does not return two Points
    return (
        point.x - width / 2,
        point.y + height / 2,
        point.x + width / 2,
        point.y - height / 2
    )

def lerp(a, b, u):
    """Linearly interpolate between two values.

    a - first value of interpolation
    b - second value of interpolation

    parameters: int, int
    returns: int
    """

    return a + ((b - a) * u)

def lerp_point(point1, point2, u):
    """Linearly interpolate between two points.

    point1 - first Point of interpolation
    point2 - second Point of interpolation

    parameters: Point, Point, int
    returns: Point
    """

    point = (
        lerp(point1.x, point2.x, u),
        lerp(point1.y, point2.y, u)
    )

    return Point(*point)

def random_vector_in_rectangle(left, width, height):
    """Generate a point in a rectangle, or think of it as a vector pointing a
    random direction with a random magnitude less than the radius.

    left - bottom left corner of the rectangle. You can calculate this from the
           x and y center coordinates by doing this:

           >>> x = x - width / 2
           >>> y = y - height / 2

           >>> point = Point(x, y)

    width - width of the rectangle
    height - height of the rectangle

    parameters: Point, int, int
    """

    return (
            random.uniform(left[0], left[0] + width),
            random.uniform(left[1], left[1] + height)
           )

def random_vector_in_circle(center, radius):
    """Generate a point in a circle, or can think of it as a vector pointing a
    random direction with a random magnitude less than the radius.

    Reference: https://stackoverflow.com/a/30564123

    NOTE: This algorithm returns a higher concentration of points around the
          center of the circle

    center - center Point of the circle
    radius - radius of the circle (the distance from the center to the rim)

    parameters: Point, int
    returns: Point
    """

    # Random angle
    angle = 2 * pi * random()

    # Random radius
    r = radius * random()

    # Calculating coordinates
    point = Point(
                  r * cos(angle) + center[0],
                  r * sin(angle) + center[1]
                 )

    return point

def random_vector_on_line(point1, point2):
    """Given two Points defining a line, return a random point on that line.

    point1 - first Point of the line
    point2 - second Point of the line

    parameters: Point, Point
    returns: Point
    """

    u = uniform(0, 1)

    return lerp_point(point1, point2, u)

### DECEPRATED FUNCTIONS ###

def set_hitbox(object):
    height = object.height

    if not object.height:
        height = 1

    x1, y1 = -object.width / 2, - height / 2
    x2, y2 = +object.width / 2, - height / 2
    x3, y3 = +object.width / 2, + height / 2
    x4, y4 = -object.width / 2, + height / 2

    return [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]

def set_position(object):
    height = object.height

    if not object.height:
        height = 1

    object.right = object.x - object.width
    object.left = object.x + object.width
    object.top = object.y + height
    object.bottom = object.y - height

    object.hit_box = set_hitbox(object)

def convert_four_to_one_quadrants(x, y, width, height):
    x = width / 2 + x
    y = height / 2 + y

    return x, y
