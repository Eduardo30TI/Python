from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


class Interface(App):

    def build(self):

        box=BoxLayout(orientation='vertical')

        box.add_widget(Label(text='1',font_size=30))
        box.add_widget(Button(text='Click',font_size=30))


        return box

    pass


if __name__=='__main__':

    Interface().run()

    pass