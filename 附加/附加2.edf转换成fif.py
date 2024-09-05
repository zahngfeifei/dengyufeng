import os
import mne
import tkinter as tk
from tkinter import filedialog, messagebox


def 转换文件():
    # 获取输入和输出目录
    输入目录 = 输入目录变量.get()
    输出目录 = 输出目录变量.get()

    # 检查目录是否为空
    if not 输入目录 or not 输出目录:
        messagebox.showerror("错误", "请选择输入和输出目录。")
        return

    # 确保输出目录存在
    if not os.path.exists(输出目录):
        os.makedirs(输出目录)

    # 遍历输入目录中的所有 .edf 文件
    for 文件名 in os.listdir(输入目录):
        if 文件名.endswith('.edf'):
            # 构建完整的文件路径
            输入路径 = os.path.join(输入目录, 文件名)
            输出路径 = os.path.join(输出目录, 文件名.replace('.edf', '.fif'))

            try:
                # 读取 .edf 文件
                raw = mne.io.read_raw_edf(输入路径, preload=True)
                # 保存为 .fif 文件
                raw.save(输出路径, overwrite=True)
                print(f'已转换 {输入路径} 到 {输出路径}')
            except Exception as e:
                messagebox.showerror("错误", f"转换 {输入路径} 失败: {e}")

    messagebox.showinfo("成功", "所有 .edf 文件已转换为 .fif 文件。")


def 选择输入目录():
    # 弹出文件选择对话框
    目录 = filedialog.askdirectory()
    输入目录变量.set(目录)


def 选择输出目录():
    # 弹出文件选择对话框
    目录 = filedialog.askdirectory()
    输出目录变量.set(目录)


# 创建主窗口
根窗口 = tk.Tk()
根窗口.title("EDF 转 FIF 转换器")

# 输入目录选择
输入目录变量 = tk.StringVar()
输入目录标签 = tk.Label(根窗口, text="输入目录:")
输入目录标签.grid(row=0, column=0, padx=10, pady=10)
输入目录输入框 = tk.Entry(根窗口, textvariable=输入目录变量, width=50)
输入目录输入框.grid(row=0, column=1, padx=10, pady=10)
输入目录按钮 = tk.Button(根窗口, text="浏览", command=选择输入目录)
输入目录按钮.grid(row=0, column=2, padx=10, pady=10)

# 输出目录选择
输出目录变量 = tk.StringVar()
输出目录标签 = tk.Label(根窗口, text="输出目录:")
输出目录标签.grid(row=1, column=0, padx=10, pady=10)
输出目录输入框 = tk.Entry(根窗口, textvariable=输出目录变量, width=50)
输出目录输入框.grid(row=1, column=1, padx=10, pady=10)
输出目录按钮 = tk.Button(根窗口, text="浏览", command=选择输出目录)
输出目录按钮.grid(row=1, column=2, padx=10, pady=10)

# 转换按钮
转换按钮 = tk.Button(根窗口, text="转换文件", command=转换文件)
转换按钮.grid(row=2, column=1, padx=10, pady=10)

# 运行主循环
根窗口.mainloop()