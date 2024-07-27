#!/usr/bin/python3
import urwid
import subprocess
import threading

class E_mitiApp:
    def __init__(self):
        self.palette = [
            ('banner', 'light cyan', 'black'),
            ('streak', 'yellow', 'black'),
            ('bg', 'white', 'black'),
            ('button', 'light green', 'dark blue'),
            ('button_focus', 'black', 'white'),
        ]
        
        self.loop = None
        self.build_ui()

    def build_ui(self):
        welcome_text = urwid.BigText("Welcome to E-miti", urwid.font.HalfBlock7x7Font())
        welcome_text = urwid.Padding(welcome_text, 'center', width='clip')

        subtitle = urwid.Text(("streak", "Negpdo-12"), align='center')

        button = urwid.Button("Enter", on_press=self.on_enter)
        button = urwid.AttrMap(button, 'button', focus_map='button_focus')
        button = urwid.Padding(button, align='center', width=20)

        content = urwid.Pile([
            welcome_text,
            urwid.Divider(),
            subtitle,
            urwid.Divider(),
            button
        ])

        content = urwid.Filler(content, valign='middle')
        content = urwid.LineBox(content, title="E-miti", title_align='center')
        background = urwid.AttrMap(content, 'bg')

        self.loop = urwid.MainLoop(background, palette=self.palette, unhandled_input=self.unhandled_input)

    def start_main(self):
        subprocess.run(["python3", "main.py"])

    def on_enter(self, button):
        threading.Thread(target=self.start_main).start()
        raise urwid.ExitMainLoop()

    def unhandled_input(self, key):
        if key == 'q':
            self.loop.stop()

if __name__ == "__main__":
    app = E_mitiApp()
    app.loop.run()