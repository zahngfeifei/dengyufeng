import tkinter as tk
from tkinter import filedialog, messagebox
import mne
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

class EEGViewer:
    def __init__(self, master):
        self.master = master
        master.title("EEG数据查看器")

        # 创建一个Frame来放置按钮
        button_frame = tk.Frame(master)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        self.label = tk.Label(master, text="选择EEG数据文件 (.fif)")
        self.label.pack()

        self.open_button = tk.Button(button_frame, text="打开文件", command=self.open_files)
        self.open_button.pack(side=tk.LEFT, padx=5)

        self.plot_button = tk.Button(button_frame, text="绘制数据", command=self.plot_data)
        self.plot_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(button_frame, text="保存数据", command=self.save_data)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # 创建一个Frame来放置Listbox和删除按钮
        listbox_frame = tk.Frame(master)
        listbox_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.channels_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE)
        self.channels_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.channels_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.channels_listbox.config(yscrollcommand=scrollbar.set)

        self.delete_button = tk.Button(master, text="删除选中通道", command=self.delete_channels)
        self.delete_button.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.raw_list = []
        self.file_paths = []

    def open_files(self):
        self.file_paths = filedialog.askopenfilenames(filetypes=[("FIF files", "*.fif")])
        if self.file_paths:
            self.load_data(self.file_paths)

    def load_data(self, file_paths):
        self.raw_list = [mne.io.read_raw_fif(file_path, preload=True) for file_path in file_paths]
        if self.raw_list:
            self.display_channel_names(self.raw_list[0].ch_names)  # 显示第一个文件的通道名称

    def display_channel_names(self, channel_names):
        self.channels_listbox.delete(0, tk.END)
        for name in channel_names:
            self.channels_listbox.insert(tk.END, name)

    def delete_channels(self):
        selected_indices = self.channels_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("未选中", "没有选中任何通道进行删除。")
            return

        selected_channels = [self.channels_listbox.get(i) for i in selected_indices]
        for raw in self.raw_list:
            raw.drop_channels(selected_channels)
        if self.raw_list:
            self.display_channel_names(self.raw_list[0].ch_names)  # 更新通道名称

    def plot_data(self):
        if self.raw_list:
            for raw in self.raw_list:
                raw.plot(duration=10, n_channels=len(raw.ch_names))
            plt.show(block=True)
        else:
            messagebox.showwarning("无数据", "没有加载数据进行绘制。")

    def save_data(self):
        if self.raw_list:
            save_directory = filedialog.askdirectory()
            if save_directory:
                for raw, file_path in zip(self.raw_list, self.file_paths):
                    original_filename = os.path.basename(file_path)
                    save_filename = f"{os.path.splitext(original_filename)[0]}_tichu.fif"
                    save_path = os.path.join(save_directory, save_filename)
                    raw.save(save_path, overwrite=True)
                messagebox.showinfo("保存成功", f"数据已保存到 {save_directory}")
        else:
            messagebox.showwarning("无数据", "没有加载数据进行保存。")

if __name__ == "__main__":
    root = tk.Tk()
    app = EEGViewer(root)
    root.mainloop()
