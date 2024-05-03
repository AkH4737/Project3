import psutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime

# Словарь для хранения времени запуска каждого процесса
process_start_time = {}

def get_running_processes():
    running_processes = []
    for process in psutil.process_iter(['pid', 'cmdline', 'create_time']):
        pid = process.info['pid']
        cmdline = ' '.join(process.info['cmdline']) if process.info['cmdline'] is not None else 'N/A'
        create_time = datetime.fromtimestamp(process.info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
        running_processes.append((pid, cmdline, create_time, get_network_usage(pid)))
        # Сохраняем время запуска процесса
        process_start_time[pid] = process.info['create_time']
    return running_processes

def get_network_usage(pid):
    try:
        connections = psutil.Process(pid).connections()
        return ', '.join([
            f"{conn.laddr.ip if conn.laddr else 'N/A'}:{conn.laddr.port if conn.laddr else 'N/A'} -> {conn.raddr.ip if conn.raddr else 'N/A'}:{conn.raddr.port if conn.raddr else 'N/A'} ({conn.status})"
            for conn in connections
        ])
    except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError) as e:
        return 'N/A'

def update_process_list():
    process_list.delete(*process_list.get_children())
    for pid, cmdline, create_time, network_usage in get_running_processes():
        process_list.insert('', 'end', values=(pid, cmdline, create_time, calculate_running_time(pid), network_usage))

def calculate_running_time(pid):
    start_time = process_start_time.get(pid, None)
    if start_time is not None:
        current_time = datetime.now().timestamp()
        running_time = current_time - start_time
        return format_time(running_time)
    else:
        return 'N/A'

def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{int(hours)}:{int(minutes)}:{int(seconds)}"

def save_to_text():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        try:
            with open(file_path, 'w') as file:
                for pid, cmdline, create_time, _, network_usage in get_running_processes():
                    running_time = calculate_running_time(pid)
                    file.write(f"PID: {pid}, Команда: {cmdline}, Время создания: {create_time}, Время работы: {running_time}, Сетевая активность: {network_usage}\n")
        except Exception as e:
            print(f"Произошла ошибка при сохранении файла: {e}")

def clear_screen():
    process_list.delete(*process_list.get_children())

# Создание главного окна
root = tk.Tk()
root.title("Список запущенных процессов")

# Создание таблицы для отображения процессов
columns = ('PID', 'Команда', 'Время создания', 'Время работы', 'Сетевая активность')
process_list = ttk.Treeview(root, columns=columns, show='headings')
process_list.heading('PID', text='PID')
process_list.heading('Команда', text='Команда')
process_list.heading('Время создания', text='Время создания')
process_list.heading('Время работы', text='Время работы')
process_list.heading('Сетевая активность', text='Сетевая активность')
process_list.pack(fill='both', expand=True)

# Кнопка для обновления списка процессов
update_button = ttk.Button(root, text="Обновить список", command=update_process_list)
update_button.pack()

# Кнопка для сохранения списка процессов в текстовом формате
save_button = ttk.Button(root, text="Сохранить в текстовом формате", command=save_to_text)
save_button.pack()

# Кнопка для очистки экрана
clear_button = ttk.Button(root, text="Очистить экран", command=clear_screen)
clear_button.pack()

# Обновление списка процессов при запуске программы
update_process_list()

# Запуск главного цикла обработки событий
root.mainloop()
