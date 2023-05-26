import tkinter as tk
from tkinter import messagebox
from gpt_functions import *

# Creating main tkinter windows
root = tk.Tk()
root.geometry("800x600") # You can set any size
root.title("OpenAI and Pinecone Query Interface")

# Creating a label for url input
url_label = tk.Label(root, text = "Enter a URL:")
url_label.pack()

# Creating a text field for url
url_entry = tk.Entry(root, width = 100)
url_entry.pack()

# Creating a button for submission
upload_button = tk.Button(root, text = "Upload from URL", command = upload_from_url)
upload_button.pack()

# Creating a label for question input
question_label = tk.Label(root, text = "Enter your question:")
question_label.pack()

# Creating a text field for question
question_entry = tk.Entry(root, width = 100)
question_entry.pack()

# Creating a button for submission
submit_button = tk.Button(root, text = "Submit", command = ask_question_from_gui)
submit_button.pack()

# Creating a text field for answer
answer_label = tk.Label(root, text = "Answer:")
answer_label.pack()

# Create a scroll bar
scrollbar_horizontal = tk.Scrollbar(root, orient = 'horizontal')
scrollbar_horizontal.pack(side = 'bottom', fill = 'x')

scrollbar_vertical = tk.Scrollbar(root)
scrollbar_vertical.pack(side = 'right', fill = 'y')

# Create text widget and specify size.
answer_text = tk.Text(root, width = 80, height = 10, wrap = 'word',
                      xscrollcommand = scrollbar_horizontal.set,
                      yscrollcommand = scrollbar_vertical.set)

answer_text.pack()

# Configure the scrollbars
scrollbar_horizontal.config(command = answer_text.xview)
scrollbar_vertical.config(command = answer_text.yview)

# Running the GUI
root.mainloop()