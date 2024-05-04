import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from datetime import datetime
import psutil

class ProcessMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Монитор процессов")
        self.root.geometry("800x600")
        self.root.config(bg='lightblue')
        
        self.process_start_time = {}  # Словарь для хранения времени запуска каждого процесса

        self.create_widgets()

        self.style = ttk.Style()
        self.style.configure("Primary.TButton", foreground="blue", background="lightblue", font=("Helvetica", 12))
        self.style.configure("Secondary.TButton", foreground="green", background="lightgreen", font=("Helvetica", 12))
        self.style.configure("Tertiary.TButton", foreground="red", background="lightcoral", font=("Helvetica", 12))
        self.style.configure("Quaternary.TButton", foreground="purple", background="lightpurple", font=("Helvetica", 12))
        self.style.configure("TEntry", foreground="black", background="white")

    def create_widgets(self):
        # Создание таблицы для отображения процессов
        columns = ('PID', 'Команда', 'Время создания', 'Время работы', 'Сетевая активность')
        self.process_list = ttk.Treeview(self.root, columns=columns, show='headings')
        self.process_list.heading('PID', text='PID')
        self.process_list.heading('Команда', text='Команда')
        self.process_list.heading('Время создания', text='Время создания')
        self.process_list.heading('Время работы', text='Время работы')
        self.process_list.heading('Сетевая активность', text='Сетевая активность')
        self.process_list.pack(fill='both', expand=True)

        # Кнопка для обновления списка процессов
        self.update_button = ttk.Button(self.root, text="Обновить список", command=self.update_process_list, style="Primary.TButton")
        self.update_button.pack()

        # Кнопка для сохранения списка процессов в текстовом формате
        self.save_button = ttk.Button(self.root, text="Сохранить в текстовом формате", command=self.save_to_text, style="Secondary.TButton")
        self.save_button.pack()

        # Кнопка для очистки экрана
        self.clear_button = ttk.Button(self.root, text="Очистить экран", command=self.clear_screen, style="Tertiary.TButton")
        self.clear_button.pack()

    def get_running_processes(self):
        running_processes = []
        for process in psutil.process_iter(['pid', 'cmdline', 'create_time']):
            pid = process.info['pid']
            cmdline = ' '.join(process.info['cmdline']) if process.info['cmdline'] is not None else 'N/A'
            create_time = datetime.fromtimestamp(process.info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
            running_processes.append((pid, cmdline, create_time, self.get_network_usage(pid)))
            # Сохраняем время запуска процесса
            self.process_start_time[pid] = process.info['create_time']
        return running_processes

    def get_network_usage(self, pid):
        try:
            connections = psutil.Process(pid).connections()
            return ', '.join([
                f"{conn.laddr.ip if conn.laddr else 'N/A'}:{conn.laddr.port if conn.laddr else 'N/A'} -> {conn.raddr.ip if conn.raddr else 'N/A'}:{conn.raddr.port if conn.raddr else 'N/A'} ({conn.status})"
                for conn in connections
            ])
        except (psutil.AccessDenied, psutil.NoSuchProcess, AttributeError) as e:
            return 'N/A'

    def update_process_list(self):
        self.process_list.delete(*self.process_list.get_children())
        for pid, cmdline, create_time, network_usage in self.get_running_processes():
            self.process_list.insert('', 'end', values=(pid, cmdline, create_time, self.calculate_running_time(pid), network_usage))

    def calculate_running_time(self, pid):
        start_time = self.process_start_time.get(pid, None)
        if start_time is not None:
            current_time = datetime.now().timestamp()
            running_time = current_time - start_time
            return self.format_time(running_time)
        else:
            return 'N/A'

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{int(hours)}:{int(minutes)}:{int(seconds)}"

    def save_to_text(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    for pid, cmdline, create_time, _, network_usage in self.get_running_processes():
                        running_time = self.calculate_running_time(pid)
                        file.write(f"PID: {pid}, Команда: {cmdline}, Время создания: {create_time}, Время работы: {running_time}, Сетевая активность: {network_usage}\n")
            except Exception as e:
                print(f"Произошла ошибка при сохранении файла: {e}")

    def clear_screen(self):
        self.process_list.delete(*self.process_list.get_children())

# Создаем экземпляр класса и запускаем главный цикл обработки событий
root = tk.Tk()
app = ProcessMonitorApp(root)
root.mainloop()
