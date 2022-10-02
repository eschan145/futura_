"""GUI interface and widgets. Documentation is found throughout the file,
though in some areas it may be obsolete or incomplete.

More than meets the eye in this example. To see all features, look at the source
code of each widget. This includes several different types of interactive
widgets and displays an example at the end. It also includes API for creating
your own widgets, which are quite easy to do. Everything is object-oriented,
which aids in accessing properties and setting them. Nearly all properties can
be accessed and set from creation. These built-in widgets have plenty of
documentation and functions.

Several widgets are provided to use. These include Image, Label, Button,
Slider, Toggle, Entry, Combobox, and various shapes. Like most projects based
off pyglet, in this GUI toolkit, all widgets subclass a base widget class,
which dispatches events to them.

This uses the awesome pyglet and arcade libraries, which are still active and
working today. Arcade's website is https://arcade.academy/, while pyglet's is
https://pyglet.org/.

Arcade does have a seperate GUI toolkit implemented, but it has fewer features
compared to this. It does have some special enhancements and functionality that
is not provided here, such as the ability to place widgets with layouts and
groups. This is being developed here.

Contributions are welcome. Visit my Github respository at
https://github.com/eschan145/futura. From there, you can submit pull requests
or chat in discussions.

Code and graphics by Ethan Chan

GitHub: eschan145
Discord: EthanC145#8543

Contact me at esamuelchan@gmail.com
"""

from html import entities
from html.parser import HTMLParser
from re import compile
from tkinter import TclError, Tk
from typing import Tuple
from webbrowser import open_new

from arcade import (ShapeElementList, Sprite, SpriteList,
                    create_rectangle_outline, draw_rectangle_outline,
                    get_window, load_texture)
from pyglet import options
from pyglet.app import run
from pyglet.clock import get_frequency
from pyglet.event import EventDispatcher
from pyglet.graphics import Batch
from pyglet.image import load
from pyglet.text import DocumentLabel, HTMLLabel, decode_attributed
from pyglet.text.caret import Caret
from pyglet.text.formats.html import (_block_containers, _block_elements,
                                      _metadata_elements, _parse_color,
                                      _whitespace_re)
from pyglet.text.formats.structured import (ImageElement, OrderedListBuilder,
                                            StructuredTextDecoder,
                                            UnorderedListBuilder)
from pyglet.text.layout import IncrementalTextLayout, TextLayout

from .color import (BLACK, COOL_BLACK, DARK_GRAY, DARK_SLATE_GRAY, RED,
                    four_byte)
from .file import (blank1, entry_focus, entry_hover, entry_normal, knob,
                   slider_horizontal, toggle_false, toggle_false_hover,
                   toggle_true, toggle_true_hover, widgets)
from .geometry import Point, are_rects_intersecting, get_distance
from .key import (ALT, CONTROL, ENTER, KEY_LEFT, KEY_RIGHT, MOTION_BACKSPACE,
                  MOTION_BEGINNING_OF_FILE, MOTION_BEGINNING_OF_LINE,
                  MOTION_COPY, MOTION_DELETE, MOTION_DOWN, MOTION_END_OF_FILE,
                  MOTION_END_OF_LINE, MOTION_LEFT, MOTION_NEXT_WORD,
                  MOTION_PREVIOUS_WORD, MOTION_RIGHT, MOTION_UP,
                  MOUSE_BUTTON_LEFT, SHIFT, SPACE, TAB, A, B, C, I, Keys, V, X)

options["debug_gl"] = False

MAX = 2 ** 32

clipboard = Tk()
clipboard.withdraw()

# Sides

LEFT = "left"
CENTER = "center"
RIGHT = "right"

TOP = "top"
BOTTOM = "bottom"

# Callbacks
SINGLE = 1
DOUBLE = 2
MULTIPLE = 3

SIMPLE = "simple"

KEYBOARD = "keyboard"
MOUSE = "mouse"
PROGRAM = "program"

DISABLE_ALPHA = 160 # Alpha of disabled widget
FOCUS_SIZE = 1.05 # [DEPRECATED]

ENTRY_BLINK_INTERVAL = 0.5

TOGGLE_VELOCITY = 2
TOGGLE_FADE = 17

SLIDER_VELOCITY = 10
KNOB_HOVER_SCALE = 1

SCROLLER_PADDING = 20

HORIZONTAL = "horizontal"
VERTICAL = "vertical"

DEFAULT_FONT_FAMILY = "Montserrat"
DEFAULT_FONT_SIZE = 12

DEFAULT_FONT = ["Montserrat", 12]

DEFAULT_LABEL_COLORS = [BLACK, (COOL_BLACK, DARK_SLATE_GRAY, DARK_GRAY)]

def _exclude(exclusions):
    import types

    # Add everything as long as it's not a module and not prefixed with _
    functions = [name for name, function in globals().items()
                 if not (name.startswith('_') or isinstance(function, types.ModuleType))]

    # Remove the exclusions from the functions
    for exclusion in exclusions:
        if exclusion in functions:
            functions.remove(exclusion)

    del types  # Deleting types from scope, introduced from the import

    return functions


# The _ prefix is important, to not add these to the __all__
# _exclusions = ["function1", "function2"]
# __all__ = _exclude(_exclusions)

def set_container(_container):
    """Set the current container. This can be used for multiple views or
    windows. It just sets container to the given parameter.

    _container - main container to be used

    parameters: Container
    """

    import gui.management as management

    management.container = _container

def get_container():
    """Get the current container.

    returns: Container
    """

    import gui.management as management

    return management.container

def clipboard_get():
    """Get some text from the clipboard. This cathces exceptions if an image
    is copied in the clipboard instead of a string.

    _tkinter.TclError:
    CLIPBOARD selection doesn't exist or form "STRING" not defined

    returns: str
    """

    try:
        return clipboard.clipboard_get()

    except TclError:
        return

def clipboard_append(text):
    """Append some text to the clipboard.

    text - text to append to the clipboard

    parameters: str
    """

    clipboard.clipboard_append(text)

def insert(index, text, add):
    """Insert some text to a string given an index. This was originally used for
    the entry widget but was deceprated when we found a faster and more
    efficient way to insert text.

    index - index of the text addition
    text - string to be edited
    add - new text to be inserted

    parameters: int, str, str
    returns: str
    """

    return text[:index] + add + text[index:]

def delete(start, end, text):
    """Delete some text to a string given an index. This was originally used for
    the entry widget but was deceprated when we found a faster and more
    efficient way to delete text.

    start - start index of the text removal
    end - end index of the text removal
    text - string to be edited

    parameters: int, int, str
    returns: str
    """

    if len(text) > end:
        text = text[:start] + text[end + 1::]
    return text

def convert_to_roman(number):
    """Convert an integer to a roman number, as in I, II, III, etc. The number
    must between 0 and 3999. The number is automatically converted to an
    integer to make it simple.

    From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/81611

    Raises a ValueError if the number is not valid (see below rules)

    number - number to be converted to roman. Must be between 0 and 3999.

    parameters: int
    returns: str
    """

    if not 0 < number < 4000:
        raise ValueError("Number must be between 1 and 3999")

    # Typically don't format like this, but it makes it neater and readable

    integers = (1000, 900,  500, 400, 100, 90,  50, 40,  10, 9,   5,  4,   1)
    numerals = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = ""

    for i in range(len(integers)):
        count = int(int(number) // integers[i])
        result += numerals[i] * count
        number -= integers[i] * count

    return result

class HTMLDecoder(HTMLParser, StructuredTextDecoder):
    """A custom HTML decoder based off pyglet's built-in one. This has limited
    functionality but still feature-rich. It is possible to modify styling and
    tag names by overriding this.
    """

    default_style = {
        "font_name" : "Montserrat",
        "font_size" : 12,
        "margin_bottom" : "1pt",
        "bold" : False,
        "italic" : False,
    }

    font_sizes = {
        1 : 8,
        2 : 10,
        3 : 12,
        4 : 14,
        5 : 18,
        6 : 24,
        7 : 48
    }

    def decode_structured(self, text, location):
        """Decode some structured text and convert it to the pyglet attributed
        text (vnd.pyglet-attributed).

        text - given HTML text to be decoded into pyglet attributed text
        location - location of images and filepaths for the document

        parameters: str, str
        """

        self.location = location
        self._font_size_stack = [3]
        self.list_stack.append(UnorderedListBuilder({}))
        self.strip_leading_space = True
        self.block_begin = True
        self.need_block_begin = False
        self.element_stack = ["_top_block"]
        self.in_metadata = False
        self.in_pre = False

        # Set default style

        self.push_style("_default", self.default_style)

        self.feed(text)
        self.close()

    def get_image(self, filename):
        """Get an image from a filename. This uses the location.

        filename - filename of image

        parameters: str
        """

        return load(filename, file=self.location.open(filename))

    def prepare_for_data(self):
        """Prepare the document for insertion of HTML text.
        """

        if self.need_block_begin:
            self.add_text("\n")
            self.block_begin = True
            self.need_block_begin = False

    def handle_data(self, data):
        """Handle HTML data. See handle_starttag for details.

        data - HTML data
        """

        if self.in_metadata:
            return

        if self.in_pre:
            self.add_text(data)

        else:
            data = _whitespace_re.sub(" ", data)

            if data.strip():
                self.prepare_for_data()

                if self.block_begin or self.strip_leading_space:
                    data = data.lstrip()
                    self.block_begin = False
                self.add_text(data)

            self.strip_leading_space = data.endswith(" ")

    def handle_starttag(self, tag, case_attributes):
        """Handle the start of tags for all HTML elements. This creates a map
        of all the elements and pushes its style to a pyglet structured text
        decoder. They may be upper or lower case. Note that you can use
        parse_distance to calculate the pixel distance from standard units like
        inches, millimeters, etc.

        Pyglet uses a subset of HTML 4.01 transitional.

        TODO: make code blocks have a gray background, keyboard blocks with a
              glowing gray background

        The following elements are currently supported.

        ALIGN B BLOCKQUOTE BR CODE DD DIR DL EM FONT H1 H2 H3 H4 H5 H6 I IMG
        KBD LI MENU OL P PRE Q STRONG SUB SUP U UL VAR

        The mark (bullet or number) of a list item is separated from the body
        of the list item with a tab, as the pyglet document model does not
        allow out-of-stream text. This means lists display as expected, but
        behave a little oddly if edited. Multi-level lists are supported.

        No style or script elements are currently supported.

        A description of each tag is found below.

        ALIGN - alignment of the text. This can be LEFT, CENTER, or RIGHT.
        B - bold or heavy text. This has no parameters, and is defined in
            Markdown as two asterisks (**). Alias of <strong>.
        BLOCKQOUTE - a quote of some text. Later, a line drawn on the left side
                     may be implemented. The left margin is indented by 60
                     pixels, but can be changed by specifying a padding
                     parameter. In Markdown, this is a greater than equal sign,
                     with the level on the number of signs.
        BR - a line break. This draws a horizontal line below the text.
        CODE - a code block. This is displayed as ` for single-line code and
               ``` for multiline code blocks in Markdown. This is an alias for
               <pre>
        DD - description, definition, or value for a item
        DIR - unordered list. This takes a type parameter, either CIRCLE or
              SQUARE. It defaults to a bullet point. Alias for <ul> and <menu>.
        DL - description list. This just sets the bottom margin to nothing.
        EM - italic or slanted text. This has no parameters. Alias for <i> and
             <var>.
        FONT - font and style of the text. It takes several parameters.
               family       font family of the text. This must be a pyglet
                            loaded font.
               size         size changes of the text. If negative the text will
                            shrink, and if positive the text will be enlarged.
                            If not specified the text size will be 3.
               real_size    actual font size of the text. This only accepts
                            positive values.
               color        font color of the text in RGBA format

        H1 - largest HTML heading. This sets the font size to 24 points. All
             headings except <h6> are bold.
        H2 - second largest HTML heading. This sets the font size to 18 points.
        H3 - third largest HTML heading. This sets the font size to 16 points.
        H4 - fourth largest HTML heading. This sets the font size to 14 points.
        H5 - fifth largest HTML heading. This sets the font size to 12 points.
        H6 - a copy of <h5>, but with italic instead of bold text

        I - italic or slanted text. This has no parameters. Alias for <em> and
            <var>.
        IMG - display an image. This takes several parameters.
              filepath      filepath of the image. This is not a loaded image.
              width         width of the image. This must be set to a value
                            greater than 0, or the image will not be rendered.
              height        height of the image. This must be set to a value
                            greater than 0, or the image will not be rendered.
        KBD - display keyboard shortcut
        LI - display a list item. This should be inserted in a ordered or
             unordered list, like this.

             <ul> My special list
                 <li> My first list item </li>
                 <li> My second list item </li>
             </ul>

        MENU - unordered list. This takes a type parmeter, either CIRCLE or
               SQUARE. It defaults to a bullet point. Alias for <dir> and <ul>.
        OL - ordered list. Instead of having symbols, this uses sequential
             titles. Parameters and options are listed below.
             start          start title of ordered list. (int)
             format         list format. Pyglet's ordered list supports
                            1       Decimal arabic (1, 2, 3)
                            a       Lowercase alphanumeric (a, b, c)
                            A       Uppercase alphanumeric (A, B, C)
                            i       Lowercase roman (i, ii, i)
                            I       Uppercase roman (I, II, III)

                            These values can contain prefixes and suffixes,
                            like "1.", "(1)", and so on. If the format is
                            invalid a question mark will be used instead.
        P - paragraph. This is different that just plain HTML text, as it will
            be formatted to the guidelines of a paragraph. This takes a align
            parameter, either LEFT, CENTER, or RIGHT. Defaults to LEFT.
        PRE - a code block. This is displayed as ` for single-line code and
              ``` for multiline code blocks in Markdown. This is an alias to
              <code>
        Q - inline quotation element. This adds formal quotation marks around
            enclosed text. NOTE: not a regular ".
        STRONG - bold or heavy text. This has no parameters, and is defined in
                 Markdown as two asterisks (**). Alias of <b>
        SUB - subscript text. Enclosed text is offset by points given in the
              baseline parameter. This has two parameters.
              size          size decrement of the enclosed text. This is the
                            amount the text is leveled down.
              baseline      offset of the enclosed text. This should be
                            negative. Defaults to -3 points.
        SUP - superscript text. Enclosed text is offset by points given in the
              baseline parameter. This has two parameters.
              size          size increment of the enclosed text. This is the
                            amount the text is leveled up.
              baseline      offset of the enclosed text. This should be
                            positive. Defaults to 3 points.
        U - underlined text. This can take an optional color argument for the
            color of the underline. If not specified this defaults to BLACK.
        UL - unordered list. This takes a type parameter, either CIRCLE or
             SQUARE. It defaults to a bullet point. Alias for <dir> and <menu>.
        VAR -  italic or slanted text. This has no parameters. Alias for <i>
               and <em>.
        """

        if self.in_metadata:
            return

        element = tag.lower()
        attributes = {}

        for key, value in case_attributes:
            attributes[key.lower()] = value

        if element in _metadata_elements:
            self.in_metadata = True

        elif element in _block_elements:
            # Pop off elements until we get to a block container

            while self.element_stack[-1] not in _block_containers:
                self.handle_endtag(self.element_stack[-1])

            if not self.block_begin:
                self.add_text("\n")

                self.block_begin = True
                self.need_block_begin = False

        self.element_stack.append(element)

        style = {}

        if element in ("b", "strong"):
            style["bold"] = True

        elif element in ("i", "em", "var"):
            style["italic"] = True

        elif element in ("tt", "code", "kbd"):
            color = self.current_style.get("color")

            if color is None:
                color = attributes.get("background_color") or \
                    (246, 246, 246, 255)

            style["font_name"] = "Courier New"
            style["background_color"] = color

        elif element == "u":
            color = self.current_style.get("color")

            if color is None:
                color = attributes.get("color") or [0, 0, 0, 255]

            style["underline"] = color

        elif element == "font":
            if "family" in attributes:
                style["font_name"] = attributes["family"].split(",")

            if "size" in attributes:
                size = attributes["size"]

                try:
                    if size.startswith("+"):
                        size = self._font_size_stack[-1] + int(size[1:])

                    elif size.startswith("-"):
                        size = self._font_size_stack[-1] - int(size[1:])

                    else:
                        size = int(size)

                except ValueError:
                    size = 3

                self._font_size_stack.append(size)

                if size in self.font_sizes:
                    style["font_size"] = self.font_sizes.get(size, 3)

            elif "real_size" in attributes:
                size = int(attributes["real_size"])

                self._font_size_stack.append(size)
                style["font_size"] = size

            else:
                self._font_size_stack.append(self._font_size_stack[-1])

            if "color" in attributes:
                try:
                    style["color"] = _parse_color(attributes["color"])

                except ValueError:
                    pass

        elif element == "sup":
            size = self._font_size_stack[-1] - (attributes.get("size") or 1)

            style["font_size"] = self.font_sizes.get(size, 1)
            style["baseline"] = attributes.get("baseline") or "3pt"

        elif element == "sub":
            size = self._font_size_stack[-1] - (attributes.get("size") or 1)

            style["font_size"] = self.font_sizes.get(size, 1)
            style["baseline"] = attributes.get("baseline") or "-3pt"

        elif element == "h1":
            style["font_size"] = 24
            style["bold"] = True

        elif element == "h2":
            style["font_size"] = 18
            style["bold"] = True

        elif element == "h3":
            style["font_size"] = 16
            style["bold"] = True

        elif element == "h4":
            style["font_size"] = 14
            style["bold"] = True

        elif element == "h5":
            style["font_size"] = 12
            style["bold"] = True

        elif element == "h6":
            style["font_size"] = 12
            style["italic"] = True

        elif element == "br":
            self.add_text(u"\u2028")

            self.strip_leading_space = True

        elif element == "p":
            if attributes.get("align") in ("left", "center", "right"):
                style["align"] = attributes["align"]

        elif element == "align":
            style["align"] = attributes.get("type")

        elif element == "pre":
            style["font_name"] = "Courier New"
            style["margin_bottom"] = 0

            self.in_pre = True

        elif element == "blockquote":
            padding = attributes.get("padding") or 60

            left_margin = self.current_style.get("margin_left") or 0
            right_margin = self.current_style.get("margin_right") or 0

            style["margin_left"] = left_margin + padding
            style["margin_right"] = right_margin + padding

        elif element == "q":
            self.handle_data(u"\u201c")

        elif element == "ol":
            try:
                start = int(attributes.get("start", 1))
            except ValueError:
                start = 1

            format = attributes.get("format", "1.")

            builder = OrderedListBuilder(start, format)

            builder.begin(self, style)
            self.list_stack.append(builder)

        elif element in ("ul", "dir", "menu"):
            type = attributes.get("type", "circle").lower()
            detail = attributes.get("detail")

            if detail and not type:
                raise UnicodeDecodeError("If a detail is specified, then a " \
                                         "type must also be specified. " \
                                         "Built in styles include circles, " \
                                         "squares, arrows, and checkboxes."
                                        )

            elif type == "square":
                mark = u"\u25a1" # □
            else:
                if type:
                    mark = type
                else:
                    mark = u"\u25cf"

            if detail:
                if type == "circle":
                    if detail == "empty":
                        mark = u"\u25CB" # ○
                    elif detail == "filled":
                        mark = u"\u25CF" # • # ●‿●
                if type == "arrow":
                    if detail == "black-white":
                        mark = u"\u27A3" # ➢
                    elif detail == "white-black":
                        mark = u"\u27A2" # ➣
                elif type == "checkbox":
                    if detail == "check":
                        # Might not work on some platforms and fonts
                        mark = u"\u2611" # ☑
                    elif detail == "cross":
                        mark = u"\u2612" # ☒

            else:
                if type == "arrow":
                    mark = u"\u27A4" # ➤
                elif type == "checkbox":
                    mark = u"\u2610" # ☐
                elif type == "circle":
                    mark = u"\u25CF"
                elif type == "dash":
                    mark = u"\u2014"

            builder = UnorderedListBuilder(mark)

            builder.begin(self, style)
            self.list_stack.append(builder)

        elif element == "li":
            self.list_stack[-1].item(self, style)
            self.strip_leading_space = True

        elif element == "dl":
            style["margin_bottom"] = 0

        elif element == "dd":
            left_margin = self.current_style.get("margin_left") or 0
            style["margin_left"] = left_margin + 30

        elif element == "img":
            image = self.get_image(attributes.get("filepath"))

            if image:
                width = attributes.get("width")

                if width:
                    width = int(width)

                height = attributes.get("height")

                if height:
                    height = int(height)

                self.prepare_for_data()

                self.add_element(ImageElement(image, width, height))
                self.strip_leading_space = False

        self.push_style(element, style)

    def handle_endtag(self, tag):
        """Handle the end tags for the HTML document. They may be upper or lower case.
        """

        element = tag.lower()

        if element not in self.element_stack:
            return

        self.pop_style(element)

        while self.element_stack.pop() != element:
            pass

        if element in _metadata_elements:
            self.in_metadata = False
        elif element in _block_elements:
            self.block_begin = False
            self.need_block_begin = True

        if element == "font" and len(self._font_size_stack) > 1:
            self._font_size_stack.pop()
        elif element == "pre":
            self.in_pre = False
        elif element == "q":
            self.handle_data(u"\u201d")
        elif element in ("ul", "ol"):
            if len(self.list_stack) > 1:
                self.list_stack.pop()

    def handle_entityref(self, name):
        """Handle entity references from the HTML document.
        """

        if name in entities.name2codepoint:
            self.handle_data(chr(entities.name2codepoint[name]))

    def handle_charref(self, name):
        """Handle character references from the HTML document. This is used
        internally for the pyglet document formatter.
        """

        name = name.lower()

        try:
            if name.startswith("x"):
                self.handle_data(chr(int(name[1:], 16)))
            else:
                self.handle_data(chr(int(name)))
        except ValueError:
            pass


class HTMLLabel(DocumentLabel):

    def __init__(self, text="", location=None,
                 x=0, y=0, width=None, height=None,
                 anchor_x='left', anchor_y='baseline',
                 multiline=False):
        self._text = text
        self._location = location

        document = HTMLDecoder().decode(text, location)
        document.label = self

        DocumentLabel.__init__(self, document, x, y, width, height,
                               anchor_x, anchor_y, multiline, None,
                               get_container().batch, None)

    def _get_text(self):
        return self._text

    def _set_text(self, text):
        if text == self._text:
            return

        self._text = text

        self.document = HTMLDecoder().decode(text)
        self.document.label = self

    text = property(_get_text, _set_text)


class WidgetsError(Exception):
    """Widgets error. When creating custom widgets, this can be invoked. Only
    use this if you need to, like if it is going to cause something to hang or
    crash, or it raises an unhelpful error. Making this unnecessary will be
    annoying in some scenarios. If the user absolutely wants to do something
    and this error keeps on being raised, this is aggravating and he will have
    to edit the source code.
    """


class Font:
    """An object-oriented Font."""

    def __init__(self,
                 family=DEFAULT_FONT_FAMILY,
                 size=DEFAULT_FONT_SIZE
                ):

        """Initialize an object-oriented Font. This is an experimental
        feature and has no effect.

        family - family of the font (style)
        size - size of the font (not in pixels)

        parameters: int, int
        """

        self.family = family
        self.size = size

        self.list = [self.family, self.size]

    def __getitem__(self, item):
        """Get an item from the list.

        item - item whose value to be returned

        parameters: int
        returns: str or int
        """

        return self.list[item]

    def __setitem__(self, index, item):
        """Get an item from the list.

        item - item whose value to be set

        parameters: int, str or int
        """

        self.list[index] = item


default_font = Font()


class Container:
    """Container class to draw and update widgets. One current problem is that
    each widget in its widget spritelist is being drawn every frame
    individually.

    You should create a Container in the __init__ function of your application,
    and before creating any widgets. It will automatically push events so you
    don't need to call pyglet.window.Window.push_handlers yourself or manually
    dispatch events.

    Containers have several useful properties, like getting the current
    application focus and the list of created widgets. You can exit the
    application (if you are going to create a new arcade.View or hide the
    application) by calling the exit function. You can also call draw_bbox or
    its aliases to draw each bounding box for each widget.

    All properties are listed here:

    focus - current widget with application focus. See Widget.on_focus for
            details.
    enable - whether the container is enabled or not
    widgets - list of widgets that have been
    """

    def __init__(self, window=None):
        """Initialize a container. You shouldn't usually need to create an
        instance of this class directly, unless managing multiple windows.
        """

        self.window = window or get_window()

        self.focus = None
        self.enable = True

        self.widgets = []
        self.fps_list = []
        self.added_widgets = []
        self.groups = []

        self.track_fps = True

        self._window = self.window

        self.batch = Batch()
        self.widget_sprites = SpriteList()

    def _get_window(self):
        """Current arcade window of the container. Sometimes using
        arcade.get_window doesn't work properly, do to GL context errors.

        type: property, arcade.Window
        """

        return self._window

    def _set_window(self, window):
        self._window = window or get_window()

        self._window.push_handlers(self)

    def _get_title(self):
        """Title or caption of the window. This is the text that is displayed
        on the top of the screen. Currently, changing text color, font, and
        other styles is not supported. In the future, a custom toolbar could be
        implemented, for customization of colors and styles.

        Raises AssertionError if there is no set window.

        type: property, str
        """

        assert self.window, (
                             "No window is active. It has not been created "
                             "yet, or it was closed. Be sure to set the "
                             "window property of the container before adding "
                             "any widgets."
                            )

        return self.window.get_caption()

    def _set_title(self, title):
        assert self.window, (
                             "No window is active. It has not been created "
                             "yet, or it was closed. Be sure to set the "
                             "window property of the container before adding "
                             "any widgets."
                            )

        if not title:
            title = ""

        title = str(title)

        self.window.set_caption(str(title))

    def _get_fps(self):
        """Current update rate in frames per second (fps). This should not vary
        between multiple containers. Drawing a fps display can aid in profiling
        and measuring of the time between code.

        This property is read-only.

        NOTE: this is not the refresh rate. The refresh rate is how fast the
              monitor redraws itself. Most monitors have a refresh rate of 60
              hertz or 120 hertz. Fps is the number of update frames per
              second. Higher fps will speed up events and collision checks.

        returns: float
        """

        # Don't use arcade.get_fps(). This measures incorrectly.

        return get_frequency()

    def _get_average_fps(self):
        """Average update rate in frames per second (fps). The items of the fps
        list are averaged and returned.

        This property is read-only.

        returns: float
        """

        # Don't use arcade.get_fps(). This measures incorrectly.

        return sum(self.fps_list) / len(self.fps_list)

    window = property(_get_window, _set_window)
    title = property(_get_title, _set_title)
    fps = property(_get_fps)
    average_fps = property(_get_average_fps)

    def add(self, *widgets):
        """Add widgets to the drawing list. Unfortunately each widget must be
        drawn individually instead of drawing them in a batch, which really
        slows down performance with hundreds of widgets. This is called
        internally for all widgets. If you are not going to subclass the base
        widget class, you will need to do this manually.

        Raises AssertionError if there is no set window.

        widgets *- widget to add to the list

        parameters: Widget
        """

        assert self.window, (
                             "No window is active. It has not been created "
                             "yet, or it was closed. Be sure to set the "
                             "window property of the container before adding "
                             "any widgets."
                            )

        for widget in widgets:
            if not isinstance(widget, Image):
                self.widgets.append(widget)

            self.added_widgets.append(widget)

        self.focus = widgets[-1]

    def draw(self):
        """Draw the container's widgets. This should be manually called in the
        draw function of your application.
        """

        self.widget_sprites.draw()

        [widget.draw() for widget in self.widgets]

        for group in self.groups:
            group.draw()

        if self.track_fps:
            self.fps_list.append(self.fps)

        with self.window.ctx.pyglet_rendering():
            self.batch.draw()

            # A shadow effect not in progress anymore

            # Interesting feature:
            # Press Control + slash when on the line with "shade = 1"
            # The text "shade" will turn light green for a second.

            # shade = 1

            # if self.shadow:
            #     for i in range(1, 100):
            #         shade += 0.01
            #         print(scale_color(self.shadow, int(shade)))
            #         draw_rectangle_outline(widget.x, widget.y,
            #                                 widget.width + 1, widget.height + 1,
            #                                 RED)

    def draw_bbox(self, width=1, padding=0):
        """Draw the bounding box of each widget in the list. The drawing is
        cached in a ShapeElementList so it won't take up more time. This can
        also be called draw_hitbox or draw_hit_box.

        width - width of the bounding box outline
        padding - padding around the widget
        """

        [widget.draw_bbox(width, padding) for widget in self.widgets]

    draw_hitbox = draw_bbox # Alias
    draw_hit_box = draw_bbox

    def exit(self):
        """Exit the event sequence and delete all widgets. This sets its
        enable property to False.
        """

        [widget.delete() for widget in self.widgets]

        self.widgets = []

        self.enable = False

    def on_key_press(self, keys, modifiers):
        """A key is pressed. This is used to detect focus change by pressing
        Tab and Shift-Tab.
        """

        if keys == TAB:
            if modifiers & SHIFT:
                direction = -1
            else:
                direction = 1

            if self.focus in self.widgets:
                i = self.widgets.index(self.focus)
            else:
                i = 0
                direction = 0

            self.focus = self.widgets[(i + direction) % len(self.widgets)]

            if self.focus.children:
                self.focus.focus = True

            for widget in self.widgets:
                if not widget == self.focus:
                    if widget.children:
                        widget.focus = False


class Rect(Sprite):
    """Rect class for bounding box and collision calculations. Supports border
    properties, and is subclassed by the widget class. Positioning and related
    properties are defined here.
    """

    _x = 0
    _y = 0

    _point = Point(0, 0)

    def _update_position(self, x, y):
        """Update the position of the widget. This is called whenever position
        properties are changed, and should be made internally in the widget.
        It should set the component properties of the widget to the given
        coordinates.
        """

    def _get_x(self):
        """Center x position of the rect.

        type: property, int
        """

        return self._x

    def _set_x(self, x):
        self._x = x
        self._update_position(x, self.y)

    def _get_y(self):
        """Center y position of the rect.

        type: property, int
        """

        return self._y

    def _set_y(self, y):
        self._y = y
        self._update_position(self.x, y)

    def _get_point(self):
        """Center x and y position of the widget, as a Point.

        type: property, Point
        """

        return self._point

    def _set_point(self, point):
        self._point = point

        self.x = point.x
        self.y = point.y

    def _get_left(self):
        """Left x position of the widget.

        type: property, int
        """

        return self.x - self.width / 2

    def _set_left(self, left):
        self.x = left + self.width / 2 # Opposite, if you think about it

    def _get_right(self):
        """Right x position of the widget.

        type: property, int
        """

        return self.x + self.width / 2

    def _set_right(self, right):
        self.x = right - self.width / 2

    def _get_top(self):
        """Top y position of the widget.

        type: property, int
        """

        return self.y + self.height / 2

    def _set_top(self, top):
        self.y = top - self.height / 2

    def _get_bottom(self):
        """Bottom y position of the widget.

        type: property, int
        """

        return self.y - self.height / 2

    def _set_bottom(self, bottom):
        self.y = bottom + self.height / 2

    def _get_width(self):
        """Get the width of the widget.

        This property is read-only.

        returns: int
        """

        if not self.widget:
            return 0

        try:
            if isinstance(self.widget, TextLayout):
                return self.widget.content_width

            return self.widget._width

        except AttributeError: # Non-supported widget
            raise WidgetsError(f"Non-supported widget type "
                               "{type(self.widget)}. Valid types must have "
                               "_width and _height or content_width and "
                               "content_height properties."
                              )

    def _get_height(self):
        """Get the height of the widget.

        This property is read-only.

        returns: int
        """

        if not self.widget:
            return 0

        try:
            if isinstance(self.widget, TextLayout):
                return self.widget.content_height

            return self.widget._height

        except AttributeError: # Non-supported widget
            raise WidgetsError(f"Non-supported widget type "
                               "{type(self.widget)}. Valid types must have "
                               "_width and _height or content_width and "
                               "content_height properties."
                              )

    x = property(_get_x, _set_x)
    y = property(_get_y, _set_y)
    point = property(_get_point, _set_point)
    left = property(_get_left, _set_left)
    right = property(_get_right, _set_right)
    top = property(_get_top, _set_top)
    bottom = property(_get_bottom, _set_bottom)
    width = property(_get_width)
    height = property(_get_height)

    def _check_collision(self, point):
        """Check if a x and y position exists within the widget's hit box. This
        is an alternative to check_collision, and should only be used if you
        are not using any components (ex. label widget), or they do not have
        left, right, top and bottom properties.

        Do not use this for shapes. Create your own custom one, as this
        accesses GUI widget x and y properties, which not all shapes have.

        TODO: replace x and y parameters with Point (COMPLETED)

        point - point to check for collision

        parameters: int, int
        returns: bool
        """

        return (0 < point.x - self.x < self.width and
                0 < point.y - self.y < self.height)

    def check_collision(self, point):
        """Check if a x and y position exists within the widget's hit box. This
        should be used if you are using components, or if they do have left,
        right, top and bottom properties.

        Do not use this for shapes. Create your own custom one, as this
        accesses GUI widget x and y properties, which not all shapes have.

        TODO: replace x and y parameters with Point (COMPLETED)

        point - point to check for collision

        parameters: int, int
        returns: bool
        """

        if self._right and \
           self._left and \
           self._top and \
           self._bottom:
            return point.x > self._left and point.x < self._right and \
                   point.y > self._bottom and point.y < self._top

        return point.x > self.left and point.x < self.right and \
               point.y > self.bottom and point.y < self.top

    def is_colliding(self, rect):
        """Check if the rect is colliding with a given one.

        returns: bool
        """

        return are_rects_intersecting(self, rect)

    def draw_bbox(self, width=1, padding=0):
        """Draw the bounding box of the widget. The drawing is cached in a
        ShapeElementList so it won't take up more time. This can also be called
        draw_hitbox or draw_hit_box.

        Do not use this for shapes. Create your own custom one, as this
        accesses GUI widget x and y properties, which not all shapes have.

        width - width of the bounding box outline
        padding - padding around the widget

        parameters: int, int
        """

        if self.shapes is None:
            shape = create_rectangle_outline(self.x, self.y,
                                             self.width + padding,
                                             self.height + padding,
                                             RED, width
                                            )

            self.shapes = ShapeElementList()
            self.shapes.append(shape)

            self.shapes.center_x = self.x
            self.shapes.center_y = self.y
            self.shapes.angle = self.angle

    draw_hitbox = draw_bbox # Alias
    draw_hit_box = draw_bbox

    def snap_to_point(self, point, distance, move=True):
        """Snap the widget's position to a Point. This is useful in dragging
        widgets around, so snapping can make them snap to position if they are
        aligned to a certian widget, etc.

        Do not use this for shapes. Create your own custom one, as this
        accesses GUI widget x and y properties, which not all shapes have.

        point - Point for the widget to snap to. Typically this should be a
                mouse position.
        distance - distance of the snapping. This gives the user less freedom
                   but makes it easier for larger snaps.
        move - move the widget towards the snapping point. If this is False,
               then coordinates will be returned. Defaults to True.

        parameters: Point
        returns: bool (whether or not the widget was snapped to position) or
                 Point
        """

        if get_distance(self, point) <= distance:
            if move:
                self.x = point.x
                self.y = point.y

                return True

            return point


class Widget(Rect, EventDispatcher):
    """Create a user interface GUI widget. This is a high-level class, and is
    not suitable for very complex widgets. It comes with built-in states,
    which can be accessed just by getting its properties. Dispatching events
    makes subclassing a widget and creating your own very easy.

    Widgets must have several things.

    1. Specified main widget in widget parameter

       This part must be set. Some different elements are supported by Futura,
       including pyglet.text.layouts.TextLayouts and arcade.Sprites. Basically,
       anything with _width and _height or content_width and _content_height
       properties.

       It is the widget that takes the hitbox points for collision detection.

    2. Children (sometimes)

       Widgets should have children if they have elements from other widgets.
       Very primitive elements are not necessary for this. A widget with
       children is recognized as a group of widgets, and therefore can have
       focus traversal. Single widgets, without any children, are not
       recognized by focus traversal.

    3. Drawing and update functions

       Widgets must have a draw function defined. It may be blank. In the
       future this may be made optional. They should also have an update
       function.

    If you have an error, double-check your code is using the right datatype
    or the value is valid.

    Plenty of things are built-in here. For example, you can access the
    current window just by using the window property. Or the key state handler
    with the key property. You can draw the hit box of a widget for debugging,
    and performance is not lost because the drawing is cached. When removing a
    widget, use its delete function.

    There are dozens and dozens of properties for the widget. You can add an
    arcade Shape to its ShapeElementList, in the shapes property. Key state
    handlers are aleady built-in, along with mouse state handlers.

    You can access the widget's state by properties. Several built-in states
    are supported: normal, hover, press, disable, and focus. A disabled widget
    cannot have focus. It is highly not recommended to change any of these
    properties, as these may lead to drawing glitches. One exception is when
    defining them in the beginning.

    TODO: of course, there are many enhancements and other things that need to
          be worked on for the built-in widgets. If you would like to work on
          these post your enhancements in the discussions.

        1. Adding left, right, top, and bottom properties to widgets. This has
           been implemented in arcade sprites and should be for this too. It
           can be useful for enhanced positioning.
           - Create an _set_coords() function that is called whenever border
             position properties are modified
           - Add setting properties for each widget. This is not recommended
             because it's a hassle to code and will take up more space.
           - Make functions like set_border_coords

           (COMPLETED)

        2. Move documentation from setters to getters for properties. I think
           this is a big stretch; it will cost me literally thousands of
           deletions on my repository.

           Actually not really. I was able to do this without too many
           deletions.
    """

    def __init__(self, widget=None, image=blank1, scale=1.0, frame=None):
        """Here's an example of a widget. This _colorchooser dispatches events,
        so a widget that subclasses it can use them.

        >>> class _Colorchooser(Widget):

                def __init__(self):
                    self.image = Image("colorchooser.png")
                    Widget.__init__(self)

                def on_press(self, x, y, buttons, modifiers):
                    color = self.get_color_from_pos(x, y)
                    self.dispatch_event("on_color_pick", color)

                def get_color_from_pos(self, x, y):
                    # Get a color from x, y
                    pass

        >>> _Colorchooser.register_event_type("on_color_pick")

        On lines 1-5 we create and initialize the widget. An event is
        dispatched by the widget called on_press when the widget is pressed.
        This _colorchooser widget then dispatches an event, called
        "on_color_pick", with its parameters listed beside it. At the end of
        defining the widget you have to register it, so we do that in the last
        line. This just confirms to pyglet that we're creating an event.

        Now, the actual colorchooser would look like this:

        >>> class Colorchooser(_Colorchooser):

                def __init__(self):
                    _Colorchooser.__init__(self)

                def on_color_pick(self, color):
                    print("Color picked: ", color)
        _______________________________________________________________________

        widget - widgets and components to be added. If you are creating
                 components, add them before initializing the widget. These
                 help calculate the hitbox or bounding box.
        image - image to be displayed. Use this only for defining an image
                widget, though one is already pre-defined.
        scale - scale of the widget. This has been deceprated, as setting this
                to a value different that one will mess up the widget's bbox
        frame - not yet implemented. This is supposed to have a frame widget,
                which stores multiple widgets. It's similar to tkinter's Frame.

        parameters:
            widgets: tuple
            image - str (filepath) or arcade.Texture
        """

        Rect.__init__(self, image, scale)

        # Super messy, but it works

        # for var in vars(self):
        #     # if hasattr(var, "width") or \
        #     #     hasattr(var, "content_width"):
        #     #     if hasattr(var, "height") or \
        #     #     hasattr(var, "content_height"):
        #     #         if hasattr(var, "content_width") or \
        #     #             hasattr(var, "content_height"):
        #     #             self.width = var.content_width
        #     #             self.height = var.content_height

        #     #         else:
        #     #             self.width = var.width
        #     #             self.height = var.height

        #     attribute = getattr(self, var)

        #     # TODO: support more instances

        #     if isinstance(attribute, Widget) or isinstance(var, Sprite):
        #         self.width = attribute.width
        #         self.height = attribute.height

        #     elif isinstance(attribute, TextLayout):
        #         pass

        #         # Doesn't work with widgets with images and buttons

        #         # self.width = attribute.content_width
        #         # self.height = attribute.content_height

        self.container = get_container()

        self.children = None

        self.hover = False
        self.press = False
        self.disable = False

        self.widget = widget

        self.drag = False

        self.component = None

        self._left = None
        self._right = None
        self._top = None
        self._bottom = None

        self._focus = False

        self.frames = 0

        self.last_press = Point(0, 0)

        assert get_container() is not None, \
               "You must create a container before adding any widgets."

        self.keys = Keys()
        self.shapes = None

        self.window = get_window()

        self.window.push_handlers(
            self.on_key_press,
            self.on_key_release,
            self.on_mouse_motion,
            self.on_mouse_press,
            self.on_mouse_release,
            self.on_mouse_scroll,
            self.on_mouse_drag,
            self.on_text_motion_select,
            self.on_deactivate,
            self.on_update
        )

    def _get_focus(self):
        """Focus of the widget. Setting the focus for a widget removes focus
        for all other widgets. If the focus is false, the previous widget will
        attempt to recieve focus.

        Raises ValueError if there are one or fewer widgets in the widget list
        and focus is set to False. Technically, this should do nothing if
        raised.

        See on_focus for details.

        focus - focus to be enabled/disabled for the widget

        parameters: bool
        returns: bool
        """

        return self._focus

    def _set_focus(self, focus):
        self._focus = focus

        if focus:
            self.container.focus = self

            self.dispatch_event("on_focus", PROGRAM)

            # Remove all other widgets' focus

            for widget in self.container.added_widgets:
                if widget.children and not widget == self:
                    widget.focus = False

        else:
            if len(self.container.added_widgets) <= 1:
                raise ValueError("You must have at least two widgets added "
                                 "when setting focus of a widget to False. "
                                 "The previous widget should be set focus."
                                )

            index = self.container.added_widgets.index(self)

            self.container.focus = self.container.added_widgets[index - 1]

    focus = property(_get_focus, _set_focus)

    def delete(self):
        """Delete this widget and remove it from the event stack. The widget
        is not drawn and will not be accepting any events. You may want to
        override this if creating your own custom widget.

        Do not use this for shapes. Create your own custom one, as this
        accesses GUI widget x and y properties, which not all shapes have.

        If overriding this, you should remove all bindings of the widget and
        all events.
        """

        self.bindings = []
        self.disable = True
        self.focus = False

        self.window.remove_handlers(
            self.on_key_press,
            self.on_key_release,
            self.on_mouse_motion,
            self.on_mouse_press,
            self.on_mouse_release,
            self.on_mouse_scroll,
            self.on_mouse_drag,
            self.on_text_motion_select,
            self.on_deactivate,
            self.on_update
        )

        self.remove_from_sprite_lists()

    def on_key_press(self, keys, modifiers):
        """The user pressed a key(s) on the keyboard.

        keys - key pressed by the user. In pyglet, this can be called symbol.
        modifiers - modifiers held down during the key press.

        parameters: int (32-bit), int (32-bit)
        """

        if self.disable or not self.focus:
            return

        self.dispatch_event("on_key", keys, modifiers)

        if self.focus:
            if self.children:
                self.dispatch_event("on_focus", KEYBOARD)

            # for widget in self.container.widgets:
            #     if not widget == self:
            #         widget.focus = False

    def on_key_release(self, keys, modifiers):
        """The user released a key(s) on the keyboard.

        keys - key released by the user. In pyglet, this can be called symbol.
        modifiers - modifiers held down during the key press.

        parameters: int (32-bit), int (32-bit)
        """

        if self.disable or not self.focus:
            return

        self.press = False

        self.dispatch_event("on_lift", keys, modifiers)

    def on_mouse_motion(self, x, y, dx, dy):
        """The user moved the mouse.

        x - x position of mouse
        y - y position of mouse
        dx - x vector in last position from mouse
        dy - y vector in last position from mouse

        parameters: int, int, int, int
        """

        if self.disable:
            return

        if self.check_collision(Point(x, y)):
            self.hover = True

            self.dispatch_event("on_hover", x, y, dx, dy)
        else:
            self.hover = False

    def on_mouse_press(self, x, y, buttons, modifiers):
        """The user pressed a mouse button.

        x - x position of press
        y - y position of press
        buttons - buttons defined in keyboard pressed
        modifiers - modifiers held down during the press

        parameters: int, int, int (32-bit), int (32-bit)
        """

        if self.disable:
            return

        self.last_press = Point(x, y)

        if self.check_collision(Point(x, y)):
            self.press = True

            if self.children:
                self.focus = True

            self.dispatch_event("on_press", x, y, buttons, modifiers)
            self.dispatch_event("on_focus", MOUSE)

    def on_mouse_release(self, x, y, buttons, modifiers):
        """The user released a mouse button.

        x - x position of press
        y - y position of press
        buttons - buttons defined in keyboard released
        modifiers - modifiers held down during the release

        parameters: int, int, int (32-bit), int (32-bit)
        """

        if self.disable:
            return

        self.press = False

        self.drag = False

        self.dispatch_event("on_release", x, y, buttons, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """The user dragged the mouse.

        x - x position of mouse during drag
        y - y position of mouse during drag
        dx - movement of mouse in vector from last position
        dy - movement of mouse in vector from last position
        buttons - buttons defined in keyboard during drag
        modifiers - modifiers held down during the during drag

        parameters: int, int, int, int, int (32-bit), int (32-bit)
        """

        if self.disable:
            return

        if not self.check_collision(Point(x, y)):
            if not self.check_collision(self.last_press):
                return

        self.drag = True

        if self.check_collision(Point(x, y)):
            self.dispatch_event("on_drag", x, y, dx, dy, buttons, modifiers)

    def on_mouse_scroll(self, x, y, sx, sy):
        """The user scrolled the mouse.

        x - x position of mouse during drag
        y - y position of mouse during drag
        scroll - scroll vector (positive being the mouse wheel up, negative the
                 mouse wheel down)

        parameters: int, int, Point
        """

        if self.disable:
            return

        if self.check_collision(Point(x, y)):
            if self.disable:
                return

            self.dispatch_event("on_scroll", x, y, Point(sx, sy))

    def on_text_motion_select(self, motion):
        """Some text in an pyglet.IncrementalTextLayout was selected. This is
        only used for entry widgets. See the entry widget on_text_select docs
        for more info.
        """

        self.dispatch_event("on_text_select", motion)

    def on_deactivate(self):
        """The window was deactivated. This means that the user switched the
        current window focus to an external application.
        """

        # for widget in self.widgets:
        #     widget.focus = widget.hover = False

    def on_update(self, delta):
        """Update the widget. Only do collision checking and property updating
        here. Drawing goes in the draw function.

        delta - time elapsed since last this function was last called
        """

        self.frames += 1

        # if self.widget:
        #     try:
        #         self.width = self.widget.width
        #         # self.height = self.widget.height

        #     except AttributeError:
        #         # For pyglet.text.Labels

        #         self.width = self.widget.content_width
        #         self.height = self.widget.content_height

        #     if self.disable:
        #         self.widget.alpha = DISABLE_ALPHA

        if self.container and not self.container.enable:
            self.disable = True

        self.dispatch_event("update")

    def on_key(self, keys, modifiers):
        """The user pressed a key(s) on the keyboard. Note that this event is
        different from on_text, because on_text returns text typed as a string,
        though you can convert a key to a string by using some of the keyboard
        functions.

        When pressing Tab, the focus of the container switches to the next
        widget created. When a widget has focus, you can give it properties
        like if a button has focus, you can press Space to invoke its command.
        If you press Shift-Tab, the focus is moved back by one notch. Focus of
        a widget can be gotten with the focus property, and the on_focus event.

        You can use bit-wise to detect multiple modifiers:

        >>> if modifiers & SHIFT and \
                modifiers & CONTROL and \
                keys == A:
                # Do something

        keys - key pressed by the user. In pyglet, this can be called symbol.
        modifiers - modifiers held down during the key press.

        parameters: int (32-bit), int (32-bit)
        """

    def on_lift(self, keys, modifiers):
        """The user released a key(s) on the keyboard. Note that this event is
        different from on_text, because on_text returns text typed as a string,
        though you can convert a key to a string by using some of the keyboard
        functions.

        When pressing Tab, the focus of the container switches to the next
        widget created. When a widget has focus, you can give it properties
        like if a button has focus, you can press Space to invoke its command.
        If you press Shift-Tab, the focus is moved back by one notch. Focus of
        a widget can be gotten with the focus property, and the on_focus event.

        You can use bit-wise to detect multiple modifiers:

        >>> if modifiers & SHIFT and \
                modifiers & CONTROL and \
                keys == A:
                # Do something

        keys - key released by the user. In pyglet, this can be called symbol.
        modifiers - modifiers held down during the key press.

        parameters: int (32-bit), int (32-bit)
        """

    def on_hover(self, x, y, dx, dy):
        """The widget was hovered over by the mouse. Typically, for widgets,
        something should react to this, for example their background shadow
        becomes more intense, or their color changes. For most widgets their
        image changes or their color does.

        For the coordinates returned for this event, you can see which specific
        widget if it had subwidgets had the hover event. Hover states can be
        accessed with the hover property.

        Do not use this for shapes. Create your own custom check, as this
        accesses GUI widget x and y properties, which not all shapes have.

        x - x position of mouse
        y - y position of mouse
        dx - movement of mouse in vector from last position
        dy - movement of mouse in vector from last position

        parameters: int, int, int, int
        """

    def on_press(self, x, y, buttons, modifiers):
        """The user pressed the widget with the mouse. When this happens, the
        widget gets the focus traversal. This event can be used with buttons,
        labels, and other widgets for cool special effects. This event is not
        called if the mouse is being dragged. This sets the press property to
        True.

        Do not use this for shapes. Create your own custom check, as this
        accesses GUI widget x and y properties, which not all shapes have.

        x - x position of press
        y - y position of press
        buttons - buttons defined in keyboard pressed
        modifiers - modifiers held down during the press

        parameters: int, int, int (32-bit), int (32-bit)
        """

    def on_release(self, x, y, buttons, modifiers):
        """The user released the widget with the mouse. If the widget has an
        on_drag event, that event is canceled. For widgets, their state should
        be set to a hover state. This sets the drag and press properties to
        False.

        Do not use this for shapes. Create your own custom check, as this
        accesses GUI widget x and y properties, which not all shapes have.

        x - x position of release
        y - y position of release
        buttons - buttons defined in keyboard releaseed
        modifiers - modifiers held down during the release

        parameters: int, int, int (32-bit), int (32-bit)
        """

    def on_drag(self, x, y, dx, dy, buttons, modifiers):
        """The user dragged the mouse, of which started over the widget. This
        is most used on text inputs and entries, where the user can select
        text, but can be on sliders and toggles and other widgets. There is no
        built-in way to get the starting position of the mouse, but that can be
        implemented. You could make a variable that gets the coordinates of each
        mouse press, then in the on_drag event, gets the last press coordinates.
        This sets the drag property to True.

        This event is only dispatched if the mouse started on the widget. It is
        not cancelled if the mouse moves outside of the widget, for as long as
        it starts in it, it works. You can get the start point with the
        last_press property.

        Do not use this for shapes. Create your own custom check, as this
        accesses GUI widget x and y properties, which not all shapes have.

        x - x position of mouse during drag
        y - y position of mouse during drag
        dx - movement of mouse in vector from last position
        dy - movement of mouse in vector from last position
        buttons - buttons defined in keyboard during drag
        modifiers - modifiers held down during the during drag

        parameters: int, int, int, int, int (32-bit), int (32-bit)
        """

    def on_scroll(self, x, y, scroll):
        """The user scrolled the mouse on the widget. This should be
        implemented in all widgets that change values, like spinboxes. Widgets
        that only have two values (like toggles) should not use this event, as
        it is impractical.

        Do not use this for shapes. Create your own custom check, as this
        accesses GUI widget x and y properties, which not all shapes have.

        x - x position of mouse during drag
        y - y position of mouse during drag
        scroll - scroll vector (positive being the mouse wheel up, negative the
                 mouse wheel down)

        parameters: int, int, Point
        """

    def on_focus(self, approach):
        """The widget recieves focus from the container. Two widgets cannot
        have focus simultaneously. A focused widget will immediately call all
        other widgets to lose focus. When a widget has focus, you should
        implement events that give it more features. For example, in a spinbox
        widget, if it has focus, the user can press the Up or Down keys to
        increase or decrease the value. The focus property can be accessed.

        This may or may not be used for shapes. It vastly depends if how the
        widget gains focus. If it is pressed, then you may use this for certian
        shapes, but if it focused with Tab, then you may use this for all
        shapes.

        approach - how the widget gains focus. This has two options:
                   KEYBOARD - the user pressed the Tab and/or Shift-Tab key
                              combinations to set focus
                   MOUSE - the user pressed the widget to get focus
                   PROGRAM - the focus property was set by the programmer
                             (not yet implemented).

                   Usually this is the mouse option. Focus traversal via
                   keyboard is unknown to most people.

        parameters: str

        See https://en.wikipedia.org/wiki/Focus_(computing)
        """


Widget.register_event_type("update")

Widget.register_event_type("on_key")
Widget.register_event_type("on_lift")
Widget.register_event_type("on_hover")
Widget.register_event_type("on_press")
Widget.register_event_type("on_release")
Widget.register_event_type("on_drag")
Widget.register_event_type("on_scroll")
Widget.register_event_type("on_focus")

Widget.register_event_type("on_text_select")


class Image(Widget):

    def __init__(self, image, x, y, scale=1, bbox=SIMPLE):
        """Create an Image widget. This is a simple widget used as the main
        component in many other widgets. It is not suitable to create vast
        numbers of these, because you must create a texture every single time.
        Use this for any sort of Image you are going to draw if you want to
        draw it efficiently.

        It's recommended to use a regular, rectangular bounding box for an
        image, unless it must be detailed. You can set the bounding box either
        simple or detailed. Detailed bounding boxes make collision calculations
        much, much, slower. Especially if the bounding box is a polygon with
        hundreds and hundreds of points (e.g. a circle).

        image - filepath of the image
        x - x position of image
        y - y position of image
        scale - scale of image. See arcade.sprite.Sprite for details.
        bbox - bounding box of sprite. See above documentation for details.
               This parameter is not yet used.
        """

        Widget.__init__(self, self, image=image, scale=scale)

        self.image = image

        self.x = x
        self.y = y

        self.normal_image = image
        self.hover_image = load_texture(image)
        self.press_image = load_texture(image)
        self.disable_image = load_texture(image)

        get_container().widget_sprites.append(self)

    def _update_position(self, x, y):
        """Update the position of the widget. This is called internally
        whenever position properties are modified.
        """

        self.center_x = x
        self.center_y = y


class Label(Widget):
    """Label widget to draw and display HTML text.

    FIXME: text changing styles after deleting and then replacing text
           (WORKAROUND)
    """

    UPDATE_RATE = 2

    def __init__(self, text, x, y,
                 colors=[BLACK, (COOL_BLACK, DARK_SLATE_GRAY, DARK_GRAY)],
                 font=DEFAULT_FONT, title=False,
                 justify=LEFT, width=None, multiline=False,
                 command=None, parameters=[],
                 outline=None, location=None,
                 group=None
                ):

        """Create a Label widget to display efficiently and advanced HTML text.
        Note that this uses pyglet's HTML decoder, so formats are limited. See
        the full list of formats at:

        https://pyglet.readthedocs.io/en/latest/programming_guide/text.html

        Text is antialiased to remove artifacts.

        text - text to be displayed on the label
        x - x position of label
        y - y position of label
        colors - colors of the text. This is specified in a format
                 [normal, (hover, press, disable)], which are its states and
                 the appropiate colors displayed. Defaults to
                 [(0, 0, 0), ((0, 46, 99), (47, 79, 79), (169, 169, 169))].
        font - font of the label. This can be a object-oriented font or just a
               tuple containing the font description in (family, size).
               Defaults to DEFAULT_FONT.
        title - the label is drawn as a title. This has long since been
                deprecated.
        justify - horizontal justification of the Label. Its avaliable options
                  are "center", "left", or "right". Defaults to "right".
        width - width of the label. This needs only to be used if the label is
                multiline. Defaults to None, which is replaced by the window
                width.
        multiline - text is drawn multiline. If this is set to true then the
                    width must be set to a value greater than zero, as this
                    will be the length each line for wrap.
        command - command called when the label is pressed
        parameters - parameters of the command. Defaults to [].
        outline - outline of the label as a rectangle. This is specified as
                  (color, padding, width). Defaults to None.

        Because this is object-oriented, nearly all of the values can be
        changed later by changing its properties. The update rate of the label
        defaults to once every sixty frames. This can be modified by setting
        the UPDATE_RATE property. The lower it is set, the higher the update
        rate is. If the update rate is too low (once every frame), then you
        will notice a massive performance drop. You can force the label to set
        text using force_text.

        See https://pyglet.readthedocs.io/en/latest/programming_guide/text.html
        for details regarding text specification and drawing.
        """

        # For new arcade installations, change the self.label property in
        # Text to a HTMLLabel for HTML scripting. (Don't need to do this
        # anymore)
        #
        # self._label = pyglet.text.HTMLLabel(
        #     text=text,
        #     x=start_x,
        #     y=start_y,
        #     width=width,
        #     multiline=multiline
        # )
        #
        # The Label widget is the only widget with a LEFT x anchor.
        #

        if not text:
            text = ""

        if not width:
            width = get_window().width

        if not justify in (LEFT, CENTER, RIGHT):
            raise WidgetsError(f"Invalid label justification \"{justify}\". "
                                "Must be \"left\", \"center\", or \"right\".")

        if multiline and not width:
            raise WidgetsError(f"When the parameter \"multiline\" is set to "
                                "True, the parameter \"width\" must be set to a "
                                "value greater than 0. See the documentation "
                                "for more details. This may be a side effect "
                                "of the window's width being set to zero.")

        self.label = HTMLLabel(f"{text}", location, x, y,
                               anchor_x=LEFT, anchor_y=CENTER,
                               width=width, multiline=multiline,
                               )

        Widget.__init__(self, self.label)

        self.colors = colors
        self.font = font
        self.title = title
        self.justify = justify
        self.multiline = multiline
        self.command = command
        self.parameters = parameters
        self.outline = outline

        self.force_text(text)

        self.bindings = []

        self.length = 0

    def _update_position(self, x, y):
        """Update the position of the widget. This is called internally
        whenever position properties are modified.
        """

        self.label.x = x
        self.label.y = y

    def _get_text(self):
        """Text of the label. It is not recommended to call this repeatedly
        with a high update rate, as this can cause the fps to drop.

        FIXME: text changing styles after deleting and then replacing text
               (COMPLETED)

        See pyglet.text.layout.TextLayout documentation for details.

        type: property, str
        """

        return self.document.text

    def _set_text(self, text):
        if self.frames % self.UPDATE_RATE:
            return

        text = str(text)

        if self.label.text == text:
            return

        if not text:
            text = ""

        self.label.begin_update()

        # self.document.delete_text(0, self.length)
        # self.document.insert_text(0, text)

        # Nasty, but it works as a workaround
        self.label.text = text

        self.label.end_update()

    def _get_document(self):
        """pyglet document of the label. Setting this is far less efficient
        than modifying the current document, as relayout and recalculating
        glyphs is very costly.

        type: property, pyglet.text.document.HTMLDocument
        """

        return self.label.document

    def _set_document(self, document):
        self.label.document = document

    def _get_width(self):
        """Get the content width of the label.

        This property is read-only.

        returns: int
        """

        return self.label.content_width

    def _get_height(self):
        """Get the content height of the label.

        This property is read-only.

        returns: int
        """

        return self.label.content_height

    text = property(_get_text, _set_text)
    document = property(_get_document, _set_document)
    # width = property(_get_width)
    # height = property(_get_height)

    def bind(self, *keys):
        """Bind some keys to the label. Invoking these keys activates the
        label. If the Enter key was binded to the lutton, pressing Enter will
        invoke its command and switches its display to a pressed state.

        >>> label.bind(ENTER, PLUS)
        [65293, 43]

        *keys - keys to be binded

        parameters: *int (32-bit)
        returns: list
        """

        self.bindings = [*keys]
        return self.bindings

    def unbind(self, *keys):
        """Unbind keys from the label.

        >>> label.bind(ENTER, PLUS, KEY_UP, KEY_DOWN)
        [65293, 43, 65362, 65364]
        >>> label.unbind(PLUS, KEY_UP)
        [65293, 65364]

        parameters: *int(32-bit)
        returns: list
        """

        for key in keys:
            self.bindings.remove(key)
        return self.bindings

    def invoke(self):
        """Invoke the label. This switches its text to a pressed state and
        calls the its associated command with the specified parameters. If the
        label is disabled this has no effect.
        """

        if self.disable or not self.command:
            return

        self.press = True

        if self.parameters:
            self.command(self.parameters)
        else:
            self.command()

    def force_text(self, text):
        """Force the label to set the text. This should only be used with
        caution, because if used excessively, will cause a performance drop.
        The update rate is completely ignored.

        text - new text of the label

        parameters: str
        """

        if self.text == text:
            return

        if not text:
            text = ""

        text = str(text)

        self.label.text = text

    def draw_bbox(self, width=1, padding=0):
        """Draw the hitbox of the label. See Widget.bbox for more details.
        This overrides the Widget.bbox because of its left anchor_x.
        """

        draw_rectangle_outline(
            self.x + self.width / 2,
            self.y, self.width + padding,
            self.height + padding, RED, width
        )

    draw_hitbox = draw_bbox
    draw_hit_box = draw_bbox

    def draw(self):
        if self.outline:
            draw_rectangle_outline(
                self.x + self.width / 2, self.y,
                self.width + self.outline[1],
                self.height + self.outline[1],
                self.outline[0], self.outline[2]
            )

        if self.text:
            if not self._left == self.x - self.width / 2 or \
                not self._right == self.x + self.width / 2 or \
                not self._top == self.y + self.height / 2 or \
                not self._bottom == self.y - self.height / 2:
                self._left = self.x - self.width / 2
                self._right = self.x + self.width / 2
                self._top = self.y + self.height / 2
                self._bottom = self.y - self.height / 2

    def on_key(self, keys, modifiers):
        if isinstance(self.bindings, list):
            if keys in self.bindings:
                self.invoke()

        else:
            if self.bindings == keys:
                self.invoke()

    def on_press(self, x, y, buttons, modifiers):
        if self.disable or not self.command:
            return

        if buttons == MOUSE_BUTTON_LEFT:
            self.invoke()

    def update(self):
        """Update the label. This upgrades its properties and registers its
        states and events.

        The following section has been tested dozens of times. The performance
        is incredibly slow, with about 1 fps for 100 Labels. Usually, for a
        single Label the processing time is about one-hundredth of a second.

        With the begin_update() and end_update() functions for the label, the
        processing time is much faster. And with batches, things are more
        efficient and speed is even greater.

        With no other widgets, you can draw 10,000 or more labels before the
        fps drops below 60.

        Multiline labels do not switch color, as it doesn't make sense for a
        paragraph to change color on state change.
        """

        self.length = len(self.text)

        # if "<u" in self.text or "<\\u>" in self.text:
        #     # ValueError: Can only assign sequence of same size
        #     return
        #
        # This was solved in the latest pyglet release

        if not self.multiline:
            # States
            if self.hover:
                self.document.set_style(0, self.length,
                                        {"color" : (four_byte(self.colors[1][1]))})
            if self.press:
                self.document.set_style(0, self.length,
                                        {"color" : four_byte(self.colors[1][1])})
            if self.disable:
                self.document.set_style(0, self.length,
                                        {"color" : four_byte(self.colors[1][2])})

            if self.focus:
                self.document.set_style(0, self.length,
                                        {"color" : four_byte(self.colors[1][0])})

            if not self.hover and \
                not self.press and \
                not self.disable and \
                not self.focus:
                # Wipe the document. Seems nasty, but the getter and setter for
                # properties works with this instance.

                self.text = self.text


class Button(Widget):
    """Button widget to invoke and call commands. Pressing on a button invokes
    its command, which is a function or callable.
    """

    def __init__(
                 self, text, x, y, command=None, parameters=[],
                 link=None, colors=["yellow", DEFAULT_LABEL_COLORS],
                 font=default_font, callback=SINGLE,
                 group=None
                ):

        """Initialize a button. A button has two components: an Image and a
        Label. You can customize the button's images and display by changing
        its normal_image, hover_image, press_image, and disable_image
        properties, but it is recommended to use the Pushable widget.

        THe on_push event is triggered when the button is invoked.

        text - text to be displayed on the button
        x - x position of the button
        y - y position of the button
        command - command to be invoked when the button is called. Defaults
                  to None.
        parameters - parameters of the callable when invoked. Defaults to [].
        link - website link to go to when invoked. Defaults to None.
        colors - colors of the button. Defaults to ("yellow", BLACK).
        font - font of the label. This can be a object-oriented font or just a
               tuple containing the font description in (family, size).
               Defaults to DEFAULT_FONT.
        callback - how the button is invoked:
                   SINGLE - the button is invoked once when pressed
                   DOUBLE - the button can be invoked multiple times in focus
                   MULTIPLE - the button can be invoked continuously

                   Defaults to SINGLE.

        parameters: str, int, int, callable, list, tuple, Font, int
        """

        # A two-component widget:
        #     - Image
        #     - Label

        if not callback in (SINGLE, DOUBLE, MULTIPLE):
            raise WidgetsError("Invalid callback for button. Must be 1, 2, or "
                               "3. Refer to the class documentation for more "
                               "information."
                              )

        self.image = Image(widgets[f"{colors[0]}_button_normal"], x, y)
        self.label = Label(text, x, y, font=font)

        Widget.__init__(self, self.image)

        self.children = [self.image, self.label]

        self.text = text
        self.x = x
        self.y = y
        self.command = command
        self.parameters = parameters
        self.link = link

        self._color = colors[0]
        self.colors = colors

        self.font = font
        self.callback = callback

        self.keys = []
        self.bindings = []

        # Find a way to fit to 80 chars

        self.normal_image = load_texture(widgets[f"{colors[0]}_button_normal"])
        self.hover_image = load_texture(widgets[f"{colors[0]}_button_hover"])
        self.press_image = load_texture(widgets[f"{colors[0]}_button_press"])
        self.disable_image = load_texture(
            widgets[f"{colors[0]}_button_disable"])

        self.window.push_handlers(self.on_key_press)

    def _update_position(self, x, y):
        """Update the position of the widget. This is called internally
        whenever position properties are modified.
        """

        self.label.x = x - self.label.label.content_width / 2
        self.image.x = x

        self.label.y = y
        self.image.y = y

    def _get_text(self):
        """Text of the button. This is the direct text that is displayed on the
        label, not a modified version of it.

        See label text documentation for details.

        type: property, str
        """

        return self.label.text

    def _set_text(self, text):
        self.label.text = text

    def _get_font(self):
        """Font of the text displayed on the button.

        See label font documentation for details.

        type: property, tuple or Font
        """

        return self.label.font

    def _set_font(self, font):
        self.label.font = font

    def _get_colors(self):
        """Colors of the text of the button. Remember that this is a
        multi-demensional list. This is also the color of the button

        See label color documentation for details.

        type: property, list
        """

        return [self._color, self.label.colors]

    def _set_colors(self, colors):
        self._color = colors

        self.label.colors = colors[1]

    text = property(_get_text, _set_text)
    font = property(_get_font, _set_font)
    colors = property(_get_colors, _set_colors)

    def bind(self, *keys):
        """Bind some keys to the button. Invoking these keys activates the
        button. If the Enter key was binded to the button, pressing Enter will
        invoke its command and switches its display to a pressed state.

        Currently, binding modifiers with keys is not supported, though this is
        quite easy to implement by yourself.

        >>> button.bind(ENTER, PLUS)
        [65293, 43]

        *keys - keys to be binded

        parameters: *int (32-bit)
        returns: list
        """

        for key in keys:
            self.bindings.append(key)
        return self.bindings

    def unbind(self, *keys):
        """Unbind keys from the button.

        >>> button.bind(ENTER, PLUS, KEY_UP, KEY_DOWN)
        [65293, 43, 65362, 65364]
        >>> button.unbind(PLUS, KEY_UP)
        [65293, 65364]

        parameters: *int(32-bit)
        returns: list
        """

        for key in keys:
            self.bindings.remove(key)

        return self.bindings

    def invoke(self):
        """Invoke the button. This switches its image to a pressed state and
        calls the its associated command with the specified parameters. If the
        button is disabled this has no effect.

        Dispatches the on_push event.
        """

        if self.disable or not self.command:
            return

        self.press = True

        self.dispatch_event("on_push")

        if self.parameters:
            self.command(self.parameters)
        else:
            self.command()

        if self.link:
            open_new(self.link)

    def draw(self):
        """Draw the button.

        1. Image - background image of the button
        2. Label - text of the button
        """

    def on_press(self, x, y, buttons, modifiers):
        """The button is pressed. This invokes its command if the mouse button
        is the left one.

        TODO: add specifying proper mouse button in settings

        x - x position of the press
        y - y position of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        if buttons == MOUSE_BUTTON_LEFT:
            self.invoke()

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts when the
        button has focus.

        keys - key pressed
        modifiers - modifier pressed

        parameters: int (32-bit), int (32-bit)
        """

        if keys == SPACE:
            self.invoke()

    def on_key_press(self, keys, modifiers):
        """A key is pressed, regardless if the button has focus. Used for
        binding commands to keyboard events.

        keys - key pressed
        modifiers - modifier pressed

        parameters: int, int
        """

        if isinstance(self.bindings, list):
            if keys in self.bindings:
                self.invoke()

        else:
            if self.bindings == keys:
                self.invoke()

    def update(self):
        """Update the button. This registers events and updates the button
        image.
        """

        if self.hover:
            self.image.texture = self.hover_image
        if self.press:
            self.image.texture = self.press_image
        if self.disable:
            self.image.texture = self.disable_image

        if not self.hover and \
            not self.press and \
            not self.disable:
            self.image.texture = self.normal_image

        double = False

        for key in self.keys:
            for binding in self.bindings:
                if key == binding:
                    double = True
                    break
                # else:
                #     continue
            break

        multiple = double # Haha

        if self.callback == DOUBLE and self.focus and double:
            self.invoke()

        if self.callback == MULTIPLE:
            if self.press or multiple:
                self.invoke()

        # .update is not called for the Label, as it is uneccessary for the
        # Label to switch colors on user events.

Button.register_event_type("on_push")


class Slider(Widget):
    """Slider widget to display slidable values.

    FIXME: even knob moves when setting x property
    TODO: add keyboard functionality

    https://github.com/eschan145/Armies/issues/20
    """

    def __init__(self, x, y, colors=DEFAULT_LABEL_COLORS, font=DEFAULT_FONT,
                 default=0, size=100, length=200, padding=50, round=None,
                 group=None
                ):

        """Initialize a slider.

        x - x position of slider
        y - y position of slider
        colors - colors of the label. See label colors for details.
        font - font of the label. This can be a object-oriented font or just a
               tuple containing the font description in (family, size).
               Defaults to DEFAULT_FONT.
        default - default value of the slider. Defaults to 0.
        size - number of values that can be on the slider. The knob will
               automatically snap to these values and their designated x
               positions.
        length - direct width/length of the slider.
        padding - spacing between the label and the slider
        round - rounds the label display to a decimal value

        parameters: int, int, tuple, Font, int, int, int, int, int
        """

        self.bar = Image(slider_horizontal, x, y)
        self.knob = Image(knob, x, y)
        self.label = Label(default, x, y, font=font)

        Widget.__init__(self, self.bar)

        self.children = [self.bar, self.knob, self.label]

        self.colors = colors
        self.font = font
        self.size = size
        self.length = length
        self.padding = padding
        self.round = round

        self.value = default

        self.x = x
        self.y = y

        self.value = 0
        self.destination = 0

    def _update_position(self, x, y):
        """Update the position of the widget. This is called internally
        whenever position properties are modified.
        """

        self.bar.x = x
        self.knob.left = x - self.length / 2
        self.label.x = self.bar.left - self.padding

        self.bar.y = y
        self.knob.y = y
        self.label.y = y

    def _get_value(self):
        """Value or x of the slider. Setting this updates and snaps it to the
        position relative to the given value.

        type: property, float
        """

        return self._value

    def _set_value(self, value):
        if self._value >= self.size:
            self._value = self.size
            return

        elif self._value <= 0:
            self._value = 0
            return

        max_knob_x = self.right # + self.knob.width / 2

        self._value = round(value, self.round)

        x = (max_knob_x - self.left) * value / self.size \
            + self.left + self.knob.width / 2
        self.knob.x = max(self.left, min(x - self.knob.width / 2, max_knob_x))

    def _get_text(self):
        """Text of the slider. This is the direct text that is displayed on the
        label, not a modified version of it.

        See label text documentation for details.

        type: property, str
        """

        return self.label.text

    def _set_text(self, text):
        self.label.text = text

    def _get_font(self):
        """Font of the text displayed on the slider.

        See label font documentation for details.

        type: property, tuple or Font
        """

        return self.label.font

    def _set_font(self, font):
        self.label.font = font

    def _get_colors(self):
        """Colors of the text of the slider. Remember that this is a
        multi-demensional list.

        See label color documentation for details.

        type: property, list
        """

        return self.label.colors

    def _set_colors(self, colors):
        self.label.colors = colors

    value = property(_get_value, _set_value)
    text = property(_get_text, _set_text)
    font = property(_get_font, _set_font)
    colors = property(_get_colors, _set_colors)

    def update_knob(self, x):
        """Update the knob and give it a velocity when moving. When calling
        this, the knob's position will automatically update so it is congruent
        with its size.

        Dispatches the on_slide_start event.

        NOTE: this does not move the knob

        x - x position of the position

        parameters: int
        """

        self.destination = max(self.left, min(x, self.right))
        self._value = round(abs(((self.knob.x - self.left) * self.size)
                                / (self.left - self.right)), self.round)

        self.text = round(self.value, self.round)

        self.dispatch_event("on_slide_start", self._value)

    def reposition_knob(self):
        """Update the value of the slider. This is used when you want to move
        the knob without it snapping to a certain position and want to update
        its value. update_knob(x) sets a velocity so the knob can glide.

        Dispatches the on_slide_motion event.
        """

        try:
            self._value = round(abs(((self.knob.x - self.left) * self.size) \
                          / (self.left - (self.right - self.knob.width))),
                          self.round)

            self.dispatch_event("on_slide_motion")

        except ZeroDivisionError: # Knob hasn't even moved
            return

        self.text = round(self.value, self.round)

    def draw(self):
        """Draw the slider. The component of the slider is the bar, which takes
        all of the collision points.

        1. Bar (component)
        2. Knob
        3. Label
        """

        # Force setting width

        self.bar._width = self.length

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts when the slider
        has focus. On a right key press, the value is incremented by one. On a
        left key press, the value is decremented by one.

        Unfortunately, this is not working currently.

        keys - key pressed
        modifiers - modifier pressed

        parameters: int (32-bit), int (32-bit)
        """

        if not self.focus:
            return

        if keys == KEY_RIGHT:
            self.value -= 1
            # self.reposition_knob()
        elif keys == KEY_LEFT:
            self.value += 1
            # self.reposition_knob()

    def on_press(self, x, y, buttons, modifiers):
        """The slider is pressed. This updates the knob to the x position of the
        press.

        x - x position of the press
        y - y position of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        self.update_knob(x)

    def on_drag(self, x, y, dx, dy, buttons, modifiers):
        """The user dragged the mouse when it was pressed. This updates the knob
        to the x position of the press.

        x - x position of the press
        y - y position of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        self.update_knob(x)

    def on_scroll(self, x, y, mouse):
        """The user scrolled the mouse wheel. This will change the knob's
        position and adjust its x position.

        x - x position of the mouse scroll
        y - y position of the mouse scroll
        mouse - movement in vector from the last position (x, y)
        direction - direction of mouse scroll

        parameters: int, int, tuple (x, y), float
        """

        self.value += mouse.y

    def update(self):
        """Update the knob. This adjusts its position and adds effects like
        gliding when the knob is moving. This way, the knob doesn't just snap to
        position. When the knob is hovered, its scale is increased by
        KNOB_HOVER_SCALE.

        Dispatches the on_slide_finish event.
        """

        if self.destination:
            if self.knob.x <= self.destination and \
               self.knob.right <= self.right:
                # Knob too left, moving to the right
                self.knob.x += SLIDER_VELOCITY
                self.reposition_knob()

            else:
                self.dispatch_event("on_slide_finish", RIGHT)

            if self.knob.right > self.destination and \
               self.knob.left >= self.left:
                # Knob too right, moving to the left
                self.knob.x -= SLIDER_VELOCITY
                self.reposition_knob()

            else:
                self.dispatch_event("on_slide_finish", LEFT)

        # Knob hover effect
        if self.knob.hover:
            self.knob.scale = KNOB_HOVER_SCALE
        else:
            self.knob.scale = 0.9

    def on_slide_start(self, value):
        """The knob of the slider has started motion. This means that the
        velocity is set, and the knob just needs to finish its journey.

        value - value for the knob to snap to

        parameters: int
        """

    def on_slider_motion(self):
        """The knob of the slider is in motion. It is in its journey to reach
        the other slide of the bar.
        """

    def on_slide_finish(self, value):
        """The knob of the slider has finished its journey, therefore changing
        the value.

        value - new value that the knob has moved to

        parameters: int
        """

Slider.register_event_type("on_slide_start")
Slider.register_event_type("on_slide_motion")
Slider.register_event_type("on_slide_finish")


class Toggle(Widget):
    """Toggle widget to switch between true and false values. This uses
    a special effect of fading during the switch.

    FIXME: even knob moves when setting x property
    """

    true_image = load_texture(toggle_true)
    false_image = load_texture(toggle_false)
    hover_true_image = load_texture(toggle_true_hover)
    hover_false_image = load_texture(toggle_false_hover)

    on_left = True
    on_right = False
    value = None
    switch = False

    def __init__(
                 self, text, x, y,
                 colors=DEFAULT_LABEL_COLORS, font=DEFAULT_FONT,
                 default=True, padding=160,
                 callback=SINGLE
                ):

        """Initialize a toggle. A toggle is a widget that when pressed, switches
        between True and False values.

        TODO: fix knob image (scaling)

        text - text to be displayed alongside the toggle
        x - x position of the toggle
        y - y position of the toggle
        colors - text color of the Label
        font - font of the Label
        default - default value of the toggle
        padding - padding of the Label and the toggle
        callback - how the toggle is invoked:
                   SINGLE - toggle is invoked once when pressed
                   MULTIPLE - toggle can be invoked continuously

                   Defaults to SINGLE.

        parameters: str, int, int, tuple, tuple, bool, int
        """

        # A three-component widget:
        #     - Image
        #     - Image
        #     - Label

        if default:
            image = toggle_true
        else:
            image = toggle_false

        if not callback in (SINGLE, DOUBLE, MULTIPLE):
            raise WidgetsError("Invalid callback for toggle. Must be 1, 2, or "
                               "3. Refer to the class documentation for more "
                               "information."
                              )

        self.bar = Image(image, x, y)
        self.knob = Image(knob, x, y)

        self.label = Label(knob, x, y, font=font)

        Widget.__init__(self, self.bar)

        self.children = [self.bar, self.knob, self.label]

        self.text = text
        self.colors = colors
        self.font = font
        self.padding = padding
        self.callback = callback

        self.x = x
        self.y = y

        self.knob.left = self.bar.left

    def _update_position(self, x, y):
        """Update the position of the widget. This is called internally
        whenever position properties are modified.
        """

        self.bar.x = x
        self.bar.y = self.knob.y = self.label.y = y

        self.label.x = self.bar.left - self.padding

    def _get_text(self):
        """Text of the toggle. This is the direct text that is displayed on the
        label, not a modified version of it.

        See label text documentation for details.

        type: property, str
        """

        return self.label.text

    def _set_text(self, text):
        self.label.text = text

    def _get_font(self):
        """Font of the text displayed on the toggle.

        See label font documentation for details.

        type: property, tuple or Font
        """

        return self.label.font

    def _set_font(self, font):
        self.label.font = font

    def _get_colors(self):
        """Colors of the text of the toggle. Remember that this is a
        multi-demensional list.

        See label color documentation for details.

        type: property, list
        """

        return self.label.colors

    def _set_colors(self, colors):
        self.label.colors = colors

    text = property(_get_text, _set_text)
    font = property(_get_font, _set_font)
    colors = property(_get_colors, _set_colors)

    def draw(self):
        """Draw the toggle. The component of the toggle is the bar, which takes
        all of the collision points.

        1. Bar (component)
        2. Knob
        3. Label
        """

    def on_press(self, x, y, buttons, modifiers):
        """The toggle is pressed. This switches between True and False values. If
        the Control key is held down during this, this will have no effect.

        x - x position of the press
        y - y position of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        if not modifiers & CONTROL:
            self.switch = True

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts when the toggle
        has focus. If the Space or Enter key is pressed, the toggle will be
        switched.

        keys - key pressed
        modifiers - modifier pressed

        parameters: int (32-bit), int (32-bit)
        """

        if keys == SPACE or keys == ENTER:
            self.switch = True

    def update(self):
        """Update the toggle. This updates its position and registers its
        special effects.

        Dispatches the on_toggle event when the toggle has finished moving.
        """

        if self.on_left:
            self.value = True
        else:
            self.value = False

        if self.callback == MULTIPLE:
            if self.keys[SPACE]:
                self.switch = True

        if self.switch and not self.disable:
            if self.on_left:
                # Knob on the left, moving towards the right
                if self.knob.right < self.bar.right - 3:
                    self.knob.x += TOGGLE_VELOCITY
                else:
                    self.on_right = True
                    self.on_left = False

                    self.switch = False

                    self.dispatch_event("on_toggle", False)

                if self.knob.x < self.x:
                    try: self.bar.alpha -= TOGGLE_FADE
                    except ValueError: pass
                elif self.knob.x > self.x: # More than halfway
                    try: self.bar.alpha += TOGGLE_FADE
                    except ValueError: pass

                    self.bar.texture = self.false_image
                    if self.hover: self.bar.texture = self.hover_false_image

            elif self.on_right:
                # Knob on the right, moving towards the left
                if self.knob.left > self.bar.left + 2:
                    self.knob.x -= TOGGLE_VELOCITY
                else:
                    self.on_left = True
                    self.on_right = False

                    self.switch = False

                    self.dispatch_event("on_toggle", True)

                if self.knob.x > self.x:
                    try: self.bar.alpha -= TOGGLE_FADE
                    except ValueError: pass
                elif self.knob.x < self.x:
                    try: self.bar.alpha += TOGGLE_FADE
                    except ValueError: pass

                    self.bar.texture = self.hover_true_image
                    if self.hover: self.bar.texture = self.hover_true_image

        else:
            if self.hover:
                if self.value: self.bar.texture = self.hover_true_image
                else: self.bar.texture = self.hover_false_image
            else:
                if self.value: self.bar.texture = self.true_image
                else: self.bar.texture = self.false_image

        if self.disable:
            if self.value: self.bar.texture = self.true_image
            else: self.bar.texture = self.false_image

        if self.knob.hover:
            self.knob.scale = KNOB_HOVER_SCALE
        else:
            self.knob.scale = 0.9

    def on_toggle(self, value):
        """The toggle has been completed. This means that the knob has moved
        from one side of the bar to the other.

        value - boolean of the toggle's value

        parameters: bool
        """

Toggle.register_event_type("on_toggle")


_Caret = Caret

class Caret(_Caret):
    """Caret used for pyglet.text.IncrementalTextLayout."""

    BLINK_INTERVAL = 0.5

    def __init__(self, layout):
        """Initalize a caret designed for interactive editing and scrolling of
        large documents and/or text.
        """

        _Caret.__init__(self, layout)

    def on_text_motion(self, motion, select=False):
        """The caret was moved or a selection was made with the keyboard.

        motion - motion the user invoked. These are found in the keyboard.
                 MOTION_LEFT                MOTION_RIGHT
                 MOTION_UP                  MOTION_DOWN
                 MOTION_NEXT_WORD           MOTION_PREVIOUS_WORD
                 MOTION_BEGINNING_OF_LINE   MOTION_END_OF_LINE
                 MOTION_NEXT_PAGE           MOTION_PREVIOUS_PAGE
                 MOTION_BEGINNING_OF_FILE   MOTION_END_OF_FILE
                 MOTION_BACKSPACE           MOTION_DELETE
                 MOTION_COPY                MOTION_PASTE
        select - a selection was made simultaneously

        parameters: int (32-bit), bool
        returns: event
        """

        if motion == MOTION_BACKSPACE:
            if self.mark is not None:
                self._delete_selection()
            elif self._position > 0:
                self._position -= 1
                self._layout.document.delete_text(self._position, self._position + 1)
                self._update()
        elif motion == MOTION_DELETE:
            if self.mark is not None:
                self._delete_selection()
            elif self._position < len(self._layout.document.text):
                self._layout.document.delete_text(self._position, self._position + 1)
        elif self._mark is not None and not select and \
            motion is not MOTION_COPY:
            self._mark = None
            self._layout.set_selection(0, 0)

        if motion == MOTION_LEFT:
            self.position = max(0, self.position - 1)
        elif motion == MOTION_RIGHT:
            self.position = min(len(self._layout.document.text), self.position + 1)
        elif motion == MOTION_UP:
            self.line = max(0, self.line - 1)
        elif motion == MOTION_DOWN:
            line = self.line
            if line < self._layout.get_line_count() - 1:
                self.line = line + 1
        elif motion == MOTION_BEGINNING_OF_LINE:
            self.position = self._layout.get_position_from_line(self.line)
        elif motion == MOTION_END_OF_LINE:
            line = self.line
            if line < self._layout.get_line_count() - 1:
                self._position = self._layout.get_position_from_line(line + 1) - 1
                self._update(line)
            else:
                self.position = len(self._layout.document.text)
        elif motion == MOTION_BEGINNING_OF_FILE:
            self.position = 0
        elif motion == MOTION_END_OF_FILE:
            self.position = len(self._layout.document.text)
        elif motion == MOTION_NEXT_WORD:
            pos = self._position + 1
            m = self._next_word_re.search(self._layout.document.text, pos)
            if not m:
                self.position = len(self._layout.document.text)
            else:
                self.position = m.start()
        elif motion == MOTION_PREVIOUS_WORD:
            pos = self._position
            m = self._previous_word_re.search(self._layout.document.text, 0, pos)
            if not m:
                self.position = 0
            else:
                self.position = m.start()

        self._next_attributes.clear()
        self._nudge()

    def _update(self, line=None, update_ideal_x=True):
        """Update the caret. This is used internally for the entry widget.

        line - current line of the caret
        update_ideal_x - x position of line is updated

        parameters: int, bool
        """

        if line is None:
            line = self._layout.get_line_from_position(self._position)
            self._ideal_line = None
        else:
            self._ideal_line = line
        x, y = self._layout.get_point_from_position(self._position, line)
        if update_ideal_x:
            self._ideal_x = x

        # x -= self._layout.view_x
        # y -= self._layout.view_y
        # add 1px offset to make caret visible on line start
        x += self._layout.x + 1

        y += self._layout.y + self._layout.height / 2 + 2

        font = self._layout.document.get_font(max(0, self._position - 1))
        self._list.position[:] = [x, y + font.descent, x, y + font.ascent]

        if self._mark is not None:
            self._layout.set_selection(min(self._position, self._mark), max(self._position, self._mark))

        self._layout.ensure_line_visible(line)
        self._layout.ensure_x_visible(x)


class Entry(Widget):
    """Entry widget to display user-editable text. This makes use of the
    pyglet.text.layout.IncrementalTextLayout and a modified version of its
    built-in caret.

    Rich text formatting is currently in progress.

    FIXME: caret not showing on line start (pyglet error)
           use of a lot of GPU when selected text is formatted (may be pyglet)
           make caret transparent or invisible instead of changing color (COMPLETED)
           caret glitching out on blinks at line end (pyglet error)
           entry taking up much CPU

    TODO
    1. Add rich text formatting (use pyglet.text.document.HTMLDocument)
    2. Add show feature for passwords
    3. Add copy, paste, select all, and more text features (COMPLETED)
    4. Add undo and redo features
    5. Enable updates for the layout for smoother performance. This raises
       AssertionError, one that has been seen before.
    6. Finish up scrolling of history. This is incomplete, and if text is
       added before the history's index, then the index is not changed.

    https://github.com/eschan145/futura/issues/1#issue-1393607169
    """

    # Simple validations
    VALIDATION_LOWERCASE = compile("^[a-z0-9_\-]+$")
    VALIDATION_UPPERCASE = compile("^[A-Z]*$")
    VALIDATION_LETTERS = compile("[A-Z]")
    VALIDATION_DIGITS = compile("[1-9]")

    # From https://www.computerhope.com/jargon/r/regex.htm
    VALIDATION_EMAIL = compile("/[\w._%+-]+@[\w.-]+\.[a-zA-Z]{2,4}")


    # Most advanced validation, with non-signed zero believers
    VALIDATION_ADVANCED_DIGITS = compile("^((?!-0?(\.0+)?(e|$))-?(0|[1-9]\d*)?"
                                         "(\.\d+)?(?<=\d)(e-?(0|[1-9]\d*))?|0x"
                                         "[0-9a-f]+)$"
                                        )
    VALIDATION_REGULAR = None

    _history_index = 0

    _validate = VALIDATION_LETTERS
    _document = None
    _placeholder = None

    normal_image = load_texture(entry_normal)
    hover_image = load_texture(entry_hover)
    focus_image = load_texture(entry_focus)

    def __init__(self, x, y, text="", font=default_font, color=BLACK,
                 history=True):

        """Initialize the entry. Typically a widget will push events
        automatically, but because there are custom named events, they have
        to be defined here.

        An entry is a widget where text input can be returned. Typing into
        an entry appends some text, which can be used for usernames,
        passwords, and more. Text can be removed by many keys.

        The on_text_edit event is triggered when text in the entry is modified.
        The on_text_interact event is triggered when text is interacted with,
        like selecting, moving the caret, or other events that are associated
        with the caret and not text modification.

        x - x position of the entry
        y - y position of the entry
        text - default text of the entry
        font - font of the text in the entry
        color - color of the text in RGB as a tuple of three ints

        history - the user can press Alt Left or Alt Right to go back and forth
                  between history. History can be marked when the user presses
                  the entry and the position of the caret is changed.

        properties:
            document - document of the pyglet.text.layout.IncrementalTextLayout
            layout - internal pyglet.text.layout.IncrementalTextLayout for
                     efficient rendering
            caret - caret of the entry
            image - image displayed to give the entry a graphical look

            x - x position of the entry
            y - y position of the entry
            default - default text of the entry (changing this has no effect)
            font - font of the entry

            blinking - caret is visible or not visible

            length - length of the text in the entry
            max - maximum amount of characters in the entry

            text - displayed text of the entry
            selection - selected text of the entry
            layout_colors - layout colors of the entry
            validate - validation of the characters in the entry
            index - index of the caret (position)
            view - view vector of the entry

        methods:
            blink - blink the caret and switch its visibility
            insert - insert some text in the entry
            delete - delete some text from the entry
        """

        self._document = decode_attributed(text)

        self.layout = IncrementalTextLayout(self._document, 190, 24,
                                            batch=get_container().batch
                                           )

        self.image = Image(entry_normal, x, y)
        self.caret = Caret(self.layout)

        Widget.__init__(self, self.image)

        self.children = [self.image]

        self.x = x
        self.y = y
        self.font = font
        self.default = text
        self.colors = BLACK

        self.layout.anchor_x = LEFT
        self.layout.anchor_y = CENTER

        self._history_enabled = history

        self._document.set_style(0, len(text), dict(font_name=DEFAULT_FONT[0],
                                                    font_size=DEFAULT_FONT[1],
                                                    color=four_byte(color)))

        self.window.push_handlers(
            self.on_text,
            self.on_text_motion
        )

    def _update_position(self, x, y):
        """Update the position of the widget. This is called internally
        whenever position properties are modified.
        """

        self.layout.x = x - self.layout.width / 2
        self.image.x = x

        self.layout.y = y - 5
        self.image.y = y

    def _get_document(self):
        """pyglet document of the entry. This is far less efficient than
        modifying the current document, as relayout and recalculating glyphs
        is very costly.

        type: property, pyglet.text.document.FormattedDocument
        """

        return self.layout.document

    def _set_document(self, document):
        self.layout.document = document

    def _get_text(self):
        """Text of the entry. This should technically become a method, and the
        "parameter" change_index is set to True. This cannot be configured,
        only by subclassing this class.

        Dispatches the on_text_edit event if the text is different.

        text - new text to be displayed. This can be a string or a tuple
        change_index - index is changed after text input. If True, the index
                       is set to the end of the entry.

        type: property, str
        """

        return self.document.text

    def _set_text(self, text):
        before = self.text

        text = text or ""

        if isinstance(text, Tuple):
            self.document._delete_text(0, self.max)
            self.document._insert_text(0, text[0], None)

            self.dispatch_event("on_text_edit", before, text)

            # self.document.text = text

            if text[1]:
                # Put the caret to the end
                self.index = self.max

            return

        self.document._delete_text(0, self.max)
        self.document._insert_text(0, text, None)

        self.dispatch_event("on_text_edit", before, text)

        # self.document.text = text

    def _get_index(self):
        """Index of the current caret position within the document. If the
        index exceeds the document length, the end of the document will be
        used instead.

        Dispatches the on_text_interact event if the index is different.

        type: property, int
        """

        return self.caret.position

    def _set_index(self, index):
        if self.caret.position == index:
            return

        self.caret.position = index

        self.dispatch_event("on_text_interact", index, None)

    def _get_mark(self):
        """Mark of the caret within the document.

        An interactive text selection is determined by its immovable end (the
        caret's position when a mouse drag begins) and the caret's position,
        which moves interactively by mouse and keyboard input.

        This property is None when there is no selection. It should not be set
        to zero, because that would just set the selection start index in the
        first position.

        Dispatches the on_text_interact event if the mark is different.

        type: property, int
        """

        return self.caret.mark

    def _set_mark(self, mark):
        if self.caret.mark == mark:
            return

        self.caret.mark = mark

        selection = None

        if self.selection[2]:
            selection = self.selection[2]

        self.dispatch_event("on_text_interact",
                            self.index,
                            selection
                            )

    def _get_selection(self):
        """Selection indices of the entry, which are defined with the property
        layout_colors. This is in the format (start, end).

        Dispatches the on_text_interact event when the selection is different.

        type: property, tuple (int, int)
        """

        # Pretty neat, but kind of long

        return (
                self.layout.selection_start,
                self.layout.selection_end,
                self.text[
                    self.layout.selection_start : self.layout.selection_end
                ]
               )

    def _set_selection(self, selection):
        self.mark = selection[1]

        self.layout.selection_start = selection[0]
        self.layout.selection_end = selection[1]

        if selection is not self.selection:
            self.dispatch_event("on_text_interact", self.index, selection)

    def _get_layout_colors(self):
        """pyglet layout-specific colors of the entry. This is a tuple of three
        colors, defined here. Defaults are listed beside.

        1. Background color of the selection (46, 106, 197)
        2. Caret color (0, 0, 0)
        3. Text color of the selection (0, 0, 0)

        (selection, caret, text)

        type: property, list (tuple, tuple, tuple)
        """

        return (
                self.layout.selection_background_color,
                self.caret.color,
                self.layout.selection_color
                )

    def _set_layout_colors(self, colors):
        self.layout.selection_background_color = colors[0]
        self.layout.selection_color = colors[2]

        self.caret.color = colors[1]

    def _get_validate(self):
        """Validation of the entry. This is a string containing all of the
        characters the user is able to type. Common charsets cam be found in
        the string module. Several validations are already provided:

        VALIDATION_LOWERCASE        VALIDATION_ADVANCED_DIGITS
        VALIDATION_UPPERCASE        VALIDATION_PUNCTUATION
        VALIDATION_LETTERS          VALIDATION_WHITESPACE
        VALIDATION_DIGITS           VALIDATION_REGULAR

        Using regex for real numerical inputs, password inputs, and other
        various types is currently in-progress, with many bugs and possible
        errors.

        TODO: replace string validation with regex (IN PROGRESS)

        type: property, str
        """

        return self._validate

    def _set_validate(self, validate):
        self._validate = validate

    def _get_placeholder(self):
        """Placeholder text of the entry. This is just "default" text, which is
        removed when the entry gains focus. When the entry loses focus, the
        placeholder text is displayed again. This can be used for instructions.

        type: property, str
        """

        return self._placeholder

    def _set_placeholder(self, placeholder):
        self._placeholder = placeholder

    def _get_view(self):
        """Get the view vector as a Point of the entry.

        type: property, tuple (x, y)
        """

        return (
                self.layout.view_x,
                self.layout.view_y
        )

    def _set_view(self, view):
        self.layout.view_x = view.x
        self.layout.view_y = view.y

    text = property(_get_text, _set_text)
    document = property(_get_document, _set_document)
    index = property(_get_index, _set_index)
    mark = property(_get_mark, _set_mark)
    selection = property(_get_selection, _set_selection)
    layout_colors = property(_get_layout_colors, _set_layout_colors)
    validate = property(_get_validate, _set_validate)
    placeholder = property(_get_placeholder, _set_placeholder)
    view = property(_get_view, _set_view)

    def blink(self, delta):
        """The caret toggles between white and black colors. This is called
        every 0.5 seconds, and only when the caret has focus.

        delta - delta time in seconds since the function was last called.
                This varies about 0.5 seconds give or take, because of
                calling delay, lags, and other inefficiencies.

        parameters: float
        """

        if not self.caret._list.colors[3] or \
            not self.caret._list.colors[7]:
            alpha = 255
        else:
            alpha = 0

        self.caret._list.colors[3] = alpha
        self.caret._list.colors[7] = alpha

    def insert(self, index, text, change_index=True):
        """Insert some text at a given index one character after the index.

        >>> entry.text = "Hello!"
        >>> entry.insert(6, " world")
        >>> entry.text
        "Hello world!"

        "Hello world!"
              ^^^^^^
              678...

        Dispatches the on_text_edit event if text is deleted.

        index - index of the text addition
        text - text to be added
        change_index - index is updated to the end of the addition. This value
                       usually just needs to be left where it is. Defaults to
                       True.

        parameters: int, str, bool
        """

        # self.text = insert(index, self.text, text)

        before = self.text

        self.document._insert_text(index, text, None)

        if not before == self.text:
            self.dispatch_event("on_text_edit", text, before)

        if change_index:
            self.index = self.index + len(text)

    def delete(self, start, end):
        """Delete some text at a start and end index, one character after the
        start position and a character after the end position.

        >>> entry.text = "Hello world!"
        >>> entry.delete(5, 10)
        >>> entry.text
        "Hello!"

        "Hello world!"
              ^^^^^^
              6... 11

        Dispatches the on_text_edit event if text is deleted.

        start - start of the text to be deleted
        end - end of the text to be deleted

        parameters: int, int
        """

        # self.text = delete(start, end, self.text)

        before = self.text

        self.document._delete_text(start, end)

        if not before == self.text:
            self.dispatch_event("on_text_edit", self.text[start : end], before)

        self.mark = None

    def clear(self, text=False, mark=0, index=0):
        """Clear the text in the entry and remove all of its caret properties.
        This is just a shortcut for setting the index, text, and mark to None.

        text - clear the text in the entry
        mark - reset the mark in the entry
        index - move the index of the caret to the first position

        parameters: bool or str, int, int
        """

        self.text = text or None
        self.mark = mark
        self.index = index

    # Text formatting functions

    def set_format(self, *args, **kwargs):
        selection = self.selection[0], self.selection[1]

        if self.mark: # Has mark (selection)
            if "bold" in kwargs:
                self.format_insert(*selection, bold=True)
            if "italic" in kwargs:
                # if "italic" in self.document.get_style_runs("italic"):z
                self.format_insert(*selection, italic=True)
        # else:
        #     for key in kwargs:
        #         setattr(self, f"self.edit_{key}")

    def format_insert(self, *args, **kwargs):
        """Insert a formatted range to a range of indices in the entry. Formats
        are specified in **kwargs. Keep in mind that this is pyglet document
        formatting, not the custom formatting that has been provided by this
        module.

        >>> entry.format_insert(5, 10, bold=True, color=(255, 0, 0, 255))

        Overlapping formats are supported, so you can call this over the same
        range of text. This fixes the problem in tkinter, where overlapping
        tags are not supported.

        Dictionary from arguments credit to:
        https://stackoverflow.com/a/44412830/19573533

        indices - a tuple of the start and end indices of the range. Defaults
                  to None, which is the whole range of the text.

        parameters: tuple (start, end)
        """

        indices = args or (0, self.length)

        formats = {("arg" + str(index + 1)): argument for index, argument in enumerate(args)}
        formats.update(kwargs)

        del formats["arg1"]
        del formats["arg2"]

        self.document.set_style(*indices, formats)

    def format_replace(self, indices=None, **kwargs):
        """Replace a formatted range to new formatted text given indices. This
        has no effect if there are no styles over the range. Formats are
        specified in **kwargs. Keep in mind that this is pyglet document
        formatting, not the custom formatting that has been provided by this
        toolkit.

        indices - a tuple of the start and end indices of the range. Defaults
                  to None, which is the whole range of the text.

        parameters: tuple (start, end)
        """

        indices = indices or (0, self.length)

        self.document.set_style(*indices, {})
        self.document.set_style(*indices, dict(kwargs))

    def draw(self):
        """Draw the entry. The layout is drawn with pyglet rendering.

        1. Image component
        2. Layout

        FIXME: there is a bug here. The anchor_x and anchor_y properties of the
               layout have to be set again and again. This makes performance
               deadly slow.
        """

        self.layout.begin_update()

        self.layout.anchor_x = LEFT

        self._document.set_style(0, len(self.text), dict(font_name=DEFAULT_FONT[0],
                                                    font_size=DEFAULT_FONT[1],
                                                    color=four_byte(self.colors)))
        self.layout.anchor_y = CENTER

        self.layout.end_update()

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts.

        Control + A     Select all of the text
        Control + V     Paste the clipboard's latest text
        Control + C     Copy the selected text and add it to the clipboard
        Control + X     Cut the selected text and add it to the clipboard. This
                        is essentially copying and deleting text, useful for
                        moving incorrectly placed text.

        If history is enabled, the user can hold Alt and press Left and Right
        to scroll back history.

        keys - key pressed
        modifiers - modifier pressed

        parameters: int (32-bit), int (32-bit)
        """

        if keys == SPACE:
            self.undo_stack.append(self.text)

        if modifiers & CONTROL:
            if keys == V:
                self.insert(self.index, clipboard_get(), change_index=True)
            elif keys == C:
                clipboard_append(self.selection[2])
            if keys == X:
                clipboard_append(self.selection[2])
                self.delete(self.selection[0], self.selection[1])
            elif keys == A:
                self.index = 0
                self.selection = (0, self.length, self.text)

            if keys == B:
                self.set_format(bold=True)
            if keys == I:
                self.set_format(italic=True)

        if modifiers & ALT and self._history_enabled:
            # This code is a little messy...

            if keys == KEY_LEFT:
                try:
                    self._history_index -= 1
                    self.index = self.history[self._history_index]

                except IndexError:
                    # Get the first item in the history
                    index = 0

                    self._history_index = index
                    self.index = self.history[index]

            if keys == KEY_RIGHT:
                try:
                    self._history_index += 1
                    self.index = self.history[self._history_index]

                except IndexError:
                    # Get the last item in the history
                    index = len(self.history) - 2 # Compensate for added index

                    self._history_index = index
                    self.index = self.history[index]

    def on_focus(self, approach):
        """The entry has focus, activating events. This activates the caret
        and stops a few errors.
        """

        if self.text == self.default:
            self.clear()

    def on_text(self, text):
        """The entry has text input. The entry adds text to the end.
        Internally, the entry does a few things:
            - Remove all selected text
            - Update the caret position
            - Appends text to the end of the layout

        Dispatches the on_text_edit event.

        text - text inputed by the user

        parameters: str
        """

        if self.text_options["title_case"]:
            if not self.text:
                text = text.capitalize()

        if self.focus and \
            self.length < self.max:
            if self.validate:
                before = self.text
                self.caret.on_text(text)
                after = self.text

                if before is not after:
                    self.dispatch_event("on_text_edit", text, before)

                if not self.validate.match(after):
                    self.text = before

                return

            before = self.text
            self.caret.on_text(text)
            after = self.text

            if before is not after:
                self.dispatch_event("on_text_edit", text, before)

    def on_text_motion(self, motion):
        """The entry has caret motion. This can be moving the caret's
        position to the left with the Left key, deleting a character
        previous with the Backspace key, and more.

        This filters out Alt key and the Left or Right key is being pressed,
        as this is used for history.

        Dispatches the on_text_edit or the on_text_interact event, depending on
        if text is selected or deleted.

        motion - motion used by the user. This can be one of many motions,
                 defined by keyboard constants found in the keyboard module.

                 MOTION_LEFT                MOTION_RIGHT
                 MOTION_UP                  MOTION_DOWN
                 MOTION_NEXT_WORD           MOTION_PREVIOUS_WORD
                 MOTION_BEGINNING_OF_LINE   MOTION_END_OF_LINE
                 MOTION_NEXT_PAGE           MOTION_PREVIOUS_PAGE
                 MOTION_BEGINNING_OF_FILE   MOTION_END_OF_FILE
                 MOTION_BACKSPACE           MOTION_DELETE
                 MOTION_COPY                MOTION_PASTE

                 You can get the list of all text motions with motions_string()
                 in the keyboard module. You can also get their keyboard
                 combinations with motions_combinations().

        parameters: int (32-bit)
        """

        if not self.focus:
            return

        if self.keys[ALT]:
            if motion == MOTION_LEFT or motion == MOTION_RIGHT:
                return

        before = self.text
        self.caret.on_text_motion(motion)

        selection = None

        if self.selection[2]:
            selection = self.selection[:2]

        if motion == MOTION_BACKSPACE or motion == MOTION_DELETE:
            self.dispatch_event("on_text_edit", "", before)

            return

        self.dispatch_event("on_text_interact", self.index, selection)

    def on_text_select(self, motion):
        """Some text in the entry is selected. When this happens, the
        selected text will have a blue background to it. Moving the caret
        with a text motion removes the selection (does not remove the text).

        NOTE: this is not called with caret mouse selections. See on_press.

        Dispatches the on_text_interact event.

        motion - motion used by the user. These can be made with the user.

                 SHIFT + LEFT               SHIFT + RIGHT
                 SHIFT + UP                 SHIFT + DOWN
                 CONTROL + SHIFT + LEFT     CONTROL + SHIFT + RIGHT

        parameters: int (32-bit)
        """

        if not self.focus:
            return

        self.caret.on_text_motion_select(motion)
        self.dispatch_event("on_text_interact",
                            self.index,
                            self.selection[:2]
                           )

    def on_press(self, x, y, buttons, modifiers):
        """The entry is pressed. This will do a number of things.
            - The caret's position is set to the nearest character.
            - The history will add the caret's position.
            - If text is selected, the selection will be removed.
            - If the Shift key is being held, a selection will be created
              between the current caret index and the closest character to
              the mouse.
            - If two clicks are made within 0.5 seconds (double-click), the
              current word is selected.
            - If three clicks are made within 0.5 seconds (triple-click), the
              current paragraph is selected.
            - If there is a placeholder text, the text is removed.

        Dispatches the on_text_interact event.

        x - x position of the press
        y - y position of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        _x, _y = x - self.layout.x, y - self.layout.y

        if self.text == self.placeholder:
            self.text = None

        index_before = self.index

        self.caret.on_mouse_press(x, y, buttons, modifiers)

        index_after = self.index

        self.mark = None

        if index_before is not index_after:
            # Add history
            self.history.append(index_after)
            self.dispatch_event("on_text_interact", self.index, None)

        if self.keys[SHIFT]:
            # Not required, but more clean
            indices = sorted((index_before, index_after))

            self.selection = indices
            self.mark = max(indices)

    def on_drag(self, x, y, dx, dy, buttons, modifiers):
        """The user dragged the mouse when it was pressed. This can create
        selections on entries.

        Dispatches the on_text_interact event.

        x - x position of the current position
        y - y position of the current position
        dx - movement in x vector from the last position
        dy - movement in y vector from the last position

        buttons - buttons that were dragged with the mouse
        modifiers - modifiers being held down

        parameters: int, int, float, float, int (32-bit), int (32-bit)
        """

        _x, _y = x - self.layout.x, y - self.layout.y

        if self.press:
            self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
            self.dispatch_event("on_text_interact",
                                self.index,
                                self.selection[:2]
                               )

            self.index = self.caret.position
        else:
            if self.focus:
                self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
                self.dispatch_event("on_text_interact",
                                    self.index,
                                    self.selection[:2]
                                   )

                self.index = self.caret.position

    def update(self):
        """Update the caret and entry. This schedules caret blinking and
        keeps track of focus.
        """

        if not self.length == len(self.text):
            self.length = len(self.text)

        if self.hover and not self.focus:
            self.image.texture = self.hover_image
        if self.focus:
            self.image.texture = self.focus_image

        if not self.hover and \
            not self.press and \
            not self.disable:
            self.image.texture = self.normal_image

        if self.focus:
            self.caret.on_activate()

        else:
            self.index = 0
            self.mark = None

            self.caret.on_deactivate()

    def on_text_edit(self, text, previous):
        """Text in the entry has been edited or modified. This may be done via
        user interaction or script. Text deletions can be found by checking the
        difference between the previous text and the new text.

        text - text that was entered. Usually just a character in length. If a
               a deletion was made, then the text will be a blank string.
        previous - previous text before modification

        parameters: str, str
        """

    def on_text_interact(self, index, selection):
        """Text in the entry was interacted somehow by the user. This is
        dispatched on text selection, or motion related the caret. Deletions
        do not trigger this event or other text modifications.

        index - index of the caret. This can be accessed by the index property.
        selection - selection made by the user

        parameters: int, list (see selection)
        """

Entry.register_event_type("on_text_edit")
Entry.register_event_type("on_text_interact")


class Pushable(Widget):
    """Pushable widget to invoke and call commands. This is an extended version
    of the button and allows more modifications.
    """

    def __init__(
                 self, text, x, y, command=None, parameters=[],
                 images=(), font=default_font,
                ):

        """Initialize a pushable. See button documentation for more information.

        text - text to be displayed on the button
        x - x position of the button
        y - y position of the button
        command - command to be invoked when the button is called
        parameters - parameters of the callable when invoked
        image - image of the button as an image
        font - font of the button

        The last parameter is for parameters of the image.

        parameters: str, int, int, callable, list, tuple, Font
        """

        # A two-component widget:
        #     - Image
        #     - Label

        self.image = Image(images[0], x, y)
        self.label = Label(text, x, y, font=font)

        Widget.__init__(self, self.image)

        self.text = text
        self.x = x
        self.y = y
        self.command = command
        self.parameters = parameters
        self.font = font

        self.normal_image = load_texture(images[0])
        self.hover_image = load_texture(images[1])
        self.press_image = load_texture(images[1])
        self.disable_image = load_texture(images[1])

    def _update_position(self, x, y):
        """Update the position of the widget. This is called internally
        whenever position properties are modified.
        """

        self.image.x = self.label.x = x
        self.image.y = self.label.y = y

    def invoke(self):
        """Invoke the button. This switches its image to a pressed state and
        calls the its associated command with the specified parameters. If the
        button is disabled this has no effect.

        Dispatches the on_push event.
        """

        if self.disable or not self.command:
            return

        self.press = True

        self.dispatch_event("on_push")

        if self.parameters:
            self.command(self.parameters)
        else:
            self.command()

    def draw(self):
        """Draw the button.

        1. Image - background image of the button
        2. Label - text of the button
        """

    def on_press(self, x, y, buttons, modifiers):
        """The button is pressed. This invokes its command if the mouse button
        is the left one.

        TODO: add specifying proper mouse button in settings

        x - x position of the press
        y - y position of the press
        buttons - buttons that were pressed with the mouse
        modifiers - modifiers being held down

        parameters: int, int, int (32-bit), int (32-bit)
        """

        if buttons == MOUSE_BUTTON_LEFT:
            self.invoke()

    def on_key(self, keys, modifiers):
        """A key is pressed. This is used for keyboard shortcuts when the
        button has focus.

        keys - key pressed
        modifiers - modifier pressed

        parameters: int (32-bit), int (32-bit)
        """

        if keys == SPACE and self.focus:
            self.invoke()

    def on_key_press(self, keys, modifiers):
        """A key is pressed, regardless if the button has focus. Used for
        binding commands to keyboard events.

        keys - key pressed
        modifiers - modifier pressed

        parameters: int, int
        """

        if isinstance(self.bindings, list):
            if keys in self.bindings:
                self.invoke()

        else:
            if self.bindings == keys:
                self.invoke()

    def update(self):
        self.image.normal_image = self.normal_image
        self.image.hover_image = self.hover_image
        self.image.press_image = self.press_image

        if self.disable:
            self.image.texture = self.disable_image

        # .update is not called for the Label, as it is uneccessary for the
        # Label to switch colors on user events.
