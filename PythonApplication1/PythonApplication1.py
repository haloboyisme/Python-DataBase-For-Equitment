import tkinter as tk
import sqlite3
from tkinter import filedialog
from PIL import ImageTk, Image
import io
import csv

# create database and table if they don't exist
conn = sqlite3.connect('notes.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS notes
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              image BLOB,
              notes TEXT)''')

# create the main window
root = tk.Tk()
root.title("Notes App")

# create a label for the image
image_label = tk.Label(root, text="Image:")
image_label.pack()

# create a button to select an image
def select_image():
    file_path = filedialog.askopenfilename()
    image_entry.insert(0, file_path)

image_button = tk.Button(root, text="Select Image", command=select_image)
image_button.pack()

# create an entry for the image path
image_entry = tk.Entry(root)
image_entry.pack()
image_entry.delete(0, 'end')


# create a label for the notes
notes_label = tk.Label(root, text="Notes:")
notes_label.pack()

# create a text box for the notes
notes_textbox = tk.Text(root, height=10, width=50)
notes_textbox.pack()
notes_textbox.delete('1.0', 'end')


# create a function to save the data to the database
def save_data():
    image_path = image_entry.get()
    with open(image_path, 'rb') as f:
        image_data = f.read()
    notes = notes_textbox.get("1.0", "end")
    c.execute("INSERT INTO notes (image, notes) VALUES (?, ?)", (image_data, notes))
    conn.commit()
    image_entry.delete(0, 'end')
    notes_textbox.delete('1.0', 'end')


# create a button to save the data to the database
save_button = tk.Button(root, text="Save", command=save_data)
save_button.pack()

# create a label for the saved notes
saved_notes_label = tk.Label(root, text="Saved Notes:")
saved_notes_label.pack()

# create a treeview to display saved notes
from tkinter import ttk
note_tree = ttk.Treeview(root, columns=['id', 'notes'])
note_tree.heading('id', text='ID')
note_tree.heading('notes', text='Notes')
note_tree.pack()

# create a function to load the saved notes from the database
def load_data():
    note_tree.delete(*note_tree.get_children())
    c.execute("SELECT id, notes FROM notes")
    rows = c.fetchall()
    for row in rows:
        note_tree.insert('', 'end', text=row[0], values=row)

# create a button to load the saved notes from the database
load_button = tk.Button(root, text="Load", command=load_data)
load_button.pack()

# create a function to remove the selected item from the tree and database
def remove_data():
    selection = note_tree.selection()
    if selection:
        note_id = note_tree.item(selection[0], 'text')
        c.execute("DELETE FROM notes WHERE id=?", (note_id,))
        conn.commit()
        note_tree.delete(selection)

# create a button to remove the selected item from the tree and database
remove_button = tk.Button(root, text="Remove", command=remove_data)
remove_button.pack()

# create a function to show the selected image
def show_image():
    selection = note_tree.selection()
    if selection:
        note_id = note_tree.item(selection[0], 'text')
        c.execute("SELECT image FROM notes WHERE id=?", (note_id,))
        row = c.fetchone()
        if row:
            image_data = row[0]
            img = Image.open(io.BytesIO(image_data))
            img = img.resize((200, 200), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)
            selected_image_label.config(image=img)
            selected_image_label.image = img


# create a button to show the selected image
show_image_button = tk.Button(root, text="Show Image", command=show_image)
show_image_button.pack()

# create a label for the selected image
selected_image_label = tk.Label(root)
selected_image_label.pack()

# create a button to clear the displayed tree
clear_button = tk.Button(root, text="Clear", command=lambda: note_tree.delete(*note_tree.get_children()))
clear_button.pack()



root.mainloop()

# close the database connection
conn.close()
