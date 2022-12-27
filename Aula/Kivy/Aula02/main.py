from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class Interface(App):

    def build(self):

        box=BoxLayout(orientation='vertical')

        box2=BoxLayout()

        box.add_widget(Label(text='Mensagem',font_size=30))
        box.add_widget(Button(text='Click',font_size=30))

        box2.add_widget(Label(text='Mensagem2',font_size=30))
        box2.add_widget(Button(text='Click2',font_size=30))

        box.add_widget(box2)

        return box

        pass


    pass


if __name__=='__main__':

    Interface().run()

    pass