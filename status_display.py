import os
import pi3d

class StatusDisplay(pi3d.PointText):
    def __init__(self, x, y, camera):

        self.x = x
        self.y = y
        
        font_colour = (255,255,255, 255)
        working_directory = os.path.dirname(os.path.realpath(__file__))
        font_path = os.path.abspath(os.path.join(working_directory, 'Fonts', 'NotoSans-Regular.ttf'))

        # Create pointFont and the text manager to use it
        point_font = pi3d.Font(font_path, font_colour, codepoints=list(range(32,128)))
        super(StatusDisplay, self).__init__(font=point_font, camera=camera,
                                            max_chars=200, point_size=32)
        
    def display_list(self, display):
        current_y = self.y
        for item in display:
            newtxt = pi3d.TextBlock(self.x, current_y, 100, 0.0, len(item)
                                    , text_format=item,
                                    size=0.99, spacing="F", space=0.05, colour=(0.0, 1.0, 0.0, 1.0))
            self.add_text_block(newtxt)
            current_y = current_y - 25
