from kivy.graphics import Color, Rectangle
from kivy.uix.layout import Layout
from kivy.uix.widget import Widget


def add_widgets(*widgets, to: Widget):
    for widget in widgets:
        to.add_widget(widget)


def add_colour(layout: Layout, colour):
    with layout.canvas.before:
        Color(*colour)
        layout.bg_rect = Rectangle(size=layout.size, pos=layout.pos)

        def update(instance, value):
            instance.bg_rect.size = instance.size
            instance.bg_rect.pos = instance.pos
        layout.bind(size=update, pos=update)


def hue_to_rgb(h):
    h_prime = (h % 360) / 60.0
    x = 1 - abs(h_prime % 2 - 1)
    if h_prime < 0:
        r, g, b = 0, 0, 0
    elif h_prime < 1:
        r, g, b = 1, x, 0
    elif h_prime < 2:
        r, g, b = x, 1, 0
    elif h_prime < 3:
        r, g, b = 0, 1, x
    elif h_prime < 4:
        r, g, b = 0, x, 1
    elif h_prime < 5:
        r, g, b = x, 0, 1
    else:
        r, g, b = 1, 0, x
    # print(f'{r=},{g=},{b=}')
    return [r, g, b, 1]
