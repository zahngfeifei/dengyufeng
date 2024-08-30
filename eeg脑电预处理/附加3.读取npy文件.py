import tkinter as tk
from tkinter import filedialog, Text
import numpy as np

class NpyReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NPY文件阅读器")

        self.label = tk.Label(root, text="选择一个.npy文件来读取:")
        self.label.pack(pady=10)

        self.browse_button = tk.Button(root, text="浏览", command=self.browse_file)
        self.browse_button.pack(pady=5)

        self.text_widget = Text(root, wrap=tk.NONE, width=80, height=20)
        self.text_widget.pack(pady=10)

    def browse_file(self):
        # 打开文件选择对话框，选择一个.npy文件
        file_path = filedialog.askopenfilename(filetypes=[("NPY文件", "*.npy")])
        if file_path:
            data = np.load(file_path)
            self.display_data(data)

    def display_data(self, data):
        # 清空文本框
        self.text_widget.delete(1.0, tk.END)

        # 显示数组的形状
        shape_str = f"形状: {data.shape}\n"
        self.text_widget.insert(tk.END, shape_str)

        # 显示数组的数据类型
        dtype_str = f"数据类型: {data.dtype}\n"
        self.text_widget.insert(tk.END, dtype_str)

        # 显示数组的前几行数据
        data_str = np.array2string(data, separator=', ', threshold=10)
        self.text_widget.insert(tk.END, "数据:\n")
        self.text_widget.insert(tk.END, data_str)

if __name__ == "__main__":
    root = tk.Tk()
    app = NpyReaderApp(root)
    root.mainloop()