import os

def create_new_list(list_name):
    with open(list_name + ".txt", "w") as f:
        print("New list created successfully!")

def display_list():
    list_name = input("Enter the name of the list you want to display: ")
    if os.path.exists(list_name + ".txt"):
        with open(list_name + ".txt", "r") as f:
            print(f.read())
    else:
        print("No such list exists!")

def add_item_to_list():
    list_name = input("Enter the name of the list you want to add an item to: ")
    item = input("Enter the item you want to add: ")
    if os.path.exists(list_name + ".txt"):
        with open(list_name + ".txt", "a") as f:
            f.write(item + "\n")
            print("Item added successfully!")
    else:
        print("No such list exists!")

def remove_item_from_list():
    list_name = input("Enter the name of the list you want to remove an item from: ")
    item = input("Enter the item you want to remove: ")
    if os.path.exists(list_name + ".txt"):
        with open(list_name + ".txt", "r") as f:
            lines = f.readlines()
        with open(list_name + ".txt", "w") as f:
            for line in lines:
                if line.strip("\n") != item:
                    f.write(line)
            print("Item removed successfully!")
    else:
        print("No such list exists!")