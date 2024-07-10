from __future__ import annotations
import urwid
import typing
from auth import register_user, authenticate_user
from inventory import get_inventory, add_item, update_item, delete_item

choices = ["Register", "Login", "Exit"]

palette = [
    ("reversed", "standout", ""),
    ("success", "dark green", ""),
    ("error", "dark red", ""),
    ("info", "light blue", ""),
]

def menu(title: str, choices_: list[str], signals: typing.Optional[dict[str, typing.Callable]] = None) -> urwid.ListBox:
    body = [urwid.Text(title), urwid.Divider()]
    for c in choices_:
        button = urwid.Button(c)
        if signals and c in signals:
            urwid.connect_signal(button, "click", signals[c])
        else:
            urwid.connect_signal(button, "click", item_chosen, c)
        body.append(urwid.AttrMap(button, None, focus_map="reversed"))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def item_chosen(button: urwid.Button, choice: str) -> None:
    if choice == "Register":
        main.original_widget = register_form()
    elif choice == "Login":
        main.original_widget = login_form()
    elif choice == "Exit":
        exit_program(button)

def register_form() -> urwid.Widget:
    body = [urwid.Text("Register"), urwid.Divider()]
    username_edit = urwid.Edit("Username: ")
    password_edit = urwid.Edit("Password: ", mask="*")
    role_edit = urwid.Edit("Role (Admin/Pharmacist/Inventory Manager): ")
    register_button = urwid.Button("Register")
    urwid.connect_signal(register_button, "click", register_action, (username_edit, password_edit, role_edit))
    body.extend([username_edit, password_edit, role_edit, urwid.AttrMap(register_button, None, focus_map="reversed")])
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def register_action(button: urwid.Button, edits: typing.Tuple[urwid.Edit, urwid.Edit, urwid.Edit]) -> None:
    username = edits[0].edit_text
    password = edits[1].edit_text
    role = edits[2].edit_text.lower().strip()
    
    if role not in ['admin', 'pharmacist', 'inventory manager']:
        response = urwid.Text(("error", "Invalid role. Must be one of: Admin, Pharmacist, Inventory Manager\n"))
    elif register_user(username, password, role):
        response = urwid.Text(("success", "Registration successful\n"))
    else:
        response = urwid.Text(("error", "Username already taken\n"))
    
    done = urwid.Button("Ok")
    urwid.connect_signal(done, "click", lambda button: main_menu())
    main.original_widget = urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map="reversed")]))

def login_form() -> urwid.Widget:
    body = [urwid.Text("Login"), urwid.Divider()]
    username_edit = urwid.Edit("Username: ")
    password_edit = urwid.Edit("Password: ", mask="*")
    login_button = urwid.Button("Login")
    urwid.connect_signal(login_button, "click", login_action, (username_edit, password_edit))
    body.extend([username_edit, password_edit, urwid.AttrMap(login_button, None, focus_map="reversed")])
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def login_action(button: urwid.Button, edits: typing.Tuple[urwid.Edit, urwid.Edit]) -> None:
    username = edits[0].edit_text
    password = edits[1].edit_text
    success, role = authenticate_user(username, password)
    if success:
        response = urwid.Text(("success", f"Login successful. Role: {role.capitalize()}\n"))
        done = urwid.Button("Ok")
        urwid.connect_signal(done, "click", lambda button: inventory_menu(username))
    else:
        response = urwid.Text(("error", "Invalid username or password\n"))
        done = urwid.Button("Ok")
        urwid.connect_signal(done, "click", lambda button: main_menu())
    
    main.original_widget = urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map="reversed")]))

def main_menu() -> None:
    main.original_widget = menu("E-miti Inventory System", choices)

def inventory_menu(username: str) -> None:
    def set_main_widget(widget: urwid.Widget) -> None:
        main.original_widget = widget
    
    options = {
        "Add Item": lambda button: set_main_widget(add_item_form(username)),
        "Update Item": lambda button: set_main_widget(update_item_form(username)),
        "Delete Item": lambda button: set_main_widget(delete_item_form(username)),
        "View Inventory": lambda button: set_main_widget(view_inventory(username)),
        "Logout": lambda button: main_menu(),
    }
    choices = ["Add Item", "Update Item", "Delete Item", "View Inventory", "Logout"]
    main.original_widget = menu("Inventory Management", choices, options)

def add_item_form(username: str) -> urwid.Widget:
    body = [urwid.Text("Add Item"), urwid.Divider()]
    name_edit = urwid.Edit("Item Name: ")
    quantity_edit = urwid.Edit("Quantity: ")
    price_edit = urwid.Edit("Price: ")
    description_edit = urwid.Edit("Description: ")
    expiry_date_edit = urwid.Edit("Expiry Date (YYYY-MM-DD): ")
    add_button = urwid.Button("Add")
    urwid.connect_signal(add_button, "click", add_item_action, (username, name_edit, quantity_edit, price_edit, description_edit, expiry_date_edit))
    body.extend([name_edit, quantity_edit, price_edit, description_edit, expiry_date_edit, urwid.AttrMap(add_button, None, focus_map="reversed")])
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def add_item_action(button: urwid.Button, edits: typing.Tuple[str, urwid.Edit, urwid.Edit, urwid.Edit, urwid.Edit, urwid.Edit]) -> None:
    username = edits[0]
    name = edits[1].edit_text
    quantity = edits[2].edit_text
    price = edits[3].edit_text
    description = edits[4].edit_text
    expiry_date = edits[5].edit_text
    try:
        quantity = int(quantity)
        price = float(price)
        if add_item(username, name, quantity, price, description, expiry_date):
            response = urwid.Text(("success", "Item added successfully\n"))
        else:
            response = urwid.Text(("error", "Item already exists\n"))
    except ValueError:
        response = urwid.Text(("error", "Invalid input. Quantity must be an integer and price must be a float\n"))

    done = urwid.Button("Ok")
    urwid.connect_signal(done, "click", lambda button: inventory_menu(username))
    main.original_widget = urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map="reversed")]))

def update_item_form(username: str) -> urwid.Widget:
    body = [urwid.Text("Update Item"), urwid.Divider()]
    name_edit = urwid.Edit("Item Name: ")
    quantity_edit = urwid.Edit("Quantity: ")
    price_edit = urwid.Edit("Price: ")
    description_edit = urwid.Edit("Description: ")
    expiry_date_edit = urwid.Edit("Expiry Date (YYYY-MM-DD): ")
    update_button = urwid.Button("Update")
    urwid.connect_signal(update_button, "click", update_item_action, (username, name_edit, quantity_edit, price_edit, description_edit, expiry_date_edit))
    body.extend([name_edit, quantity_edit, price_edit, description_edit, expiry_date_edit, urwid.AttrMap(update_button, None, focus_map="reversed")])
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def update_item_action(button: urwid.Button, edits: typing.Tuple[str, urwid.Edit, urwid.Edit, urwid.Edit, urwid.Edit, urwid.Edit]) -> None:
    username = edits[0]
    name = edits[1].edit_text
    quantity = edits[2].edit_text
    price = edits[3].edit_text
    description = edits[4].edit_text
    expiry_date = edits[5].edit_text
    try:
        quantity = int(quantity)
        price = float(price)
        if update_item(username, name, quantity, price, description, expiry_date):
            response = urwid.Text(("success", "Item updated successfully\n"))
        else:
            response = urwid.Text(("error", "Item does not exist\n"))
    except ValueError:
        response = urwid.Text(("error", "Invalid input. Quantity must be an integer and price must be a float\n"))

    done = urwid.Button("Ok")
    urwid.connect_signal(done, "click", lambda button: inventory_menu(username))
    main.original_widget = urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map="reversed")]))

def delete_item_form(username: str) -> urwid.Widget:
    body = [urwid.Text("Delete Item"), urwid.Divider()]
    name_edit = urwid.Edit("Item Name: ")
    delete_button = urwid.Button("Delete")
    urwid.connect_signal(delete_button, "click", delete_item_action, (username, name_edit))
    body.extend([name_edit, urwid.AttrMap(delete_button, None, focus_map="reversed")])
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def delete_item_action(button: urwid.Button, edits: typing.Tuple[str, urwid.Edit]) -> None:
    username = edits[0]
    name = edits[1].edit_text
    if delete_item(username, name):
        response = urwid.Text(("success", "Item deleted successfully\n"))
    else:
        response = urwid.Text(("error", "Item does not exist\n"))

    done = urwid.Button("Ok")
    urwid.connect_signal(done, "click", lambda button: inventory_menu(username))
    main.original_widget = urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map="reversed")]))

def view_inventory(username: str) -> urwid.Widget:
    inventory = get_inventory(username)
    body = [urwid.Text("Inventory"), urwid.Divider()]
    for item_name, item_list in inventory.items():
        for item in item_list:
            body.append(urwid.Text(f"{item['name']}: {item['quantity']}"))
    done = urwid.Button("Back")
    urwid.connect_signal(done, "click", lambda button: inventory_menu(username))
    body.append(urwid.AttrMap(done, None, focus_map="reversed"))
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def exit_program(button: urwid.Button) -> None:
    raise urwid.ExitMainLoop()

main = urwid.Padding(menu("E-miti Inventory System", choices), left=2, right=2)
top = urwid.Overlay(
    main,
    urwid.SolidFill("\N{MEDIUM SHADE}"),
    align=urwid.CENTER,
    width=(urwid.RELATIVE, 60),
    valign=urwid.MIDDLE,
    height=(urwid.RELATIVE, 60),
    min_width=20,
    min_height=9,
)
urwid.MainLoop(top, palette=palette).run()
