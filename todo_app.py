import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

TASKS_FILE = "tasks.json"

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r") as f:
                self.tasks = json.load(f)

    def save_tasks(self):
        with open(TASKS_FILE, "w") as f:
            json.dump(self.tasks, f, indent=4)

    def add_task(self, title, description, category):
        task = {"title": title, "description": description, "category": category, "completed": False}
        self.tasks.append(task)
        self.save_tasks()

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.save_tasks()

    def toggle_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index]["completed"] = not self.tasks[index]["completed"]
            self.save_tasks()


class TodoApp:
    def __init__(self, root):
        self.manager = TaskManager()
        self.root = root
        self.root.title("To-Do List Application")
        self.root.geometry("650x450")

        # Track currently filtered tasks
        self.filtered_indices = []

        # Task input
        frame = tk.Frame(root)
        frame.pack(pady=10)

        tk.Label(frame, text="Title:").grid(row=0, column=0)
        self.title_entry = tk.Entry(frame)
        self.title_entry.grid(row=0, column=1)

        tk.Label(frame, text="Description:").grid(row=1, column=0)
        self.desc_entry = tk.Entry(frame)
        self.desc_entry.grid(row=1, column=1)

        tk.Label(frame, text="Category:").grid(row=2, column=0)
        self.cat_entry = tk.Entry(frame)
        self.cat_entry.grid(row=2, column=1)

        tk.Button(frame, text="Add Task", command=self.add_task).grid(row=3, columnspan=2, pady=5)

        # Search + Filter
        filter_frame = tk.Frame(root)
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Search:").grid(row=0, column=0)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(filter_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1)
        self.search_entry.bind("<Return>", lambda e: self.on_search())

        tk.Button(filter_frame, text="Search", command=self.on_search).grid(row=0, column=2, padx=5)

        tk.Label(filter_frame, text="Category:").grid(row=0, column=3)
        self.cat_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(filter_frame, textvariable=self.cat_var, values=["All"], state="readonly")
        self.cat_combo.grid(row=0, column=4)
        self.cat_combo.current(0)

        tk.Button(filter_frame, text="Apply Filter", command=self.apply_filters).grid(row=0, column=5, padx=5)
        tk.Button(filter_frame, text="Clear Filter", command=self.clear_filters).grid(row=0, column=6, padx=5)

        # Task list
        self.task_listbox = tk.Listbox(root, width=80)
        self.task_listbox.pack(pady=10)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack()

        tk.Button(btn_frame, text="Toggle Completed", command=self.toggle_task).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="View Details", command=self.view_task_details).grid(row=0, column=2, padx=5)

        self.update_task_list()

    def add_task(self):
        title = self.title_entry.get()
        desc = self.desc_entry.get()
        cat = self.cat_entry.get()

        if not title:
            messagebox.showwarning("Input Error", "Task title is required")
            return

        self.manager.add_task(title, desc, cat if cat else "General")
        self.update_task_list()

        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.cat_entry.delete(0, tk.END)

    def update_task_list(self, filtered_tasks=None):
        self.task_listbox.delete(0, tk.END)
        tasks = filtered_tasks if filtered_tasks is not None else self.manager.tasks
        self.filtered_indices = []

        categories = set(["All"])
        for i, task in enumerate(tasks):
            status = "✓" if task["completed"] else "✗"
            display_text = f"{i+1}. [{status}] {task['title']} ({task['category']})"
            self.task_listbox.insert(tk.END, display_text)
            categories.add(task["category"])

            # Keep track of original task index
            if filtered_tasks is not None:
                self.filtered_indices.append(self.manager.tasks.index(task))

        self.cat_combo["values"] = list(categories)

    def delete_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("Selection Error", "No task selected")
            return
        index = self.filtered_indices[selected[0]] if self.filtered_indices else selected[0]
        self.manager.delete_task(index)
        self.apply_filters()

    def toggle_task(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("Selection Error", "No task selected")
            return
        index = self.filtered_indices[selected[0]] if self.filtered_indices else selected[0]
        self.manager.toggle_task(index)
        self.apply_filters()

    def view_task_details(self):
        selected = self.task_listbox.curselection()
        if not selected:
            messagebox.showwarning("Selection Error", "No task selected")
            return
        index = self.filtered_indices[selected[0]] if self.filtered_indices else selected[0]
        task = self.manager.tasks[index]

        details = f"Title: {task['title']}\n"
        details += f"Description: {task['description']}\n"
        details += f"Category: {task['category']}\n"
        details += f"Completed: {'Yes' if task['completed'] else 'No'}"

        messagebox.showinfo("Task Details", details)

    def apply_filters(self):
        search_text = self.search_var.get().lower()
        category = self.cat_var.get()

        filtered = [
            task for task in self.manager.tasks
            if (search_text in task["title"].lower() or search_text in task["description"].lower())
            and (category == "All" or task["category"] == category)
        ]
        self.update_task_list(filtered)

    def clear_filters(self):
        self.search_var.set("")
        self.cat_var.set("All")
        self.apply_filters()

    def on_search(self):
        self.apply_filters()


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
