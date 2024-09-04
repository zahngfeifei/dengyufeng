import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, Listbox, SINGLE, MULTIPLE
import mne
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
from mne.preprocessing import ICA
from scipy.io import savemat

matplotlib.use('tkAgg')
from mne.datasets import eegbci
from mne.preprocessing import ICA
import numpy as np
import scipy.io as sio
import pandas as pd
"""
  * @author: dengyufeng
  * @Created on 2024/9/2 10：11
  * @Email: 3087178834@qq.com
 """
# 提取事件有标注
class AnnotationEventProcessor:
    def __init__(self, root, raw_list, file_names, save_path):
        self.root = root
        self.raw_list = raw_list
        self.file_names = file_names
        self.save_path = save_path
        self.root.geometry("1000x800")

        # 创建主框架
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建文件列表框框架
        file_list_frame = tk.Frame(main_frame)
        file_list_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5, pady=5)

        # 创建设置框架
        settings_frame = tk.Frame(main_frame)
        settings_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=5, pady=5)

        # 创建文件列表框，支持多选
        self.file_listbox = Listbox(file_list_frame, selectmode=MULTIPLE)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 填充文件列表框
        for file_name in self.file_names:
            self.file_listbox.insert(tk.END, os.path.basename(file_name))

        # 创建并放置按钮
        button_frame = tk.Frame(settings_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        self.process_button = tk.Button(button_frame, text="提取事件", command=self.process_data, state=tk.NORMAL)
        self.process_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_button = tk.Button(button_frame, text="保存文件", command=self.save_file, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.close_button = tk.Button(button_frame, text="关闭", command=self.close_app)
        self.close_button.pack(side=tk.LEFT, padx=5, pady=5)

        # 创建结果标签
        self.result_label = tk.Label(settings_frame, text="", wraplength=950)
        self.result_label.pack(fill=tk.X, padx=5, pady=5)

        # 创建一个框架用于组织tmin、tmax、基线、标注设置
        settings_inner_frame = tk.Frame(settings_frame)
        settings_inner_frame.pack(fill=tk.X, padx=5, pady=5)

        # tmin 和 tmax 输入框
        tk.Label(settings_inner_frame, text="tmin:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.tmin_entry = tk.Entry(settings_inner_frame)
        self.tmin_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(settings_inner_frame, text="tmax:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.tmax_entry = tk.Entry(settings_inner_frame)
        self.tmax_entry.grid(row=0, column=3, padx=5, pady=5)

        self.set_tmin_tmax_button = tk.Button(settings_inner_frame, text="设置 tmin 和 tmax",
                                              command=self.set_tmin_tmax)
        self.set_tmin_tmax_button.grid(row=0, column=4, padx=5, pady=5)

        # 基线设置输入框
        tk.Label(settings_inner_frame, text="基线 (格式: '开始时间 结束时间' 或 'None'):").grid(row=1, column=0, padx=5,
                                                                                                pady=5, sticky='e')
        self.baseline_entry = tk.Entry(settings_inner_frame)
        self.baseline_entry.grid(row=1, column=1, padx=5, pady=5, columnspan=3)

        self.set_baseline_button = tk.Button(settings_inner_frame, text="设置基线", command=self.set_baseline)
        self.set_baseline_button.grid(row=1, column=4, padx=5, pady=5)

        # 自定义标注输入框
        tk.Label(settings_inner_frame, text="自定义标注 (格式: '标注名=事件编号', 例如 'T1=1 T2=2'):").grid(row=2,
                                                                                                            column=0,
                                                                                                            padx=5,
                                                                                                            pady=5,
                                                                                                            sticky='e')
        self.annotation_entry = tk.Entry(settings_inner_frame)
        self.annotation_entry.grid(row=2, column=1, padx=5, pady=5, columnspan=3)

        self.set_annotation_button = tk.Button(settings_inner_frame, text="设置自定义标注",
                                               command=self.set_annotations)
        self.set_annotation_button.grid(row=2, column=4, padx=5, pady=5)

        # 保存文件名输入框
        self.filename_entries = {}

        # 默认 tmin, tmax, baseline 值
        self.tmin = None
        self.tmax = None
        self.baseline = None

        self.annotations = {}
        self.epochs_data = {}

        # 保存格式选择
        save_format_frame = tk.Frame(settings_frame)
        save_format_frame.pack(fill=tk.X, padx=5, pady=5)

        self.save_format_label = tk.Label(save_format_frame, text="选择保存格式:")
        self.save_format_label.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_format_var = tk.StringVar(value="mat")
        self.mat_radio = tk.Radiobutton(save_format_frame, text="MAT", variable=self.save_format_var, value="mat")
        self.mat_radio.pack(side=tk.LEFT, padx=5, pady=5)

        self.npy_radio = tk.Radiobutton(save_format_frame, text="Numpy", variable=self.save_format_var, value="npy")
        self.npy_radio.pack(side=tk.LEFT, padx=5, pady=5)



    def process_data(self):
        if self.tmin is None or self.tmax is None:
            messagebox.showwarning("错误", "请先设置 tmin 和 tmax")
            return

        if not self.annotations:
            messagebox.showwarning("错误", "请先设置自定义标注")
            return

        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("错误", "请选择要处理的文件")
            return

        self.epochs_data = {}
        self.processed_file_names = {}  # 记录每个标注对应的文件名

        for idx in selected_indices:
            raw = self.raw_list[idx]
            file_name = self.file_names[idx]
            try:
                self.process_single_file(raw, file_name)
            except Exception as e:
                messagebox.showerror("处理错误", f"处理文件时出错: {e}")
                continue

        # 计算每个标注的数据形状
        result_text = ""
        for name, data_list in self.epochs_data.items():
            if data_list:
                sample_shape = data_list[0].shape
                result_text += f"{name} Epochs形状: {sample_shape}\n"

        self.result_label.config(text=result_text)

        messagebox.showinfo("处理完成", "数据已处理。")
        self.save_button.config(state=tk.NORMAL)

    def process_single_file(self, raw, file_name):
        events, event_id = mne.events_from_annotations(raw, event_id=self.annotations)
        picks = mne.pick_types(raw.info, meg=False, eeg=True, stim=False, eog=False, exclude='bads')

        for name, event_code in self.annotations.items():
            epochs = mne.Epochs(raw, events, event_id={name: event_code}, tmin=self.tmin, tmax=self.tmax,
                                baseline=self.baseline, picks=picks, preload=True)
            if name not in self.epochs_data:
                self.epochs_data[name] = []
                self.processed_file_names[name] = []
            self.epochs_data[name].append((epochs.get_data() * 1e6).astype(np.float32))
            self.processed_file_names[name].append(file_name)

    def set_tmin_tmax(self):
        try:
            self.tmin = float(self.tmin_entry.get())
            self.tmax = float(self.tmax_entry.get())
            messagebox.showinfo("设置成功", f"tmin 设置为 {self.tmin}\ntmax 设置为 {self.tmax}")
        except ValueError:
            messagebox.showerror("输入错误", "请确保 tmin 和 tmax 输入的是有效的数字")

    def set_baseline(self):
        baseline_text = self.baseline_entry.get()
        if baseline_text.strip().lower() == 'none':
            self.baseline = None
        else:
            try:
                self.baseline = tuple(float(x) for x in baseline_text.split())
            except ValueError:
                messagebox.showerror("输入错误", "请确保基线输入的是有效的时间范围或 'None'")
                return
        messagebox.showinfo("设置成功", f"基线设置为: {self.baseline}")

    def set_annotations(self):
        annotation_text = self.annotation_entry.get()
        try:
            self.annotations = {}
            for item in annotation_text.split():
                name, id_ = item.split('=')
                self.annotations[name.strip()] = int(id_.strip())
            messagebox.showinfo("设置成功", f"自定义标注已设置为: {self.annotations}")

            # 为每个标注生成文件名输入框
            for widget in self.filename_entries.values():
                widget.pack_forget()

            self.filename_entries.clear()

            for name in self.annotations.keys():
                label = tk.Label(self.root, text=f"输入{name}的保存文件名:")
                label.pack(pady=5)
                entry = tk.Entry(self.root)
                entry.pack(pady=5)
                self.filename_entries[name] = entry
        except ValueError:
            messagebox.showerror("输入错误", "请确保标注格式正确，如 'T1=1 T2=2'")

    def save_file(self):
        if self.epochs_data:
            file_format = self.save_format_var.get()
            for name, data_list in self.epochs_data.items():
                filename = self.filename_entries[name].get().strip()
                if not filename:
                    messagebox.showerror("保存错误", f"请为{name}提供文件名")
                    return
                for i, data in enumerate(data_list):
                    # 获取文件名部分并删除后缀
                    file_name = os.path.splitext(os.path.basename(self.processed_file_names[name][i]))[0]

                    if file_format == "mat":
                        save_path = os.path.join(self.save_path, f"{filename}_{file_name}.mat")
                        sio.savemat(save_path, {name: data})
                    elif file_format == "npy":
                        save_path = os.path.join(self.save_path, f"{filename}_{file_name}.npy")
                        np.save(save_path, data)
            messagebox.showinfo("保存成功", f"文件已保存到: {self.save_path}")
        else:
            messagebox.showwarning("保存错误", "没有可保存的数据")

    def close_app(self):
        self.root.destroy()


import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import scipy.io as sio
# 拼接
class NpyConcatenator:
    def __init__(self, root):
        self.root = root
        self.root.title("拼接 .npy 文件")
        self.file_paths = []

        # 创建主框架
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 创建选择文件按钮和显示框
        tk.Label(main_frame, text="选择要拼接的文件:").grid(row=0, column=0, padx=10, pady=5)
        self.file_paths_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=self.file_paths_var, width=50, state='readonly').grid(row=0, column=1, padx=10, pady=5)
        tk.Button(main_frame, text="浏览", command=self.browse_files).grid(row=0, column=2, padx=10, pady=5)

        # 创建输出文件路径选择按钮和显示框
        tk.Label(main_frame, text="输出文件:").grid(row=1, column=0, padx=10, pady=5)
        self.output_file_var = tk.StringVar()
        tk.Entry(main_frame, textvariable=self.output_file_var, width=50).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(main_frame, text="浏览", command=self.browse_output_file).grid(row=1, column=2, padx=10, pady=5)

        # 创建保存格式选择下拉菜单
        tk.Label(main_frame, text="保存格式:").grid(row=2, column=0, padx=10, pady=5)
        self.output_format_var = tk.StringVar()
        self.output_format_var.set('npy')  # 默认选择 npy 格式
        format_menu = ttk.Combobox(main_frame, textvariable=self.output_format_var, values=['npy', 'mat'], state='readonly')
        format_menu.grid(row=2, column=1, padx=10, pady=5)
        self.output_format_var.trace_add('write', self.update_output_file_extension)

        # 创建拼接按钮
        tk.Button(main_frame, text="拼接文件", command=self.on_concatenate).grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # 创建关闭按钮
        tk.Button(main_frame, text="关闭", command=self.root.destroy).grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        # Listbox 控件展示加载的数据文件
        self.file_listbox = tk.Listbox(main_frame, width=50, height=10)
        self.file_listbox.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

    def browse_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("NumPy files", "*.npy")])
        if file_paths:
            self.file_paths = file_paths
            self.file_paths_var.set('; '.join(file_paths))
            self.file_listbox.delete(0, tk.END)
            for filepath in file_paths:
                self.file_listbox.insert(tk.END, filepath)

    def browse_output_file(self):
        file_selected = filedialog.asksaveasfilename(defaultextension='.npy',
                                                     filetypes=[("NumPy files", "*.npy"), ("MAT files", "*.mat")])
        if file_selected:
            self.output_file_var.set(file_selected)
            self.update_output_file_extension()

    def update_output_file_extension(self, *args):
        output_file = self.output_file_var.get()
        output_format = self.output_format_var.get()
        if output_file:
            if output_format == 'npy' and not output_file.endswith('.npy'):
                output_file += '.npy'
            elif output_format == 'mat' and not output_file.endswith('.mat'):
                output_file += '.mat'
            self.output_file_var.set(output_file)

    def on_concatenate(self):
        file_paths = self.file_paths_var.get().split('; ')
        output_file = self.output_file_var.get()
        output_format = self.output_format_var.get()
        if not file_paths or not output_file:
            messagebox.showerror("错误", "请指定要拼接的文件和输出文件路径。")
            return
        self.concatenate_npy_files(file_paths, output_file, output_format)

    def concatenate_npy_files(self, file_paths, output_file, output_format):
        if not file_paths:
            messagebox.showerror("错误", "没有选择任何文件。")
            return
        arrays = []
        for file_path in file_paths:
            data = np.load(file_path, allow_pickle=True)  # 允许加载pickle数据
            arrays.append(data)
        concatenated_array = np.concatenate(arrays, axis=0)
        if output_format == 'npy':
            np.save(output_file, concatenated_array)
        elif output_format == 'mat':
            sio.savemat(output_file, {'data': concatenated_array})
        messagebox.showinfo("成功", f"拼接后的数据已保存到 {output_file}")
        self.show_concatenated_data_structure(concatenated_array)

    def show_concatenated_data_structure(self, data):
        structure_window = tk.Toplevel(self.root)
        structure_window.title("拼接后数据结构")
        tk.Label(structure_window, text=f"数据结构: {data.shape}").pack(padx=10, pady=10)

# 阈值
class DataFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("数据过滤器与拼接工具")
        self.loaded_data = []
        self.filtered_data = []
        self.save_directory = None

        # 设置主框架
        main_frame = tk.Frame(root)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # 设置输入参数框架
        input_frame = tk.Frame(main_frame)
        input_frame.grid(row=0, column=0, sticky="nsew")

        # 阈值标签和输入框
        self.label_threshold = tk.Label(input_frame, text="自定义阈值:")
        self.label_threshold.grid(row=0, column=0, padx=10, pady=10)
        self.threshold = tk.Entry(input_frame, width=10)
        self.threshold.grid(row=0, column=1, padx=10, pady=10)

        # 最小试验数量标签和输入框
        self.label_min_trials = tk.Label(input_frame, text="最小试验数量:")
        self.label_min_trials.grid(row=0, column=2, padx=10, pady=10)
        self.min_trials = tk.Entry(input_frame, width=10)
        self.min_trials.grid(row=0, column=3, padx=10, pady=10)

        # 选择文件按钮
        self.btn_load_file = tk.Button(input_frame, text="选择文件", command=self.load_data_files)
        self.btn_load_file.grid(row=0, column=4, padx=10, pady=10)

        # 保存格式标签和选项
        self.label_format = tk.Label(input_frame, text="保存格式:")
        self.label_format.grid(row=1, column=0, padx=10, pady=10)
        self.selected_format = tk.StringVar(value="npy")
        self.option_format = tk.OptionMenu(input_frame, self.selected_format, "npy", "mat")
        self.option_format.grid(row=1, column=1, padx=10, pady=10)

        # 选择保存目录按钮
        self.btn_select_directory = tk.Button(input_frame, text="选择保存目录", command=self.select_save_directory)
        self.btn_select_directory.grid(row=1, column=2, padx=10, pady=10)

        # 过滤按钮
        self.btn_filter = tk.Button(input_frame, text="过滤数据", command=self.filter_data)
        self.btn_filter.grid(row=1, column=3, padx=10, pady=10)

        # 显示数据结构按钮
        self.btn_show_structure = tk.Button(input_frame, text="显示数据结构", command=self.show_data_structure)
        self.btn_show_structure.grid(row=1, column=4, padx=10, pady=10)

        # 关闭按钮
        self.btn_close = tk.Button(input_frame, text="关闭", command=root.destroy)
        self.btn_close.grid(row=2, column=0, columnspan=5, padx=10, pady=10)

        # Listbox 控件展示加载的数据文件
        self.file_listbox = tk.Listbox(main_frame, width=50, height=10)
        self.file_listbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # 添加拼接功能按钮
        self.btn_concatenate = tk.Button(input_frame, text="拼接文件", command=self.open_concatenate_window)
        self.btn_concatenate.grid(row=2, column=4, padx=10, pady=10)

    def open_concatenate_window(self):
        concatenate_window = tk.Toplevel(self.root)
        NpyConcatenator(concatenate_window)

    def load_data_files(self):
        filepaths = filedialog.askopenfilenames(title="选择数据文件", filetypes=[("Numpy Files", "*.npy")])
        if filepaths:
            self.loaded_data.clear()
            self.file_listbox.delete(0, tk.END)
            for filepath in filepaths:
                data = self.load_data(filepath)
                if data is not None:
                    self.loaded_data.append((filepath, data))
                    self.file_listbox.insert(tk.END, filepath)

    def load_data(self, filepath):
        try:
            data = np.load(filepath)  # 假设数据是以.npy格式存储的
            return data
        except Exception as e:
            messagebox.showerror("错误", f"加载数据失败: {e}")
            return None

    def filter_trials(self, epochs_data, threshold, min_trials):
        ntrail = []
        for trail in range(len(epochs_data)):
            if np.max(np.abs(epochs_data[trail])) < threshold:
                ntrail.append(trail)

        filtered_data = epochs_data[ntrail, :, :]

        # 检查过滤后的试验数量是否不足
        if filtered_data.shape[0] < min_trials:
            print("有效的试验数量不足。")
            return None

        return filtered_data

    def save_data(self, data, save_path, file_format):
        try:
            if file_format == 'npy':
                np.save(save_path, data)
            elif file_format == 'mat':
                sio.savemat(save_path, {'filtered_data': data})
            messagebox.showinfo("成功", f"过滤后的数据已保存至: {save_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存数据失败: {e}")

    def filter_data(self):
        if not self.loaded_data:
            messagebox.showwarning("警告", "请先加载数据")
            return

        try:
            threshold_value = float(self.threshold.get())
            min_trials_value = int(self.min_trials.get())
        except ValueError:
            messagebox.showwarning("警告", "请输入有效的阈值和试验数量")
            return

        self.filtered_data.clear()
        for filepath, data in self.loaded_data:
            filtered_data = self.filter_trials(data, threshold_value, min_trials_value)
            if filtered_data is None:
                messagebox.showwarning("警告", f"文件 {filepath} 有效的试验数量不足，未进行保存。")
                continue
            self.filtered_data.append((filepath, filtered_data))

        if self.save_directory is None:
            messagebox.showwarning("警告", "请选择保存目录")
            return

        for filepath, filtered_data in self.filtered_data:
            base_name = filepath.rsplit('/', 1)[-1].rsplit('.', 1)[0]
            save_path = f"{self.save_directory}/{base_name}_yz.{self.selected_format.get()}"
            self.save_data(filtered_data, save_path, self.selected_format.get())

    def show_data_structure(self):
        if not self.loaded_data:
            messagebox.showwarning("警告", "请先加载数据")
            return

        # 显示处理前数据的结构
        msg = "处理前数据结构:\n"
        for filepath, data in self.loaded_data:
            msg += f"{filepath}: {data.shape}\n"

        if self.filtered_data:
            # 显示处理后数据的结构
            msg += "\n处理后数据结构:\n"
            for filepath, filtered_data in self.filtered_data:
                msg += f"{filepath}: {filtered_data.shape}\n"
        else:
            msg += "\n尚未处理数据\n"

        messagebox.showinfo("数据结构", msg)

    def select_save_directory(self):
        self.save_directory = filedialog.askdirectory(title="选择保存目录")
        if self.save_directory:
            messagebox.showinfo("成功", f"选择的保存目录为: {self.save_directory}")
        else:
            self.save_directory = None
# 主界面
class EEGViewerProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("EEG数据查看与处理器")
        self.root.geometry("1000x700")
        self.root.minsize(600, 400)

        # Set modern theme
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Customize ttk style for a modern look
        self.style.configure('TButton', padding=6, relief="flat", background="#4CAF50", foreground="white",
                             font=("Arial", 10))
        self.style.configure('TFrame', background="#f0f0f0")
        self.style.configure('TLabel', background="#f0f0f0", font=("Arial", 10))
        self.style.configure('TMenu', background="#4CAF50", foreground="white", font=("Arial", 10))

        # Set up layout frames
        self.frame_top = ttk.Frame(root)
        self.frame_top.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        self.frame_middle = ttk.Frame(root)
        self.frame_middle.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.frame_bottom = ttk.Frame(root)
        self.frame_bottom.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        # File Listbox
        self.file_listbox = Listbox(self.frame_top, selectmode=MULTIPLE)
        self.file_listbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Save path
        tk.Label(self.frame_top, text="保存路径:", font=('Helvetica', 12)).grid(row=1, column=0, padx=10, pady=5)
        self.save_path_entry = ttk.Entry(self.frame_top, width=50)
        self.save_path_entry.grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.frame_top, text="选择保存路径", command=self.select_save_path).grid(row=1, column=2, padx=10, pady=5)

        # Create menu bar
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        self.file_menu.add_command(label="加载EEG数据", command=self.load_data)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出", command=self.close_window)

        # Filter menu
        self.filter_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="滤波", menu=self.filter_menu)
        self.filter_menu.add_command(label="应用滤波", command=self.set_filter_parameters)

        # ICA menu
        self.ica_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="ICA处理", menu=self.ica_menu)
        self.ica_menu.add_command(label="运行ICA处理", command=self.open_ica_window)
        self.ica_window = None
        self.ica_canvas = None

        # Annotation menu (New)
        self.annotation_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="标注检查", menu=self.annotation_menu)
        self.annotation_menu.add_command(label="检查标注", command=self.open_annotation_window)

        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="帮助", menu=self.help_menu)
        self.help_menu.add_command(label="关于", command=self.show_about_info)

        # Scrolled text box for displaying EEG data information
        self.info_text = scrolledtext.ScrolledText(self.frame_middle, wrap=tk.WORD, font=("Arial", 10))
        self.info_text.grid(row=0, column=0, sticky="nsew")
        self.info_text.config(state=tk.DISABLED)

        # Status bar
        self.status_bar = ttk.Label(self.frame_bottom, text="欢迎使用EEG数据查看与处理器", anchor=tk.W)
        self.status_bar.grid(row=0, column=0, sticky="ew")

        # Set row and column expansion
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

        self.annotation_event_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="数据有标注提取事件", menu=self.annotation_event_menu)
        self.annotation_event_menu.add_command(label="提取事件", command=self.open_annotation_event_window)

        self.data_extractor_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="数据有无标注提取事件", menu=self.data_extractor_menu)
        self.data_extractor_menu.add_command(label="提取事件", command=self.open_data_extractor_window)

        # 添加数据过滤菜单
        self.data_filter_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="阈值", menu=self.data_filter_menu)
        self.data_filter_menu.add_command(label="打开数据过滤器", command=self.open_data_filter_window)

    def open_data_extractor_window(self):
        if not hasattr(self, "raw_list"):
            messagebox.showerror("错误", "请先加载数据。")
            return

        data_extractor_window = tk.Toplevel(self.root)
        data_extractor_window.title("EEG Data Extractor")
        data_extractor_app = EEGDataExtractorApp(data_extractor_window, self.file_names)

    def open_data_filter_window(self):
        data_filter_window = tk.Toplevel(self.root)
        DataFilterApp(data_filter_window)

    def select_save_path(self):
        save_path = filedialog.askdirectory()
        if save_path:
            self.save_path_entry.delete(0, tk.END)
            self.save_path_entry.insert(0, save_path)

    def open_annotation_event_window(self):
        if not hasattr(self, "raw_list"):
            messagebox.showerror("错误", "请先加载数据。")
            return

        save_path = self.save_path_entry.get()
        if not save_path:
            messagebox.showerror("错误", "请先选择保存路径。")
            return

        annotation_event_window = tk.Toplevel(self.root)
        annotation_event_window.title("数据有标注提取事件")
        annotation_event_processor = AnnotationEventProcessor(annotation_event_window, self.raw_list, self.file_names,
                                                              save_path)

    def load_data(self):
        file_paths = filedialog.askopenfilenames(
            filetypes=[("FIF files", "*.fif"), ("EDF files", "*.edf"), ("BDF files", "*.bdf")]
        )

        if file_paths:
            try:
                self.raw_list = []
                self.file_names = []

                self.file_listbox.delete(0, tk.END)

                for file_path in file_paths:
                    if file_path.endswith('.fif'):
                        raw = mne.io.read_raw_fif(file_path, preload=True)
                    elif file_path.endswith('.edf'):
                        raw = mne.io.read_raw_edf(file_path, preload=True)
                    elif file_path.endswith('.bdf'):
                        raw = mne.io.read_raw_bdf(file_path, preload=True)
                    else:
                        messagebox.showerror("错误", f"不支持的文件格式: {file_path}")
                        continue

                    # 标准化通道名称
                    eegbci.standardize(raw)

                    self.raw_list.append(raw)
                    self.file_names.append(file_path)
                    self.file_listbox.insert(tk.END, os.path.basename(file_path))

                messagebox.showinfo("信息", "数据加载成功。")
                self.status_bar.config(text="EEG数据加载成功")

                self.info_text.config(state=tk.NORMAL)
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, "\n\n".join(str(raw.info) for raw in self.raw_list))
                self.info_text.config(state=tk.DISABLED)

            except Exception as e:
                messagebox.showerror("错误", f"数据加载失败: {e}")
                self.status_bar.config(text="EEG数据加载失败")

    def set_filter_parameters(self):
        filter_window = tk.Toplevel(self.root)
        filter_window.title("应用滤波")

        # 添加文件列表框
        tk.Label(filter_window, text="选择要处理的文件:", font=('Helvetica', 12)).grid(row=0, column=0, padx=10,
                                                                                       pady=10)
        self.filter_file_listbox = Listbox(filter_window, selectmode=MULTIPLE)
        self.filter_file_listbox.grid(row=0, column=1, padx=10, pady=10)

        if hasattr(self, "file_names"):
            for file_name in self.file_names:
                self.filter_file_listbox.insert(tk.END, os.path.basename(file_name))

        tk.Label(filter_window, text="工频滤波频率 (Hz):", font=('Helvetica', 12)).grid(row=1, column=0, padx=10,
                                                                                        pady=10)
        self.notch_freq_entry = ttk.Entry(filter_window)
        self.notch_freq_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(filter_window, text="带通滤波下限 (Hz):", font=('Helvetica', 12)).grid(row=2, column=0, padx=10,
                                                                                        pady=10)
        self.l_freq_entry = ttk.Entry(filter_window)
        self.l_freq_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(filter_window, text="带通滤波上限 (Hz):", font=('Helvetica', 12)).grid(row=3, column=0, padx=10,
                                                                                        pady=10)
        self.h_freq_entry = ttk.Entry(filter_window)
        self.h_freq_entry.grid(row=3, column=1, padx=10, pady=10)

        tk.Label(filter_window, text="参考类型:", font=('Helvetica', 12)).grid(row=4, column=0, padx=10, pady=10)
        self.ref_var = tk.StringVar(value='使用平均参考')
        self.ref_menu = ttk.Combobox(filter_window, textvariable=self.ref_var, values=["使用平均参考", "不使用参考"],
                                     font=('Helvetica', 12))
        self.ref_menu.grid(row=4, column=1, padx=10, pady=10)

        tk.Button(filter_window, text="应用滤波并保存", command=self.process_and_save_data).grid(row=5, column=0,
                                                                                                 columnspan=2, pady=10)

    def process_and_save_data(self):
        if not hasattr(self, "raw_list"):
            messagebox.showerror("错误", "请先加载数据。")
            return

        try:
            # 获取滤波参数
            if self.notch_freq_entry.winfo_exists():
                notch_freq = float(self.notch_freq_entry.get())
            else:
                messagebox.showerror("错误", "工频滤波频率输入框未找到。")
                return

            l_freq = float(self.l_freq_entry.get())
            h_freq = float(self.h_freq_entry.get())
            ref_type = self.ref_var.get()

            processed_files = []

            # 获取选择的文件索引
            selected_indices = self.filter_file_listbox.curselection()
            if not selected_indices:
                messagebox.showerror("错误", "请选择要处理的文件。")
                return

            for idx in selected_indices:
                raw = self.raw_list[idx]
                file_path = self.file_names[idx]

                # 滤波
                raw.notch_filter(notch_freq)
                raw.filter(l_freq, h_freq)

                # 设置参考
                if ref_type == "使用平均参考":
                    raw.set_eeg_reference('average')
                elif ref_type == "不使用参考":
                    raw.set_eeg_reference([])

                # 保存文件
                base_name = os.path.basename(file_path)
                save_name = f"{os.path.splitext(base_name)[0]}_filtering.fif"
                save_path = os.path.join(self.save_path_entry.get(), save_name)
                raw.save(save_path, overwrite=True)
                processed_files.append(save_name)

            messagebox.showinfo("信息", f"滤波并保存成功: {', '.join(processed_files)}")
            self.status_bar.config(text="滤波并保存成功")

        except Exception as e:
            messagebox.showerror("错误", f"滤波处理失败: {e}")
            self.status_bar.config(text="滤波处理失败")
    def open_annotation_window(self):
        if not hasattr(self, "raw_list"):
            messagebox.showerror("错误", "请先加载数据。")
            return

        annotation_window = tk.Toplevel(self.root)
        annotation_window.title("标注检查")

        tk.Label(annotation_window, text="选择要检查的文件:", font=('Helvetica', 12)).grid(row=0, column=0, padx=10,
                                                                                           pady=10)
        self.annotation_file_listbox = Listbox(annotation_window, selectmode=SINGLE)
        self.annotation_file_listbox.grid(row=0, column=1, padx=10, pady=10)

        for file_name in self.file_names:
            self.annotation_file_listbox.insert(tk.END, os.path.basename(file_name))

        tk.Label(annotation_window, text="标注信息:", font=('Helvetica', 12)).grid(row=1, column=0, padx=10, pady=10)
        annotations_text = scrolledtext.ScrolledText(annotation_window, wrap=tk.WORD, font=("Arial", 10), width=60,
                                                     height=20)
        annotations_text.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(annotation_window, text="标注个数:", font=('Helvetica', 12)).grid(row=2, column=0, padx=10, pady=10)
        annotation_count_text = scrolledtext.ScrolledText(annotation_window, wrap=tk.WORD, font=("Arial", 10), width=60,
                                                          height=10)
        annotation_count_text.grid(row=2, column=1, padx=10, pady=10)

        def update_annotations():
            selected_index = self.annotation_file_listbox.curselection()
            if not selected_index:
                annotations_text.delete(1.0, tk.END)
                annotations_text.insert(tk.END, "请选择一个文件。\n")
                annotation_count_text.delete(1.0, tk.END)
                annotation_count_text.insert(tk.END, "请选择一个文件。\n")
                return

            raw = self.raw_list[selected_index[0]]
            if raw.annotations is not None:
                annotations_text.delete(1.0, tk.END)
                for annot in raw.annotations:
                    annotations_text.insert(tk.END,
                                            f"开始时间: {annot['onset']}, 持续时间: {annot['duration']}, 描述: {annot['description']}\n")

                annotation_counts = {}
                for annot in raw.annotations:
                    if annot['description'] in annotation_counts:
                        annotation_counts[annot['description']] += 1
                    else:
                        annotation_counts[annot['description']] = 1

                annotation_count_text.delete(1.0, tk.END)
                for description, count in annotation_counts.items():
                    annotation_count_text.insert(tk.END, f"{description}: {count}\n")
            else:
                annotations_text.delete(1.0, tk.END)
                annotations_text.insert(tk.END, "没有找到标注信息。\n")
                annotation_count_text.delete(1.0, tk.END)
                annotation_count_text.insert(tk.END, "没有找到标注信息。\n")

        update_annotations()
        self.annotation_file_listbox.bind('<<ListboxSelect>>', lambda event: update_annotations())
    def open_ica_window(self):
        if not hasattr(self, "raw_list"):
            messagebox.showerror("错误", "请先加载数据。")
            return

        ica_window = tk.Toplevel(self.root)
        ica_window.title("ICA处理")

        tk.Label(ica_window, text="选择要处理的文件:", font=('Helvetica', 12)).grid(row=0, column=0, padx=10, pady=10)
        self.ica_file_listbox = Listbox(ica_window, selectmode=MULTIPLE)
        self.ica_file_listbox.grid(row=0, column=1, padx=10, pady=10)

        for file_name in self.file_names:
            self.ica_file_listbox.insert(tk.END, os.path.basename(file_name))

        tk.Label(ica_window, text="Montage系统:", font=('Helvetica', 12)).grid(row=1, column=0, padx=10, pady=10)
        montage_var = tk.StringVar()
        montage_menu = ttk.Combobox(ica_window, textvariable=montage_var,
                                    values=["standard_1005", "standard_1020", "standard_1020", "biosemi32",
                                            "biosemi64"],
                                    font=('Helvetica', 12))
        montage_menu.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(ica_window, text="ICA成分数:", font=('Helvetica', 12)).grid(row=2, column=0, padx=10, pady=10)
        n_components_entry = ttk.Entry(ica_window)
        n_components_entry.insert(0, "7")
        n_components_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(ica_window, text="最大迭代次数:", font=('Helvetica', 12)).grid(row=3, column=0, padx=10, pady=10)
        max_iter_entry = ttk.Entry(ica_window)
        max_iter_entry.insert(0, "1000")
        max_iter_entry.grid(row=3, column=1, padx=10, pady=10)

        exclude_muscle_btn = tk.Button(ica_window, text="排除肌肉伪影",
                                       command=lambda: self.exclude_muscle_artifacts(montage_var.get(),
                                                                                     n_components_entry.get(),
                                                                                     max_iter_entry.get()))
        exclude_muscle_btn.grid(row=4, column=0, padx=10, pady=10)

        run_ica_btn = tk.Button(ica_window, text="运行ICA", command=lambda: self.run_ica(montage_var.get(),
                                                                                         n_components_entry.get(),
                                                                                         max_iter_entry.get()))
        run_ica_btn.grid(row=4, column=1, padx=10, pady=10)

        tk.Label(ica_window, text="剔除成分索引 (空格分隔):", font=('Helvetica', 12)).grid(row=5, column=0, padx=10,
                                                                                           pady=10)
        exclude_components_entry = ttk.Entry(ica_window)
        exclude_components_entry.grid(row=5, column=1, padx=10, pady=10)

        exclude_btn = tk.Button(ica_window, text="剔除成分",
                                command=lambda: self.exclude_components(exclude_components_entry.get()))
        exclude_btn.grid(row=6, column=0, columnspan=2, pady=10)

        save_btn = tk.Button(ica_window, text="保存ICA结果", command=self.save_ica_results)
        save_btn.grid(row=7, column=0, columnspan=2, pady=10)

    def save_ica_results(self):
        if not hasattr(self, "raw_list"):
            messagebox.showerror("错误", "请先加载数据。")
            return

        try:
            selected_indices = self.ica_file_listbox.curselection()
            for idx in selected_indices:
                raw = self.raw_list[idx]
                file_path = self.file_names[idx]
                base_name = os.path.basename(file_path)
                save_name = f"{os.path.splitext(base_name)[0]}_ica.fif"
                save_path = os.path.join(self.save_path_entry.get(), save_name)

                # 确保ICA对象存在
                if not hasattr(self, "ica") or self.ica is None:
                    messagebox.showerror("错误", "请先运行ICA处理。")
                    return

                # 应用ICA并保存
                raw.load_data()
                raw = self.ica.apply(raw)
                raw.save(save_path, overwrite=True)

            messagebox.showinfo("信息", "ICA结果保存成功")
            self.status_bar.config(text="ICA结果保存成功")

        except Exception as e:
            messagebox.showerror("错误", f"保存ICA结果失败: {e}")
            self.status_bar.config(text="保存ICA结果失败")

    def exclude_muscle_artifacts(self, montage_system, n_components, max_iter):
        if not hasattr(self, "raw_list"):
            messagebox.showerror("错误", "请先加载数据。")
            return

        try:
            selected_indices = self.ica_file_listbox.curselection()
            for idx in selected_indices:
                raw = self.raw_list[idx]
                ica = ICA(n_components=int(n_components), max_iter=int(max_iter), random_state=97)
                ica.fit(raw)

                muscle_idx, scores = ica.find_bads_muscle(raw)
                ica.exclude = muscle_idx

                raw.load_data()
                raw = ica.apply(raw)

            messagebox.showinfo("信息", "肌肉伪影已排除")
            self.status_bar.config(text="肌肉伪影已排除")

        except Exception as e:
            messagebox.showerror("错误", f"排除肌肉伪影失败: {e}")
            self.status_bar.config(text="排除肌肉伪影失败")

    def run_ica(self, montage_system, n_components, max_iter):
        if not hasattr(self, "raw_list"):
            messagebox.showerror("错误", "请先加载数据。")
            return

        try:
            selected_indices = self.ica_file_listbox.curselection()
            for idx in selected_indices:
                raw = self.raw_list[idx]
                montage = mne.channels.make_standard_montage(montage_system)
                raw.set_montage(montage)

                # 清除之前的ICA对象
                self.ica = None

                self.ica = ICA(n_components=int(n_components), max_iter=int(max_iter), random_state=97)
                self.ica.fit(raw)

                if self.ica_window is None or not tk.Toplevel.winfo_exists(self.ica_window):
                    self.ica_window = tk.Toplevel(self.root)
                    self.ica_window.title("ICA 成分图")

                    fig = self.ica.plot_components(inst=raw, show=False)
                    self.ica_canvas = FigureCanvasTkAgg(fig, master=self.ica_window)
                    self.ica_canvas.draw()
                    self.ica_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

                    toolbar_frame = tk.Frame(self.ica_window)
                    toolbar_frame.pack(side=tk.TOP, fill=tk.X)
                    toolbar = matplotlib.backends.backend_tkagg.NavigationToolbar2Tk(self.ica_canvas, toolbar_frame)
                    toolbar.update()

                    # 移除保存ICA结果按钮
                    # save_btn = tk.Button(self.ica_window, text="保存ICA结果",
                    #                      command=lambda: self.save_ica_results(self.ica, raw))
                    # save_btn.pack(pady=10)
                else:
                    fig = self.ica.plot_components(inst=raw, show=False)
                    self.ica_canvas.figure = fig
                    self.ica_canvas.draw()

                messagebox.showinfo("信息", "ICA处理成功")
                self.status_bar.config(text="ICA处理成功")

        except Exception as e:
            messagebox.showerror("错误", f"ICA处理失败: {e}")
            self.status_bar.config(text="ICA处理失败")

    def exclude_components(self, component_indices):
        if not hasattr(self, "raw_list"):
            messagebox.showerror("错误", "请先加载数据。")
            return

        try:
            selected_indices = self.ica_file_listbox.curselection()
            for idx in selected_indices:
                raw = self.raw_list[idx]
                # 清除之前的ICA对象
                self.ica = None

                self.ica = ICA()
                self.ica.fit(raw)

                exclude = list(map(int, component_indices.split()))
                self.ica.exclude = exclude

                raw.load_data()
                raw = self.ica.apply(raw)

            messagebox.showinfo("信息", "成分已剔除")
            self.status_bar.config(text="成分已剔除")

        except Exception as e:
            messagebox.showerror("错误", f"剔除成分失败: {e}")
            self.status_bar.config(text="剔除成分失败")
    def show_about_info(self):
        messagebox.showinfo("关于", "版本：1.0\n作者：dengyufeng\n邮箱：3087178834@qq.com")

    def close_window(self):
        self.root.quit()


# 提取事件无标注界面
class EEGDataExtractorApp:
    def __init__(self, root, eeg_file_paths):
        self.root = root
        self.root.title("EEG Data Extractor")
        self.root.geometry("800x600")

        self.eeg_file_paths = [os.path.normpath(path) for path in eeg_file_paths]

        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # 加载TSV文件的按钮
        self.load_tsv_button = tk.Button(button_frame, text="加载TSV文件", command=self.load_tsv_files)
        self.load_tsv_button.pack(side=tk.LEFT, padx=5)

        # 查看文件对应关系的按钮
        self.show_correspondence_button = tk.Button(button_frame, text="查看文件对应关系",
                                                    command=self.show_file_correspondence)
        self.show_correspondence_button.pack(side=tk.LEFT, padx=5)

        # 添加保存格式下拉菜单
        self.save_format_label = tk.Label(button_frame, text="选择保存格式:")
        self.save_format_label.pack(side=tk.LEFT, padx=5)

        self.save_format = tk.StringVar()
        self.save_format.set("npy")  # 默认保存格式为NPY

        self.save_format_combobox = ttk.Combobox(button_frame, textvariable=self.save_format, values=["npy", "mat"])
        self.save_format_combobox.pack(side=tk.LEFT, padx=5)

        self.process_button = tk.Button(button_frame, text="处理数据", command=self.process_data)
        self.process_button.pack(side=tk.LEFT, padx=5)

        self.close_button = tk.Button(button_frame, text="关闭", command=self.close_app)
        self.close_button.pack(side=tk.LEFT, padx=5)

        # 添加Listbox展示已加载的文件
        self.file_listbox = Listbox(main_frame, selectmode=MULTIPLE)
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 添加Listbox展示主界面加载的数据
        self.eeg_file_listbox = Listbox(main_frame, selectmode=MULTIPLE)
        self.eeg_file_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.save_dirs = {}
        self.tsv_file_paths = []
        self.output_dir = None

        # 展示主界面加载的数据
        self.show_eeg_files()

    def create_trial_type_buttons(self, tsv_file_paths):
        trial_types = set()
        for tsv_file_path in tsv_file_paths:
            df = pd.read_csv(tsv_file_path, sep='\t')
            trial_types.update(df['trial_type'].unique())

        self.save_dirs = {}

        for trial_type in trial_types:
            button = tk.Button(self.root, text=f"选择 {trial_type} 保存目录",
                               command=lambda t=trial_type: self.select_save_dir(t))
            button.pack(pady=5)

    def load_tsv_files(self):
        tsv_file_paths = filedialog.askopenfilenames(filetypes=[("TSV files", "*.tsv")])
        if tsv_file_paths:
            self.tsv_file_paths = [os.path.normpath(path) for path in tsv_file_paths]
            if len(self.tsv_file_paths) != len(self.eeg_file_paths):
                messagebox.showerror("错误", "加载的TSV文件和EEG文件数量不匹配")
                return
            self.create_trial_type_buttons(self.tsv_file_paths)
            self.show_file_correspondence()
            messagebox.showinfo("信息", f"已加载 {len(self.tsv_file_paths)} 个TSV文件")

            # 更新Listbox内容
            self.file_listbox.delete(0, tk.END)
            for tsv_file_path in self.tsv_file_paths:
                self.file_listbox.insert(tk.END, os.path.basename(tsv_file_path))

    def show_file_correspondence(self):
        correspondence_window = tk.Toplevel(self.root)
        correspondence_window.title("文件对应关系")
        correspondence_window.geometry("600x400")

        text_area = tk.Text(correspondence_window, wrap=tk.NONE)
        text_area.pack(expand=True, fill=tk.BOTH)

        text_area.insert(tk.END, "TSV文件 - EEG文件\n")
        text_area.insert(tk.END, "-" * 40 + "\n")

        for tsv_file_path, eeg_file_path in zip(self.tsv_file_paths, self.eeg_file_paths):
            tsv_filename = os.path.basename(tsv_file_path)
            eeg_filename = os.path.basename(eeg_file_path)
            text_area.insert(tk.END, f"{tsv_filename} - {eeg_filename}\n")


    def select_save_dir(self, trial_type=None):
        if trial_type:
            dir_path = filedialog.askdirectory()
            if dir_path:
                self.save_dirs[trial_type] = os.path.normpath(dir_path)
                messagebox.showinfo("信息", f"{trial_type} 保存目录已选择: {dir_path}")

    def process_data(self):
        if not self.tsv_file_paths or not self.eeg_file_paths:
            messagebox.showerror("错误", "请确保已加载TSV文件和EEG文件")
            return

        if len(self.tsv_file_paths) != len(self.eeg_file_paths):
            messagebox.showerror("错误", "加载的TSV文件和EEG文件数量不匹配")
            return

        if not self.save_dirs:
            messagebox.showerror("错误", "请先选择所有试验类型的保存目录")
            return

        save_format = self.save_format.get()

        try:
            for tsv_idx, (tsv_file_path, eeg_file_path) in enumerate(zip(self.tsv_file_paths, self.eeg_file_paths)):
                events_df = pd.read_csv(tsv_file_path, sep='\t')
                onsets = events_df['onset'].values
                durations = events_df['duration'].values
                trial_types = events_df['trial_type'].values

                # 使用 MNE 直接加载 EEG 数据
                eeg_data = mne.io.read_raw(eeg_file_path, preload=True)

                sfreq = eeg_data.info['sfreq']
                n_channels = eeg_data.info['nchan']

                # 收集所有事件的数据
                all_trials_data = []
                max_samples = 0
                for onset, duration in zip(onsets, durations):
                    # Convert milliseconds to seconds
                    onset_sec = onset / 1000.0
                    duration_sec = duration / 1000.0

                    start_idx = int(onset_sec * sfreq)
                    end_idx = int((onset_sec + duration_sec) * sfreq)
                    trial_data = eeg_data.get_data(start=start_idx, stop=end_idx)
                    all_trials_data.append(trial_data)
                    max_samples = max(max_samples, trial_data.shape[1])

                # 确保所有事件的数据长度一致，通过填充使其匹配最大采样点数
                for i in range(len(all_trials_data)):
                    trial_data = all_trials_data[i]
                    if trial_data.shape[1] < max_samples:
                        padding = np.zeros((n_channels, max_samples - trial_data.shape[1]))
                        all_trials_data[i] = np.hstack((trial_data, padding))
                    elif trial_data.shape[1] > max_samples:
                        all_trials_data[i] = trial_data[:, :max_samples]

                # 将数据形状转为 (事件数, 通道数, 单个事件的采样点数)
                all_trials_data = np.stack(all_trials_data)

                for trial_type in np.unique(trial_types):
                    trial_indices = np.where(trial_types == trial_type)[0]
                    selected_trials_data = all_trials_data[trial_indices, :, :]

                    if trial_type in self.save_dirs:
                        # 根据TSV文件的顺序和试验类型命名文件
                        tsv_basename = os.path.basename(tsv_file_path).split('.')[0]
                        if save_format == 'npy':
                            file_name = f'{tsv_idx + 1}_{tsv_basename}_{trial_type}_trials.npy'
                            file_path = os.path.join(self.save_dirs[trial_type], file_name)
                            np.save(file_path, selected_trials_data)
                        elif save_format == 'mat':
                            file_name = f'{tsv_idx + 1}_{tsv_basename}_{trial_type}_trials.mat'
                            file_path = os.path.join(self.save_dirs[trial_type], file_name)
                            savemat(file_path, {'data': selected_trials_data})
                        print(f'Saved {len(trial_indices)} trials for {trial_type} to {file_path}')
                    else:
                        messagebox.showwarning("警告", f"未为 trial_type '{trial_type}' 选择保存目录")

            messagebox.showinfo("完成", "所有试验数据已成功保存。")
        except Exception as e:
            messagebox.showerror("错误", f"处理数据时出现错误: {str(e)}")

    def show_eeg_files(self):
        self.eeg_file_listbox.delete(0, tk.END)
        for eeg_file_path in self.eeg_file_paths:
            self.eeg_file_listbox.insert(tk.END, os.path.basename(eeg_file_path))

    def close_app(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EEGViewerProcessor(root)
    root.mainloop()
