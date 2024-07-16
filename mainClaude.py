#!/usr/bin/python3
import urwid
import typing
from auth import register_user, authenticate_user
from inventory import get_inventory, add_item, update_item, delete_item
from datetime import datetime

class InventorySystem:
    def __init__(self):
        self.palette = [
            ('banner', 'light cyan', 'black'),
            ('streak', 'yellow', 'black'),
            ('bg', 'white', 'black'),
            ('button', 'white', 'black'),
            ('button_focus', 'black', 'white'),
            ('header', 'light cyan', 'black'),
            ('body', 'light gray', 'black'),
            ('footer', 'black', 'light cyan'),
            ('key', 'light cyan', 'black', 'bold'),
            ('reversed', 'standout', ''),
            ('success', 'dark green', 'black'),
            ('error', 'dark red', 'black'),
            ('expired', 'dark red', 'black'),
            ('flagged', 'yellow', 'black'),
        ]
        self.choices = ["Register", "Login", "Exit"]
        self.inventory_choices = ["Add Item", "Update Item", "Delete Item", "Logout"]
        self.main = urwid.Padding(urwid.SolidFill(), left=2, right=2)
        self.top = urwid.Overlay(self.main, urwid.SolidFill("\N{MEDIUM SHADE}"),
            align="center", width=("relative", 80),
            valign="middle", height=("relative", 80),
            min_width=20, min_height=9)

    def run(self):
        self.main_menu()
        urwid.MainLoop(self.top, self.palette, unhandled_input=self.handle_input).run()

    def handle_input(self, key):
        if key in ("q", "Q"):
            raise urwid.ExitMainLoop()

    def main_menu(self):
        title = urwid.BigText("E-miti Inventory System", urwid.font.HalfBlock7x7Font())
        title = urwid.Padding(title, 'center', width='clip')
        
        subtitle = urwid.Text(("streak", "Negpdo-12"), align='center')
        
        buttons = []
        for choice in self.choices:
            button = urwid.Button(choice)
            urwid.connect_signal(button, 'click', self.item_chosen, choice)
            button = urwid.AttrMap(button, 'button', focus_map='button_focus')
            buttons.append(urwid.Padding(button, align='center', width=20))

        content = urwid.Pile([
            title,
            urwid.Divider(),
            subtitle,
            urwid.Divider(),
            *buttons
        ])

        content = urwid.Filler(content, valign='middle')
        content = urwid.LineBox(content, title="E-miti", title_align='center')
        self.main.original_widget = urwid.AttrMap(content, 'bg')

    def item_chosen(self, button, choice):
        if choice == "Register":
            self.main.original_widget = self.register_form()
        elif choice == "Login":
            self.main.original_widget = self.login_form()
        elif choice == "Exit":
            self.exit_program(button)

    def exit_program(self, button):
        raise urwid.ExitMainLoop()

    def register_form(self):
        body = [urwid.Text("Register"), urwid.Divider()]
        username_edit = urwid.Edit("Username: ")
        password_edit = urwid.Edit("Password: ", mask="*")

        role_group = []
        roles = ["Admin", "Pharmacist", "Inventory Manager", "Hospital"]
        role_options = [urwid.RadioButton(role_group, role) for role in roles]
        
        register_button = urwid.Button("Register")
        urwid.connect_signal(register_button, "click", self.register_action, (username_edit, password_edit, role_group))

        body.extend([
            username_edit,
            password_edit,
            urwid.Text("Role:"),
            *role_options,
            urwid.AttrMap(register_button, None, focus_map="reversed"),
        ])
        
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def register_action(self, button, edits):
        username = edits[0].edit_text
        password = edits[1].edit_text
        role_group = edits[2]

        selected_role = next((rb.label for rb in role_group if rb.state), None)
        
        if not selected_role:
            response = urwid.Text(("error", "Please select a role\n"))
        elif register_user(username, password, selected_role.lower()):
            response = urwid.Text(("success", "Registration successful\n"))
        else:
            response = urwid.Text(("error", "Username already taken\n"))
        
        done = urwid.Button("Ok")
        urwid.connect_signal(done, "click", lambda button: self.main_menu())
        self.main.original_widget = urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map="reversed")]))

    def login_form(self):
        body = [urwid.Text("Login"), urwid.Divider()]
        username_edit = urwid.Edit("Username: ")
        password_edit = urwid.Edit("Password: ", mask="*")
        login_button = urwid.Button("Login")
        urwid.connect_signal(login_button, "click", self.login_action, (username_edit, password_edit))
        body.extend([username_edit, password_edit, urwid.AttrMap(login_button, None, focus_map="reversed")])
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    def login_action(self, button, edits):
        username = edits[0].edit_text
        password = edits[1].edit_text
        if authenticate_user(username, password):
            self.inventory_menu(username)
        else:
            response = urwid.Text(("error", "Login failed\n"))
            done = urwid.Button("Ok")
            urwid.connect_signal(done, "click", self.main_menu)
            self.main.original_widget = urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map="reversed")]))

    def inventory_menu(self, username):
        inventory_ui = InventoryUI(username, self.main)
        inventory_ui.show_inventory()

class InventoryUI:
    def __init__(self, username, main_widget):
        self.username = username
        self.main = main_widget

    def show_inventory(self):
        tasks_content = [
            ("header", " ID   NAME           EXPIRY_DATE   PRICE     QUANTITY           CODE      "),
        ]
        inventory = get_inventory(self.username)

        max_widths = [len(col) for col in tasks_content[0][1].split()]

        for item_list in inventory.values():
            for item in item_list:
                max_widths[0] = max(max_widths[0], len(str(item['id'])) + len("ID"))
                max_widths[1] = max(max_widths[1], len(item['name']) + len("NAME"))
                max_widths[2] = max(max_widths[2], len(item['expiry_date']) + len("EXPIRY_DATE"))
                max_widths[3] = max(max_widths[3], len(str(item['price'])) + len("PRICE"))
                max_widths[4] = max(max_widths[4], len(str(item['quantity'])) + len("QUANTITY"))
                max_widths[5] = max(max_widths[5], len(str(item['Code'])) + len("CODE"))

        tasks_content[0] = ("header", f" ID{' '*(max_widths[0]-2)} NAME{' '*(max_widths[1]-4)} EXPIRY_DATE{' '*(max_widths[2]-11)} PRICE{' '*(max_widths[3]-6)} QUANTITY{' '*(max_widths[4]-8)} CODE{' '*(max_widths[5]-4)}")

        for item_list in inventory.values():
            for item in item_list:
                if item['expiry_date'] < datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                    tasks_content.append(("expired", f" {item['id']}{' '*(max_widths[0]-len(str(item['id'])))} {item['name']}{' '*(max_widths[1]-len(item['name']))} {item['expiry_date']}{' '*(max_widths[2]-len(item['expiry_date']))} {item['price']}{' '*(max_widths[3]-len(str(item['price'])))} {item['quantity']}{' '*(max_widths[4]-len(str(item['quantity'])))} {item['Code']}{' '*(max_widths[5]-len(str(item['Code'])))}"))
                else:
                    tasks_content.append(("body", f" {item['id']}{' '*(max_widths[0]-len(str(item['id'])))} {item['name']}{' '*(max_widths[1]-len(item['name']))} {item['expiry_date']}{' '*(max_widths[2]-len(item['expiry_date']))} {item['price']}{' '*(max_widths[3]-len(str(item['price'])))} {item['quantity']}{' '*(max_widths[4]-len(str(item['quantity'])))} {item['Code']}{' '*(max_widths[5]-len(str(item['Code'])))}"))

        tasks_list = urwid.SimpleListWalker([urwid.AttrMap(urwid.Text(item[1]), item[0]) for item in tasks_content])

        menu_items = [
            urwid.Text(f"=========== Welcome back, {self.username} ==========="),
            urwid.Text(""),
            urwid.Button("Add Item", on_press=lambda button: self.handle_menu_action("add")),
            urwid.Button("Update Item", on_press=lambda button: self.handle_menu_action("update")),
            urwid.Button("Delete Item", on_press=lambda button: self.handle_menu_action("delete")),
            urwid.Button("Logout", on_press=lambda button: self.handle_menu_action("logout")),
        ]
        right_menu = urwid.ListBox(urwid.SimpleFocusListWalker(menu_items))

        layout = urwid.Columns([
            ('weight', 2, urwid.ListBox(tasks_list)),
            ('weight', 1, right_menu),
        ], dividechars=1)

        framed_layout = urwid.LineBox(layout, title=f"E-miti Inventory System", title_align='center')
        self.main.original_widget = urwid.AttrMap(framed_layout, 'bg')

    def handle_menu_action(self, action):
        if action == "add":
            self.main.original_widget = self.add_item_form()
        elif action == "update":
            self.main.original_widget = self.update_item_form()
        elif action == "delete":
            self.main.original_widget = self.delete_item_form()
        elif action == "logout":
            InventorySystem().main_menu()

    # Add methods for add_item_form, update_item_form, delete_item_form, and their respective actions

if __name__ == "__main__":
    InventorySystem().run()