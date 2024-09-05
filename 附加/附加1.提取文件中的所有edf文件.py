import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def find_edf_files(directory):
    """
    查找指定目录及其子目录中的所有EDF文件
    :param directory: 要搜索的目录
    :return: EDF文件路径列表
    """
    edf_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.edf'):
                edf_files.append(os.path.join(root, file))
    return edf_files

def copy_edf_files(edf_files, output_directory):
    """
    将EDF文件复制到指定目录
    :param edf_files: EDF文件路径列表
    :param output_directory: 目标目录
    """
    try:
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        for file_path in edf_files:
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(output_directory, file_name)
            shutil.copy(file_path, dest_path)

        messagebox.showinfo("成功", f"成功复制 {len(edf_files)} 个EDF文件到 {output_directory}")
    except Exception as e:
        messagebox.showerror("错误", f"复制EDF文件时发生错误: {e}")

def select_input_directory():
    """
    选择输入目录
    """
    directory = filedialog.askdirectory()
    input_directory_var.set(directory)

def select_output_directory():
    """
    选择输出目录
    """
    directory = filedialog.askdirectory()
    output_directory_var.set(directory)

def start_copy():
    """
    开始复制操作
    """
    input_dir = input_directory_var.get()
    output_dir = output_directory_var.get()

    if not input_dir or not output_dir:
        messagebox.showwarning("警告", "请选择输入和输出目录。")
        return

    edf_files = find_edf_files(input_dir)
    copy_edf_files(edf_files, output_dir)

# 创建主窗口
root = tk.Tk()
root.title("EDF文件提取器")

# 创建变量来存储目录路径
input_directory_var = tk.StringVar()
output_directory_var = tk.StringVar()

# 创建和放置组件
tk.Label(root, text="输入目录:").grid(row=0, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=input_directory_var, width=50).grid(row=0, column=1, padx=10, pady=10)
tk.Button(root, text="浏览", command=select_input_directory).grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="输出目录:").grid(row=1, column=0, padx=10, pady=10)
tk.Entry(root, textvariable=output_directory_var, width=50).grid(row=1, column=1, padx=10, pady=10)
tk.Button(root, text="浏览", command=select_output_directory).grid(row=1, column=2, padx=10, pady=10)

tk.Button(root, text="开始复制", command=start_copy).grid(row=2, column=1, padx=10, pady=10)

# 运行主循环
root.mainloop()