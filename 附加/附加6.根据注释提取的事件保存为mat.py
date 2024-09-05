import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import Listbox
import mne
import scipy.io
import numpy as np
import os


class EEGDataProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("EEG 数据处理工具")
        self.file_paths = []

        # 创建并放置选择文件按钮
        self.select_files_button = tk.Button(root, text="选择 EEG 数据文件", command=self.select_files)
        self.select_files_button.pack(pady=10)

        # 创建并放置 Listbox 用于显示加载的数据文件
        self.file_listbox = Listbox(root, width=50, height=10)
        self.file_listbox.pack(pady=10)

        # 创建并放置自定义保存路径按钮
        self.save_path_button = tk.Button(root, text="选择保存目录", command=self.select_save_directory)
        self.save_path_button.pack(pady=10)

        # 创建并放置处理数据按钮
        self.process_button = tk.Button(root, text="处理数据", command=self.process_data)
        self.process_button.pack(pady=10)

    def select_files(self):
        # 打开文件对话框以选择多个文件
        self.file_paths = filedialog.askopenfilenames(filetypes=[("FIF files", "*.fif")])
        # 清空 Listbox
        self.file_listbox.delete(0, tk.END)
        # 将选中的文件路径添加到 Listbox
        for file_path in self.file_paths:
            self.file_listbox.insert(tk.END, file_path)

    def select_save_directory(self):
        # 打开目录对话框以选择保存目录
        self.save_directory = filedialog.askdirectory()
        if not self.save_directory:
            messagebox.showwarning("警告", "未选择保存目录!")

    def process_data(self):
        if not self.file_paths:
            messagebox.showwarning("警告", "未选择数据文件!")
            return

        if not hasattr(self, 'save_directory'):
            messagebox.showwarning("警告", "未选择保存目录!")
            return

        try:
            # 处理每个文件
            for file_path in self.file_paths:
                # 读取 .fif 文件
                raw = mne.io.read_raw_fif(file_path, preload=True)
                # 获取注释
                annotations = raw.annotations
                if len(annotations.duration) == 0:
                    raise ValueError("注释数据为空，请检查 .fif 文件的注释内容。")
                # 将注释转换为事件
                events, event_id = mne.events_from_annotations(raw)
                # 获取通道数
                n_channels = raw.info['nchan']
                # 获取采样频率
                sfreq = raw.info['sfreq']
                # 初始化一个空数组来存储重构后的数据
                n_trials = len(events)
                max_samples_per_trial = int(max(annotations.duration) * sfreq)  # 最大采样点数
                reconstructed_data = np.zeros((n_channels, max_samples_per_trial, n_trials))
                # 重构数据
                for trial_idx, event in enumerate(events):
                    # 获取事件的时间戳
                    event_time = event[0]
                    # 获取对应注释的持续时间
                    annotation_duration = annotations.duration[trial_idx]
                    # 计算采样点数
                    n_samples_per_trial = int(annotation_duration * sfreq)
                    # 获取事件开始和结束的样本索引
                    start_sample = event_time
                    end_sample = start_sample + n_samples_per_trial
                    # 提取数据
                    trial_data = raw[:, start_sample:end_sample][0]
                    # 将数据存储到重构数组中
                    reconstructed_data[:, :n_samples_per_trial, trial_idx] = trial_data

                # 构建保存文件的完整路径
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                save_path = os.path.join(self.save_directory, f"{base_name}_events.mat")

                # 保存为 .mat 文件
                scipy.io.savemat(save_path, {'events_data': reconstructed_data, 'event_id': event_id})

            messagebox.showinfo("完成", "数据处理和保存成功!")
        except Exception as e:
            messagebox.showerror("错误", f"数据处理时出现错误: {e}")


# 创建主窗口
root = tk.Tk()
app = EEGDataProcessor(root)
root.mainloop()
