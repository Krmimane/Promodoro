import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import ttk, Style
from PIL import Image, ImageTk
import requests
from io import BytesIO
import sqlite3

WORK_TIME = 25 * 60
SHORT_BREAK_TIME = 5 * 60
LONG_BREAK_TIME = 15 * 60

class CombinedApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("950x700")
        self.root.title("Motivation Booster")

        # Styles
        self.style = Style(theme="minty")
        self.style.theme_use()

        # To-Do List Frame
        self.todo_frame = tk.Frame(self.root, bg="#a5d6a7")
        self.todo_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.todo_frame, text="To-Do List", font=("Helvetica", 16, "bold"), bg="#a5d6a7").pack(pady=10)

        self.conn = sqlite3.connect("tasks.db")
        self.c = self.conn.cursor()
        self.create_tasks_table()

        self.tasks = []
        self.task_entry = tk.Entry(self.todo_frame, width=30, bg="#a5d6a7")  # Set background color
        self.task_entry.pack(pady=5)

        tk.Button(self.todo_frame, text="Add Task", command=self.add_task, bg="#66bb6a", fg="white").pack(pady=5)

        tk.Button(self.todo_frame, text="Remove Task", command=self.remove_task, bg="#ef5350", fg="white").pack(pady=5)

        self.todo_listbox = tk.Listbox(self.todo_frame, selectmode=tk.SINGLE, height=10, bg="#a5d6a7")  # Set background color
        self.todo_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

        self.populate_todo_list()

        # Note and Inspiration Frame
        self.note_inspiration_frame = tk.Frame(self.root, bg="#ffc107")
        self.note_inspiration_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Note Widget Frame
        self.note_frame = tk.Frame(self.note_inspiration_frame, bg="#ffc107")
        self.note_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.note_frame, text="Notes", font=("Helvetica", 16, "bold"), bg="#ffc107").pack(pady=10)

        # Note entry takes the entire frame
        self.note_entry = tk.Text(self.note_frame, wrap=tk.WORD, bg="#ffc107")
        self.note_entry.pack(pady=5, fill=tk.BOTH, expand=True)


        # Inspiration Frame
        self.inspiration_frame = tk.Frame(self.note_inspiration_frame, bg="#81d4fa")
        self.inspiration_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.inspiration_frame, text="Inspiration", font=("Helvetica", 16, "bold"), bg="#81d4fa").pack(pady=10)

        self.inspiration_label = tk.Label(self.inspiration_frame, text="", font=("Helvetica", 12), bg="#81d4fa", wraplength=300, justify=tk.CENTER)
        self.inspiration_label.pack(pady=20)

        tk.Button(self.inspiration_frame, text="Get Inspiration", command=self.get_inspiration, bg="#29b6f6", fg="white").pack(pady=5)

        # Pomodoro Timer Frame
        self.timer_frame = tk.Frame(self.root, bg="#81c784")
        self.timer_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)

        tk.Label(self.timer_frame, text="Pomodoro Timer", font=("Helvetica", 16, "bold"), bg="#81c784").pack(pady=10)

        self.timer_label = tk.Label(self.timer_frame, text="", font=("TkDefaultFont", 20), bg="#81c784")
        self.timer_label.pack(pady=20)

        ttk.Button(self.timer_frame, text="Start Timer", command=self.start_timer, style="success.TButton").pack(pady=5)

        ttk.Button(self.timer_frame, text="Stop Timer", command=self.stop_timer, style="danger.TButton", state=tk.DISABLED).pack(pady=5)

        self.work_time, self.break_time = WORK_TIME, SHORT_BREAK_TIME
        self.is_work_time, self.pomodoros_completed, self.is_running = True, 0, False

        # Set background image
        self.root.configure(bg='#a5d6a7')
        self.root.mainloop()
    def start_timer(self):
        self.timer_frame.children["!button"].config(state=tk.DISABLED)
        self.timer_frame.children["!button2"].config(state=tk.NORMAL)
        self.is_running = True
        self.update_timer()

    def stop_timer(self):
        self.timer_frame.children["!button"].config(state=tk.NORMAL)
        self.timer_frame.children["!button2"].config(state=tk.DISABLED)
        self.is_running = False

    def update_timer(self):
        if self.is_running:
            if self.is_work_time:
                self.work_time -= 1
                if self.work_time == 0:
                    self.is_work_time = False
                    self.pomodoros_completed += 1
                    self.break_time = LONG_BREAK_TIME if self.pomodoros_completed % 4 == 0 else SHORT_BREAK_TIME
                    messagebox.showinfo("Pomodoro Completed!", "Take a break!")
            else:
                self.break_time -= 1
                if self.break_time == 0:
                    self.is_work_time, self.work_time = True, WORK_TIME
                    messagebox.showinfo("Break Time Over!", "Get back to work!")
            minutes, seconds = divmod(self.work_time if self.is_work_time else self.break_time, 60)
            self.timer_label.config(text="{:02d}:{:02d}".format(minutes, seconds))
            self.root.after(1000, self.update_timer)

    def add_task(self):
        task = self.task_entry.get()
        if task:
            self.c.execute("INSERT INTO tasks (name) VALUES (?)", (task,))
            self.conn.commit()
            self.populate_todo_list()
            self.task_entry.delete(0, tk.END)

    def remove_task(self):
        selected_index = self.todo_listbox.curselection()
        if selected_index:
            task_id = self.tasks[selected_index[0]][0]
            self.c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            self.conn.commit()
            self.populate_todo_list()

    def populate_todo_list(self):
        self.todo_listbox.delete(0, tk.END)
        self.tasks = self.c.execute("SELECT * FROM tasks").fetchall()
        for task in self.tasks:
            task_text = f"[{'x' if task[3] else ' '}] {task[1]}"
            self.todo_listbox.insert(tk.END, task_text)

    def create_tasks_table(self):
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                completed INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()



    def add_note(self):
        note = self.note_entry.get("1.0", tk.END).strip()  # Get text from Text widget
        if note:
            # For simplicity, we won't save notes to a database in this example
            self.note_listbox.insert(tk.END, note)
            self.note_entry.delete("1.0", tk.END)  # Clear text in Text widget

    def get_inspiration(self):
        response = requests.get("https://api.quotable.io/random")
        if response.status_code == 200:
            data = response.json()
            quote = data.get("content", "")
            author = data.get("author", "")
            self.inspiration_label.config(text=f'"{quote}"\n\n- {author}')
        else:
            self.inspiration_label.config(text="Failed to fetch inspiration.")

app=CombinedApp()