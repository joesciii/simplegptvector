import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import gpt_functions
from ttkthemes import ThemedTk
import threading

#main tk window
root = ThemedTk(theme="arc")
root.geometry("800x600")
root.title("simplegptpinecone")

frame = ttk.Frame(root)
frame.pack(expand=True, fill="both")

frame.grid_columnconfigure(0, weight=1)
frame.grid_columnconfigure(2, weight=1)
frame.grid_rowconfigure(0, weight=1)
frame.grid_rowconfigure(8, weight=1)

url_label = ttk.Label(frame, text="Enter the URL content to be fed in. Supports PDF, plaintext and webpages:")
url_label.grid(row=1, column=1, sticky='ew', padx=10, pady=10)

url_entry = ttk.Entry(frame, width=70)
url_entry.grid(row=2, column=1, padx=10)

question_label = ttk.Label(frame, text="Enter your question:")
question_label.grid(row=3, column=1, sticky='ew', padx=10, pady=10)

question_entry = ttk.Entry(frame, width=70)
question_entry.grid(row=4, column=1, padx=10)

submit_button = ttk.Button(frame, text="Submit", command=None)  # we will add the command later
submit_button.grid(row=5, column=1, pady=10)

style = ttk.Style()
style.configure("TProgressbar", thickness=50)

progress_bar = ttk.Progressbar(frame, mode='indeterminate', length=500, style="TProgressbar")

answer_label = ttk.Label(frame, text="Answer:")
answer_label.grid(row=7, column=1, sticky='ew', padx=10, pady=10)

# scrollbars
scrollbar = tk.Scrollbar(frame)
answer_text = tk.Text(frame, width=70, height=15, wrap="word", yscrollcommand=scrollbar.set)
answer_text.grid(row=8, column=1, sticky='ew', padx=10)
scrollbar.grid(row=8, column=2, sticky='ns')

def submit():
    url = url_entry.get()
    question = question_entry.get()

    if url and question:
        root.after(0, progress_bar.grid, {"row": 6, "column": 1, "pady": 10})
        root.after(0, progress_bar.start, 10)  # 10 is the speed of the progress bar

        answer = gpt_functions.ask_question_from_gui(url, question)

        # Schedule the progress bar to stop and be removed on the main thread
        root.after(0, progress_bar.stop)
        root.after(0, progress_bar.grid_remove)

        # Schedule the new answer to be inserted on the main thread
        if answer:
            root.after(0, answer_text.insert, tk.END, answer)
    else:
        root.after(0, messagebox.showwarning, "Warning", "Please enter a URL and a question.")

# run in additional thread 
def submit_thread():
    thread = threading.Thread(target=submit)
    thread.start()

# Assigning command to submit button here to avoid 'submit' function being undefined
submit_button.config(command=submit_thread)

# run GUI
root.mainloop()