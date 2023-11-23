import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt

'''проверка работы с гитхаб'''

def validate_date(date_str):
    """Проверяет, соответствует ли строка формату dd.mm.yyyy."""
    try:
        datetime.strptime(date_str, '%d.%m.%Y')
        return True
    except ValueError:
        return False

def exit_app():
    """Закрыть все соединения с базой данных и завершить приложение."""
    connection.close()
    root.quit()

def create_table():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    connection.commit()

def add_task_to_db(date, description, status):
    cursor.execute("INSERT INTO tasks (date, description, status) VALUES (?, ?, ?)", (date, description, status))
    connection.commit()

def update_task_in_db(task_id, date, description, status):
    cursor.execute("UPDATE tasks SET date = ?, description = ?, status = ? WHERE id = ?", (date, description, status, task_id))
    connection.commit()

def delete_task_from_db(task_id):
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    connection.commit()

def get_all_tasks_from_db():
    cursor.execute("SELECT * FROM tasks")
    return cursor.fetchall()

def filter_tasks_from_db(date=None, status=None):
    if date and status:
        cursor.execute("SELECT * FROM tasks WHERE date = ? AND status = ?", (date, status))
    elif date:
        cursor.execute("SELECT * FROM tasks WHERE date = ?", (date,))
    elif status:
        cursor.execute("SELECT * FROM tasks WHERE status = ?", (status,))
    else:
        return []

    return cursor.fetchall()

def filter_tasks():
    date = date_search_bar.get()
    status = status_search_bar.get()
    tasks = filter_tasks_from_db(date, status)
    refresh_listbox(tasks)


# ===============================================================================================
def analyze():
    # Берем две даты
    start_date = simpledialog.askstring("Начальную дату", "Введите начальную дату dd.mm.yyyy:")
    end_date = simpledialog.askstring("Конечную дату", "Введите конечную дату dd.mm.yyyy:")

    if not start_date or not end_date:
        return

    # строки дат =>> объекты datetime
    start_date = datetime.strptime(start_date, '%d.%m.%Y')
    end_date = datetime.strptime(end_date, '%d.%m.%Y')

    # два списка  хранения дней и ко-во задач
    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    task_counts = [0] * 7  # Создаем список из 7 нулей
    not_completed_task_counts = [0] * 7  # Создаем список из 7 нулей для не выполненных задач

    tasks = filter_tasks_from_db(date=None, status='да')  # Забрал задачи в диапазоне дат и статус  "да"
    for task in tasks:
        task_date = datetime.strptime(task[1], '%d.%m.%Y')
        if start_date <= task_date <= end_date:
            day_of_week = task_date.weekday()  # 0 - Пн, 1 - Вт, 7 - вс
            task_counts[day_of_week] += 1

    tasks = filter_tasks_from_db(date=None, status='нет')  # Забрал задачи в диапазоне дат и статус  "нет"
    for task in tasks:
        task_date = datetime.strptime(task[1], '%d.%m.%Y')
        if start_date <= task_date <= end_date:
            day_of_week = task_date.weekday()  # 0 - Пн, 1 - Вт, 7 - вс
            not_completed_task_counts[day_of_week] += 1

    x = [0, 1, 2, 3, 4, 5, 6]

    # Рисуем выполненные задачи с синим цветом
    plt.bar(x, task_counts, width=0.2, color='blue', label='Сделал')

    # Рисуем не выполненные красным
    plt.bar(x, not_completed_task_counts, width=0.2, color='red', label='Не сделал', align='edge')

    plt.xlabel('День недели')
    plt.ylabel('Количество задач')
    plt.title('Анализ выполнения по дням')
    plt.xticks(x, weekdays)  # Устанавливаем подписи оси X как дни недели
    plt.legend()  # Добавляем легенду

    plt.show()


# =====================================================================================================
def refresh_listbox(tasks=None):
    task_listbox.delete(0, tk.END)  # Очищаем список перед обновлением

    if not tasks:
        tasks = get_all_tasks_from_db()

    # Определение фиксированных ширин для каждой колонки
    id_width = 8
    date_width = 15
    description_width = 85
    status_width = 10

    for task in tasks:
        task_id, date, description, status = task
        # Вставка данных с фиксированными ширинами колонок
        task_listbox.insert(tk.END, f"{str(task_id).rjust(id_width)} {date.center(date_width)} {description.center(description_width)} {status.center(status_width)}")

def create_task():
    new_win = tk.Toplevel(root)
    new_win.title("Создать задачу")
    new_win.geometry("450x200")

    ttk.Label(new_win, text="Дата:").place(x=10, y=10)
    date_entry = ttk.Entry(new_win, width=10)  # ширина поля дата

    date_entry.place(x=100, y=10)

    ttk.Label(new_win, text="Описание:").place(x=10, y=40)
    description_entry = ttk.Entry(new_win, width=50)  # ширина поля описание задачи
    description_entry.place(x=100, y=40)

    ttk.Label(new_win, text="Статус:да/нет", width=15).place(x=10, y=70)
    status_default_value = tk.StringVar(value="нет")  # Установка значения по умолчанию
    status_entry = ttk.Entry(new_win, textvariable=status_default_value)
    status_entry.place(x=100, y=70)

    def set_current_date(event):
        today = datetime.now().strftime("%d.%m.%Y")
        date_entry.delete(0, tk.END)
        date_entry.insert(0, today)

    date_entry.bind("<ButtonRelease-1>", set_current_date)


    def save_data():
        date = date_entry.get()
        description = description_entry.get()
        status = status_entry.get()
        if not validate_date(date):
            messagebox.showwarning("Предупреждение", "Введите корректную дату в формате dd.mm.yyyy.")
            return
        add_task_to_db(date, description, status)
        refresh_listbox()
        new_win.destroy()

    ttk.Button(new_win, text="Сохранить", command=save_data).place(x=10, y=100)

def edit_task():
    edit_win = tk.Toplevel(root)
    edit_win.title("Редактировать задачу")
    edit_win.geometry("450x200")

    ttk.Label(edit_win, text="ID записи:", width=15).place(x=10, y=10)
    id_entry = ttk.Entry(edit_win, width=10)
    id_entry.place(x=100, y=10)

    ttk.Label(edit_win, text="Дата:").place(x=10, y=40)
    date_entry = ttk.Entry(edit_win, width=10)
    date_entry.place(x=100, y=40)

    ttk.Label(edit_win, text="Описание:").place(x=10, y=70)
    description_entry = ttk.Entry(edit_win, width=50)
    description_entry.place(x=100, y=70)

    ttk.Label(edit_win, text="Статус: да/нет").place(x=10, y=100)
    status_entry = ttk.Entry(edit_win, width=10)
    status_entry.place(x=100, y=100)

    def get_task_data():
        task_id = id_entry.get()
        if not task_id.isdigit():
            messagebox.showwarning("Предупреждение", "ID записи должен быть числом.")
            return
        task_id = int(task_id)
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task_data = cursor.fetchone()
        if not task_data:
            messagebox.showerror("Ошибка", "Задача с указанным ID не найдена.")
            return
        _, date, description, status = task_data
        date_entry.delete(0, tk.END)
        date_entry.insert(0, date)
        description_entry.delete(0, tk.END)
        description_entry.insert(0, description)
        status_entry.delete(0, tk.END)
        status_entry.insert(0, status)

    ttk.Button(edit_win, text="Получить данные", command=get_task_data).place(x=10, y=130)

    def save_edited_data():
        task_id = id_entry.get()
        if not task_id.isdigit():
            messagebox.showwarning("Предупреждение", "ID записи должен быть числом.")
            return
        task_id = int(task_id)
        date = date_entry.get()
        description = description_entry.get()
        status = status_entry.get()
        if not validate_date(date):
            messagebox.showwarning("Предупреждение", "Введите корректную дату в формате dd.mm.yyyy.")
            return
        update_task_in_db(task_id, date, description, status)
        refresh_listbox()
        edit_win.destroy()

    ttk.Button(edit_win, text="Сохранить", command=save_edited_data).place(x=10, y=160)

def delete_task():
    delete_win = tk.Toplevel(root)
    delete_win.title("Удалить задачу")
    delete_win.geometry("200x200")

    ttk.Label(delete_win, text="ID записи:", width=15).place(x=10, y=10)
    id_entry = ttk.Entry(delete_win, width=10)
    id_entry.place(x=100, y=10)





    def delete_task_data():
        task_id = id_entry.get()
        if not task_id.isdigit():
            messagebox.showwarning("Предупреждение", "ID записи должен быть числом.")
            return
        task_id = int(task_id)
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task_data = cursor.fetchone()
        if not task_data:
            messagebox.showerror("Ошибка", "Задача с указанным ID не найдена.")
            return
        _, date, description, status = task_data
        delete_task_from_db(task_id)
        refresh_listbox()
        delete_win.destroy()

    ttk.Button(delete_win, text="Удалить", command=delete_task_data).place(x=10, y=80)

def sort_by_id():
    def id_key(task):
        return task[0]  # Сортировка по ID

    tasks = get_all_tasks_from_db()
    sorted_tasks = sorted(tasks, key=id_key)
    refresh_listbox(sorted_tasks)

def sort_by_date():
    def date_key(task):
        return datetime.strptime(task[1], '%d.%m.%Y')  # Сортировка по Дате

    tasks = get_all_tasks_from_db()
    sorted_tasks = sorted(tasks, key=date_key)
    refresh_listbox(sorted_tasks)

def sort_by_status():
    def status_key(task):
        return task[3]  # Сортировка по Статусу

    tasks = get_all_tasks_from_db()
    sorted_tasks = sorted(tasks, key=status_key)
    refresh_listbox(sorted_tasks)

root = tk.Tk()
root.title("Ежедневник 1.0")
root.geometry("550x400")

connection = sqlite3.connect('planner.db')
cursor = connection.cursor()

ttk.Label(root, text="Дата:").place(x=10, y=10)
date_search_bar = ttk.Entry(root, width=10)
date_search_bar.place(x=100, y=10)

ttk.Label(root, text="Статус: да/нет").place(x=10, y=40)
status_search_bar = ttk.Entry(root, width=20)
status_search_bar.place(x=100, y=40)

all_lists_button = tk.Button(root, text="Сброс фильтра!", width=15, command=refresh_listbox, bg='green', fg='white')
all_lists_button.place(x=300, y=40)

filter_button = tk.Button(root, text="Фильтр!", width=15, command=filter_tasks, bg='green', fg='white')
filter_button.place(x=300, y=10)

study_button = tk.Button(root,  command=analyze   , text="Анализ успехов!", width=15, bg='red', fg='white')  #
study_button.place(x=420, y=10)


task_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=80, height=10)
task_listbox.place(x=10, y=100)

create_table()

tasks = get_all_tasks_from_db()
refresh_listbox(tasks)

create_button = tk.Button(root, text="СОЗДАТЬ", width=15, bg='green', fg='white', command=create_task)
create_button.place(x=10, y=350)

edit_button = tk.Button(root, text="РЕДАКТОР", width=15, bg='red', fg='white', command=edit_task)
edit_button.place(x=130, y=350)

delete_button = tk.Button(root, text="УДАЛИТЬ", width=15, bg='red', fg='white', command=delete_task)
delete_button.place(x=250, y=350)

exit_button = tk.Button(root, text="ВЫЙТИ", width=15, bg='green', fg='white', command=exit_app)
exit_button.place(x=370, y=350)

sort_id_button = tk.Button(root, text="id", width=3, command=sort_by_id)
sort_id_button.place(x=10, y=70)

sort_date_button = tk.Button(root, text="Дата", width=10, command=sort_by_date)
sort_date_button.place(x=40, y=70)

sort_date_button = tk.Button(root, text="Описание", width=40)
sort_date_button.place(x=110, y=70)

sort_status_button = tk.Button(root, text="Статус", width=10, command=sort_by_status)
sort_status_button.place(x=400, y=70)

root.mainloop()
