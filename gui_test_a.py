from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup


class FilePickerPopup(Popup):
    def __init__(self, select_callback, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Pick a file'
        self.size_hint = (0.9, 0.9)
        
        layout = BoxLayout(orientation='vertical')
        self.filechooser = FileChooserListView()
        layout.add_widget(self.filechooser)
        
        buttons_layout = BoxLayout(size_hint_y=None, height=50)
        select_button = Button(text='Select')
        cancel_button = Button(text='Cancel')
        
        select_button.bind(on_press=lambda x: self.select_file(select_callback))
        cancel_button.bind(on_press=self.dismiss)
        
        buttons_layout.add_widget(select_button)
        buttons_layout.add_widget(cancel_button)
        
        layout.add_widget(buttons_layout)
        self.add_widget(layout)

    def select_file(self, select_callback):
        if self.filechooser.selection:
            select_callback(self.filechooser.selection[0])
        self.dismiss()



class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.label = Label(text='No file selected')
        layout.add_widget(self.label)
        
        open_button = Button(text='Open File Picker')
        open_button.bind(on_press=self.show_file_picker)
        self.fc = FileChooserListView()
        layout.add_widget(self.fc)
        layout.add_widget(open_button)
        
        return layout

    def show_file_picker(self, instance):
        file_picker_popup = FilePickerPopup(self.file_selected)
        file_picker_popup.open()

    def file_selected(self, filepath):
        self.label.text = f'Selected file: {filepath}'

if __name__ == '__main__':
    MyApp().run()
