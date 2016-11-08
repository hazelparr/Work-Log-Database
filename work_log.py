import os
import datetime
import sys
from collections import OrderedDict
from peewee import *

db = SqliteDatabase('work_log.db')

class Entry(Model):
    name = CharField(max_length = 255)
    task_name = CharField(max_length = 255)
    date = DateField(formats = '%Y-%m-%d')
    time_spent = IntegerField(default = 1)
    notes = CharField(max_length = 255)

    class Meta:
        database = db

def initialize():
    """Create the database and table if they don't exist"""
    db.connect()
    db.create_tables([Entry], safe=True)


def clear(): 
    """Clears screen when called"""   
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def get_name():
    """Asks user for employee name"""
    clear()
    name = input("Employee Name: ")

    if len(name) == 0:
        input("Name must have at least one character.")
        return get_name()
    else:
        return name
    

def get_task_name():
    """Asks user for task name"""
    clear()
    task_name = input("Task Name: ")

    if len(task_name) == 0:
        input("Name must have at least one character.")
        return get_task_name()
    else:
        return task_name


def get_notes():
    """Asks user for any additional notes"""
    clear()
    notes = input("Notes (Optional, leave blank if none): ")
    return notes


def get_minutes():
    """Validates if user input is an integer"""
    clear()
    minutes = input("Number of minutes spent: ")
    try:
        int(minutes)
    except ValueError:
        input("Entry must be an integer. Example: 1, 20. "
            "Press enter to continue.")
        return get_minutes()
    else:
        minutes = int(minutes)
        return minutes


def get_date(text=""):
    """Asks user for date, check if valid entry"""
    clear()
    date = input("Enter {}date (Format:YYYY-MM-DD): ".format(text))
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        input("Please enter date in this format: YYYY-MM-DD."
            " Press enter to continue.")
        return get_date()
    else:
        return date


def convert(date):
    """Converts date to datetime object"""
    converted_date = datetime.datetime.strptime(date, 
                    "%Y-%m-%d").date()
    return converted_date


def get_user_entry():
    """Gets user input for the data fields"""
    name = get_name()
    task_name = get_task_name()
    date = convert(get_date())
    time_spent = get_minutes()
    notes = get_notes()

    entry = {"name": name,
        "task_name": task_name,
        "date": date,
        "time_spent": time_spent,
        "notes": notes}

    print_entry(entry)

    while True:
        save = input("""Would you like to save the entry? 
[Y] - Yes
[N] - No
""").lower().strip()
        if save == "y":
            input("Entry saved succesfully. Press enter to continue.")
            return entry
        else:
            input("Entry NOT saved.")
            return None

def print_entry(entry):
    """prints entry to screen"""
    print("""
Employee Name: {name}
Task Name: {task_name}
Date: {date}
Time Spent: {time_spent}
Notes: {notes}
""".format(**entry))


def create_entry(entry):
    """Saves entry to database"""
    Entry.create(**entry)
    return entry



def add_entry():
    """Add an entry"""
    entry = get_user_entry()
    if entry:
        return create_entry(entry)


def select_entries():
    """Retrieves all entries from database"""
    return Entry.select().order_by(Entry.date.desc())


def list_entries(entries, search, field):
    """Shows list of search results"""
    clear()
    if entries:
        print("Your search results for {}:\n".format(search))
        for entry in entries:
            print(getattr(entry, field))
        input("Press enter to continue.")
        view_entries(entries)
    else:
        input("No results for {}. Press enter to continue. ".format(search))
        menu_loop()


def search_entry():
    """Search for an entry"""
    while True:
        clear()
        print("""
WORK.LOG - Log, edit, delete, save and seach your tasks!
--------------------------------------------------------
SEARCH MENU
[N] - Find by employee name
[D] - Find by date
[T] - Find by time spent
[S] - Find by term or string
[M] - Back to main menu
        """)

        option = input("Please select option from menu: "
                    ).lower().strip()

        if option in list("ndtsm"):
            break
        

    if option == "n":
        search = search_name()
        return search 
    elif option == "d":
        search = search_date()
        return search
    elif option == "t":
        search = search_minutes()
        return search
    elif option == "s":
        search = search_term()
        return search
    elif option == "m":
        menu_loop()
    else:
        input("Invalid entry. See menu for valid options. "
            "Press enter to continue.")



def search_name():
    """Searches database for user specified field: name"""
    search = get_name()
    entries = select_entries()
    entries = entries.where(Entry.name.contains(search))
    list_entries(entries, search, "name")
    return entries


def search_date():
    """Searches database for user specified field: date"""
    start = get_date("start ")
    end = get_date("end ")
    search = start + " - " + end
    entries = select_entries()
    entries = entries.where(
            (Entry.date >= start) & 
            (Entry.date <= end))
    list_entries(entries, search, "date")
    return entries


def search_minutes():
    """Searches database for user specified field: time spent"""
    search = get_minutes()
    entries = select_entries()
    entries = entries.where(Entry.time_spent == search)
    list_entries(entries, search, "time_spent")
    return entries


def search_term():
    """Searches database for a term or string in notes and task name"""
    search = input("Enter term or string: ")
    entries = select_entries()
    entries = entries.where(
            (Entry.task_name.contains(search)) |
            (Entry.notes.contains(search)))
    view_entries(entries)
    return entries


def delete_entry(entry):
    """Deletes an entry"""
    if input("""Are you sure? 
[Y] - Yes
[N] - No
""").lower().strip() == "y":
        entry.delete_instance()
        input("Entry deleted. Press enter to continue.")
        return None
    else:
        menu_loop()


def display_choices(index, entries):
    """Menu choices to page through multiple entries"""
    p = "[P] - Previous Entry"
    n = "[N] - Next Entry"
    e = "[E] - Edit Entry"
    d = "[D] - Delete an entry"   
    m = "[M] - Go back to Main Menu"

    menu = [p,n,e,d,m]

    if index == 0:
        menu.remove(p)
    if index == len(entries) - 1:
        menu.remove(n)

    for menu in menu:
        print(menu)


def edit_notes(entry):
    """Edit notes field on an entry"""
    entry.notes = get_notes()
    entry.save()
    input("Edit successful. ")
    return entry


def edit_name(entry):
    """Edit name field on an entry"""
    entry.name = get_name()
    entry.save()
    input("Edit successful. ")
    return entry


def edit_date(entry):
    """Edit date field on an entry"""
    entry.date = get_date()
    entry.save()
    input("Edit successful. ")
    return entry


def edit_task_name(entry):
    """Edit task name field on an entry"""
    entry.task_name = get_task_name()
    entry.save()
    input("Edit successful. ")
    return entry


def edit_time_spent(entry):
    """Edit time spent field on an entry"""
    entry.time_spent = get_minutes()
    entry.save()
    input("Edit successful. ")
    return entry


def edit_entry(entry):
    """Edit entries"""
    while True:
        clear()
        print("""
Which field would you like to edit?
[E] - Employee name
[D] - Date
[N] - Task Name
[T] - Time spent
[S] - Notes
[M] - Back to main menu

""")
        option = input("Please select option from menu: "
                    ).lower().strip()
        if option == "e":
            edit = edit_name(entry)
            return edit
        elif option == "d":
            edit = edit_date(entry)
            return edit
        elif option == "n":
            edit = edit_task_name(entry)
            return edit
        elif option == "t":
            edit = edit_time_spent(entry)
            return edit
        elif option == "s":
            edit = edit_notes(entry)
            return edit


def view_entries(search=None):
    """View all entries"""
    clear()
    if search:
        entries = search
    else:
        entries = select_entries()

    if len(entries) > 0:
        index = 0
        while True:
            clear()
            print("Displaying {} of {} entry/entries. \n".format(index+1, 
                    len(entries)))

            print("Employee Name: {}".format(entries[index].name))
            print("Task Name: {}".format(entries[index].task_name))
            print("Date: {}".format(entries[index].date))
            print("Time Spent: {}".format(entries[index].time_spent))
            print("Notes: {}".format(entries[index].notes))
            print("\n\n")
            display_choices(index, entries)

            choice = input("\nPlease select option from"
                    " menu. ").lower().strip()

            if index == 0 and choice == "n":
                index += 1
            elif (index > 0 and index < len(entries)-1 
                and choice == "p"):
                index -= 1
            elif (index > 0 and index < len(entries)-1 
                and choice == "n"):
                index += 1
            elif index == len(entries)-1 and choice == "p":
                index -= 1
            elif choice == "m":
                return None
            elif choice == "d":
                return delete_entry(entries[index])
            elif choice == "e":
                edit = edit_entry(entries[index])
                return edit   
            else:
                print("Invalid input. Refer to menu for valid choice.")
                
    else:
        input("No entry found. Press enter to continue.")
       


def quit_program():
    """Quit and exit program"""
    sys.exit()
    

menu = OrderedDict([
        ("A", add_entry),
        ("S", search_entry),
        ("V", view_entries),
        ("Q", quit_program)
        ])


def menu_loop():
    """Displays main menu"""
    while True:
        clear()
        print("""
WORK.LOG - Log, edit, delete, save and seach your tasks!
--------------------------------------------------------
MAIN MENU

""")
        for key, value in menu.items():
            print("[{}] - {}".format(key, value.__doc__))

        option = input("\nPlease select option from menu: ").upper().strip()

        if option in menu:
            menu[option]()
            
        else:
            input("Invalid choice. Check menu for valid choices.")





if __name__ == "__main__":
    initialize()
    menu_loop()




