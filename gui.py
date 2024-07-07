from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget

class BoxLayoutExample(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    pass

class MainWidget(Widget):
    pass

class TheLabApp(App):
    pass

TheLabApp().run()