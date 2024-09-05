import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, Scrollbar, Entry, Button
import mne
import scipy.io
import os

class EEGDataProcessor:
    def __init__(self, master):
        self.master = master
        master.title("EEG 数据处理器")

        # Frame for file list
        self.list_frame = tk.Frame(master)
        self.list_frame.pack(pady=10)

        self.file_listbox = Listbox(self.list_frame, width=50, height=10)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        self.scrollbar = Scrollbar(self.list_frame, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.file_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox.config(yscrollcommand=self.scrollbar.set)

        # Frame for buttons and save path entry
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        self.save_path_label = tk.Label(self.button_frame, text="保存路径:")
        self.save_path_label.pack(side=tk.LEFT, padx=5)

        self.save_path_entry = Entry(self.button_frame, width=40)
        self.save_path_entry.pack(side=tk.LEFT, padx=5)

        self.load_button = tk.Button(self.button_frame, text="加载文件", command=self.load_files)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.process_button = tk.Button(self.button_frame, text="处理文件", command=self.process_files)
        self.process_button.pack(side=tk.LEFT, padx=5)

    def load_files(self):
        file_paths = filedialog.askopenfilenames(title="选择 EEG FIF 文件", filetypes=[("FIF 文件", "*.fif")])
        for file_path in file_paths:
            self.file_listbox.insert(tk.END, file_path)

    def process_files(self):
        selected_files = self.file_listbox.get(0, tk.END)
        save_path = self.save_path_entry.get()

        if not selected_files:
            messagebox.showwarning("无文件", "没有选择要处理的文件。")
            return

        if not save_path:
            messagebox.showwarning("无保存路径", "请输入保存路径。")
            return

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        for file_path in selected_files:
            try:
                raw = mne.io.read_raw_fif(file_path, preload=True)
                data, _ = raw[:]
                mat_data = {'data': data}
                mat_file = os.path.join(save_path, os.path.basename(os.path.splitext(file_path)[0]) + '.mat')
                scipy.io.savemat(mat_file, mat_data)
                print(f"已处理并保存 {mat_file}")
            except Exception as e:
                messagebox.showerror("处理错误", f"处理 {file_path} 时出错: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EEGDataProcessor(root)
    root.mainloop()