from arcade import Window

from .key import Keys, Mouse

container = None


class Application(Window):
    
    def __init__(self, *args, **kwargs):
        Window.__init__(self, *args, **kwargs)
        
        self.mouse = Mouse()
        self.keys = Keys()
    
    def _get_title(self):
        """pyglet window title or caption. This is the text displayed on the
        toolbar. This is implemented because arcade only has functions to
        change the caption.
        
        type: property, str
        """
        
        return self.get_caption()
    
    def _set_title(self, title):
        self.set_caption(title)
    
    title = property(_get_title, _set_title)


# from pyglet.window import Window
# from pyglet.text import HTMLLabel
# from pyglet.app import run

# class MyApplication(Window):
    
#     def __init__(self, *args, **kwargs):
#         Window.__init__(self, *args, **kwargs)
        
#         self.label = HTMLLabel("This is some <u>underlined</u> text.",
#                                None, self.width / 2, self.height / 2
#                               )
        
#     def on_draw(self):
#         self.label.draw()

# if __name__ == "__main__":
#     application = MyApplication()
    
#     run()
