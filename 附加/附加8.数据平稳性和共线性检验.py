import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import mne
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
import matplotlib.pyplot as plt

class EEGAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EEG数据分析器")

        # 创建GUI组件
        self.create_widgets()

    def create_widgets(self):
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="打开", command=self.load_files)
        filemenu.add_command(label="保存", command=self.save_results)
        menubar.add_cascade(label="文件", menu=filemenu)
        self.root.config(menu=menubar)

        # 创建列表框用于展示加载的数据
        self.listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE, width=100, height=20)
        self.listbox.pack(pady=20)

        # 创建按钮用于处理数据
        process_button = tk.Button(self.root, text="处理数据", command=self.process_data)
        process_button.pack(pady=10)

        # 创建按钮用于设置保存地址
        save_path_button = tk.Button(self.root, text="设置保存地址", command=self.set_save_path)
        save_path_button.pack(pady=10)

        # 保存路径
        self.save_path = None

    def load_files(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("FIF files", "*.fif")])
        for file_path in file_paths:
            self.listbox.insert(tk.END, file_path)

    def set_save_path(self):
        self.save_path = filedialog.askdirectory()
        if self.save_path:
            messagebox.showinfo("保存地址", f"保存地址已设置为: {self.save_path}")

    def process_data(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "请选择要处理的数据文件")
            return

        if not self.save_path:
            messagebox.showwarning("警告", "请先设置保存地址")
            return

        for index in selected_indices:
            file_path = self.listbox.get(index)
            try:
                raw = mne.io.read_raw_fif(file_path, preload=True)
                data = raw.get_data()
                channel_names = raw.info['ch_names']

                # 进行ADF检验
                adf_results = {}
                for i, channel in enumerate(channel_names):
                    channel_data = data[i]
                    adf_result = adfuller(channel_data)
                    adf_stat, p_value, used_lag, n_obs, critical_values, icbest = adf_result
                    adf_results[channel] = {
                        'ADF Statistic': adf_stat,
                        'p-value': p_value,
                        'Critical Values': critical_values
                    }

                # 计算VIF
                df = pd.DataFrame(data.T, columns=channel_names)
                df_with_const = add_constant(df)
                vif_data = pd.DataFrame()
                vif_data["features"] = df_with_const.columns
                vif_data["VIF Factor"] = [variance_inflation_factor(df_with_const.values, i) for i in range(df_with_const.shape[1])]

                # 保存结果
                self.save_results(file_path, adf_results, vif_data)
            except Exception as e:
                messagebox.showerror("错误", f"处理文件 {file_path} 时发生错误: {e}")

    def save_results(self, file_path, adf_results, vif_data):
        if not self.save_path:
            messagebox.showwarning("警告", "请先设置保存地址")
            return

        file_name = file_path.split('/')[-1].split('.')[0]
        save_path = f"{self.save_path}/{file_name}_results.txt"

        with open(save_path, 'w') as f:
            f.write(f"文件: {file_path}\n")
            f.write("ADF检验结果:\n")
            for channel, result in adf_results.items():
                f.write(f'通道 {channel}:\n')
                f.write(f'  ADF 统计量: {result["ADF Statistic"]:.6f}\n')
                f.write(f'  p值: {result["p-value"]:.6f}\n')
                f.write(f'  临界值: 1%: {result["Critical Values"]["1%"]:.6f}, 5%: {result["Critical Values"]["5%"]:.6f}, 10%: {result["Critical Values"]["10%"]:.6f}\n')
                if result["p-value"] < 0.05:
                    f.write('  数据平稳\n')
                else:
                    f.write('  数据非平稳\n')

            f.write("\nVIF结果:\n")
            for index, row in vif_data.iterrows():
                f.write(f'特征 {row["features"]} 的 VIF 值: {row["VIF Factor"]:.6f}\n')
                if row["VIF Factor"] > 10:
                    f.write('  存在较强的共线性\n')
                else:
                    f.write('  共线性较低\n')

        messagebox.showinfo("保存成功", f"结果已保存到: {save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EEGAnalyzerApp(root)
    root.mainloop()