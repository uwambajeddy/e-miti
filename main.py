import urwid
import typing
from auth import register_user, authenticate_user
from inventory import get_inventory, add_item, update_item, delete_item

# Define the palette for the UI colors
palette = [
    ('header', 'light cyan', 'black'),
    ('body', 'light gray', 'black'),
    ('footer', 'black', 'light cyan'),
    ('key', 'light cyan', 'black', 'bold'),
    ('reversed', 'standout', ''),
    ('success', 'dark green', 'black'),
    ('error', 'dark red', 'black'),
]

choices = ["Register", "Login", "Exit"]
inventory_choices = ["Add Item", "Update Item", "Delete Item", "Logout"]

def inventory_menu(username: str) -> None:
    tasks_content = [
        ("header", " ID   NAME           EXPIRY_DATE   PRICE    QUANTITY  CREATED_AT          "),
    ]
    inventory = get_inventory(username)
    for item_list in inventory.values():
        for item in item_list:
            tasks_content.append(("body", f" {item['id']}    {item['name']}       {item['expiry_date']}    {item['price']}    {item['quantity']}        {item['created_at']} "))

    tasks_list = urwid.SimpleListWalker([urwid.AttrMap(urwid.Text(item[1]), item[0]) for item in tasks_content])

    # Create buttons for the menu options on the right side
    menu_items = [
        urwid.Button("Add Item", on_press=lambda button: handle_menu_action(username, "add")),
        urwid.Button("Update Item", on_press=lambda button: handle_menu_action(username, "update")),
        urwid.Button("Delete Item", on_press=lambda button: handle_menu_action(username, "delete")),
        urwid.Button("Logout", on_press=lambda button: handle_menu_action(username, "logout")),
    ]
    right_menu = urwid.ListBox(urwid.SimpleFocusListWalker(menu_items))

    # Define the main layout
    layout = urwid.Columns([
        ('weight', 2, urwid.ListBox(tasks_list)),
        ('weight', 1, right_menu),
    ], dividechars=1)

    frame = urwid.Frame(header=urwid.Text(" E-miti Inventory System"), body=layout)
    main.original_widget = frame

def handle_menu_action(username: str, action: str) -> None:
    if action == "add":
        main.original_widget = add_item_form(username)
    elif action == "update":
        main.original_widget = update_item_form(username)
    elif action == "delete":
        main.original_widget = delete_item_form(username)
    elif action == "logout":
        main.original_widget = menu("E-miti Inventory System", choices)

def add_item_form(username: str) -> urwid.Widget:
    body = [urwid.Text("Add Item"), urwid.Divider()]
    name_edit = urwid.Edit("Item Name: ")
    quantity_edit = urwid.Edit("Quantity: ")
    price_edit = urwid.Edit("Price: ")
    description_edit = urwid.Edit("Description: ")
    expiry_date_edit = urwid.Edit("Expiry Date: ")
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
            response = urwid.Text(("error", "Failed to add item\n"))
    except ValueError:
        response = urwid.Text(("error", "Invalid input. Quantity must be an integer and price must be a float\n"))

    done = urwid.Button("Ok")
    urwid.connect_signal(done, "click", lambda button: inventory_menu(username))
    main.original_widget = urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map="reversed")]))

def update_item_form(username: str) -> urwid.Widget:
    body = [urwid.Text("Update Item"), urwid.Divider()]
    name_edit = urwid.Edit("Item Name: ")
    quantity_edit = urwid.Edit("New Quantity: ")
    price_edit = urwid.Edit("New Price: ")
    description_edit = urwid.Edit("New Description: ")
    expiry_date_edit = urwid.Edit("New Expiry Date: ")
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

def exit_program(button: urwid.Button) -> None:
    raise urwid.ExitMainLoop()

def main_menu() -> None:
    main.original_widget = menu("E-miti Inventory System", choices)

def menu(title: str, choices_: typing.Iterable[str]) -> urwid.ListBox:
    body = [urwid.Text(title), urwid.Divider()]
    for c in choices_:
        button = urwid.Button(c)
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

    role_group = []
    roles = ["Admin", "Pharmacist", "Inventory Manager", "Hospital"]
    role_options = [urwid.RadioButton(role_group, role) for role in roles]
    
    register_button = urwid.Button("Register")
    urwid.connect_signal(register_button, "click", register_action, (username_edit, password_edit, role_group))

    body.extend([
        username_edit,
        password_edit,
        urwid.Text("Role:"),
        *role_options,
        urwid.AttrMap(register_button, None, focus_map="reversed"),
    ])
    # role_edit = urwid.Edit("Role (Admin/Pharmacist/Inventory Manager): ")
    # register_button = urwid.Button("Register")
    # urwid.connect_signal(register_button, "click", register_action, (username_edit, password_edit, role_edit))
    # body.extend([username_edit, password_edit, role_edit, urwid.AttrMap(register_button, None, focus_map="reversed")])
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def register_action(button: urwid.Button, edits: typing.Tuple[urwid.Edit, urwid.Edit, list]) -> None:
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
    if authenticate_user(username, password):
        inventory_menu(username)
    else:
        response = urwid.Text(("error", "Login failed\n"))
        done = urwid.Button("Ok")
        urwid.connect_signal(done, "click", main_menu)
        main.original_widget = urwid.Filler(urwid.Pile([response, urwid.AttrMap(done, None, focus_map="reversed")]))
        
def handle_input(key: str) -> None:
    if key in ("q", "Q"):
        raise urwid.ExitMainLoop()

main = urwid.Padding(menu("E-miti Inventory System", choices), left=2, right=2)
top = urwid.Overlay(main, urwid.SolidFill("\N{MEDIUM SHADE}"),
    align="center", width=("relative", 60),
    valign="middle", height=("relative", 60),
    min_width=20, min_height=9)
urwid.MainLoop(top, palette, unhandled_input=handle_input).run()
