import tkinter as tk
from tkinter import messagebox
import gpt_functions

# Creating main tkinter window
root = tk.Tk()
root.geometry("800x600") 
root.title("simplegptpinecone")

# Creating a label for URL input
url_label = tk.Label(root, text = "Enter the URL of your PDF document:")
url_label.pack()

# Creating a text field for URL
url_entry = tk.Entry(root, width = 50)
url_entry.pack()

# Creating a label for question input
question_label = tk.Label(root, text = "Enter your question:")
question_label.pack()

# Creating a text field for question
question_entry = tk.Entry(root, width = 50)
question_entry.pack()

# Creating a text field for answer
answer_label = tk.Label(root, text = "Answer:")
answer_label.pack()

# Setting wrap="word" and adding horizontal and vertical scrollbars
scrollbar = tk.Scrollbar(root)
scrollbar.pack(side="right", fill="y")
answer_text = tk.Text(root, width = 50, height = 10, wrap="word", yscrollcommand=scrollbar.set)
answer_text.pack(side="left", fill="both", expand=True)
scrollbar.config(command=answer_text.yview)

def submit():
    url = url_entry.get()
    question = question_entry.get()

    answer = gpt_functions.ask_question_from_gui(url, question)
    
    # Clear the previous answer
    answer_text.delete(1.0, tk.END)
    
    # Insert the new answer
    if answer:
        answer_text.insert(tk.END, answer)

# Creating a button for submission
submit_button = tk.Button(root, text = "Submit", command = submit)
submit_button.pack()

# Running the GUI
root.mainloop()







