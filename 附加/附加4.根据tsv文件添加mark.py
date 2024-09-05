import pandas as pd
import numpy as np
import mne
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def 加载TSV文件():
    global tsv_data_list
    tsv_paths = filedialog.askopenfilenames(title="选择TSV文件", filetypes=[("TSV文件", "*.tsv")])
    if tsv_paths:
        tsv_data_list = [pd.read_csv(path, sep='\t') for path in tsv_paths]
        for path in tsv_paths:
            tsv_listbox.insert(tk.END, f"已加载TSV文件: {path}")

def 加载FIF文件():
    global raw_list
    fif_paths = filedialog.askopenfilenames(title="选择FIF文件", filetypes=[("FIF文件", "*.fif")])
    if fif_paths:
        raw_list = [mne.io.read_raw_fif(path, preload=True) for path in fif_paths]
        for path in fif_paths:
            fif_listbox.insert(tk.END, f"已加载FIF文件: {path}")

def 选择保存地址():
    global save_dir
    save_dir = filedialog.askdirectory(title="选择保存地址")
    if save_dir:
        save_dir_label.config(text=f"保存地址: {save_dir}")

import os

def 处理文件():
    if 'tsv_data_list' not in globals() or 'raw_list' not in globals() or 'save_dir' not in globals():
        messagebox.showerror("错误", "请先加载TSV和FIF文件并选择保存地址。")
        return

    for tsv_data, raw in zip(tsv_data_list, raw_list):
        tsv_data['onset'] = tsv_data['onset'] / 1000.0
        tsv_data['duration'] = tsv_data['duration'] / 1000.0

        events = []
        for index, row in tsv_data.iterrows():
            onset = int(row['onset'] * raw.info['sfreq'])
            duration = int(row['duration'] * raw.info['sfreq'])
            events.append([onset, 0, duration])

        events = np.array(events)
        descriptions = ['event_{}'.format(i) for i in range(len(events))]
        annot = mne.Annotations(onset=events[:, 0] / raw.info['sfreq'],
                                duration=events[:, 2] / raw.info['sfreq'],
                                description=descriptions)
        raw.set_annotations(annot)

        # 获取原始文件名并添加标记
        original_filename = os.path.basename(raw.filenames[0])
        new_filename = f"{os.path.splitext(original_filename)[0]}_marked.fif"
        save_path = os.path.join(save_dir, new_filename)
        raw.save(save_path, overwrite=True)

    messagebox.showinfo("成功", "已成功保存修改后的FIF文件。")

# 创建主窗口
root = tk.Tk()
root.title("EEG数据加载器")

# 创建列表框
tsv_listbox = tk.Listbox(root, width=100, height=10)
tsv_listbox.pack(pady=10)

fif_listbox = tk.Listbox(root, width=100, height=10)
fif_listbox.pack(pady=10)

# 创建按钮
加载TSV按钮 = tk.Button(root, text="加载TSV文件", command=加载TSV文件)
加载TSV按钮.pack(side=tk.LEFT, padx=10)

加载FIF按钮 = tk.Button(root, text="加载FIF文件", command=加载FIF文件)
加载FIF按钮.pack(side=tk.LEFT, padx=10)

选择保存地址按钮 = tk.Button(root, text="选择保存地址", command=选择保存地址)
选择保存地址按钮.pack(side=tk.LEFT, padx=10)

处理文件按钮 = tk.Button(root, text="处理文件", command=处理文件)
处理文件按钮.pack(side=tk.LEFT, padx=10)

# 显示保存地址的标签
save_dir_label = tk.Label(root, text="保存地址: 未选择")
save_dir_label.pack(pady=10)

# 运行主循环
root.mainloop()