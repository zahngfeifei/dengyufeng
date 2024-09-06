import os
import mne
import tkinter as tk
from tkinter import filedialog, Listbox, END

def read_channels_from_txt(txt_file):
    """读取 .txt 文件中的通道名称"""
    try:
        with open(txt_file, 'r') as file:
            channels = [line.strip() for line in file if line.strip()]
    except Exception as e:
        print(f"读取 {txt_file} 时出错: {e}")
        channels = []
    return channels

def select_channels_from_fif(fif_file, channels):
    """读取 .fif 文件并选择通道"""
    try:
        raw = mne.io.read_raw_fif(fif_file, preload=True)
        available_channels = raw.info['ch_names']
        channels_to_pick = [ch for ch in channels if ch in available_channels]
        raw.pick_channels(channels_to_pick)
    except Exception as e:
        print(f"处理 {fif_file} 时出错: {e}")
        raw = None
    return raw

def save_filtered_fif(raw, output_file):
    """保存处理后的数据到新的 .fif 文件"""
    if raw is not None:
        try:
            raw.save(output_file, overwrite=True)
        except Exception as e:
            print(f"保存 {output_file} 时出错: {e}")

def process_fif_files(input_dir, output_dir, txt_dir, listbox_txt, listbox_fif, listbox_mapping):
    """批量处理目录中的 .fif 文件"""
    txt_files = sorted([f for f in os.listdir(txt_dir) if f.endswith('.txt')])
    fif_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.fif')])

    if len(txt_files) != len(fif_files):
        print("警告: txt 文件和 fif 文件数量不匹配，无法一一对应。")
        return

    for i in range(len(txt_files)):
        txt_filename = txt_files[i]
        fif_filename = fif_files[i]

        txt_file = os.path.join(txt_dir, txt_filename)
        fif_filepath = os.path.join(input_dir, fif_filename)
        output_file = os.path.join(output_dir, fif_filename.replace('.fif', '_filtered.fif'))

        channels = read_channels_from_txt(txt_file)
        listbox_txt.insert(END, txt_filename)

        print(f"正在处理 {fif_filepath} 和 {txt_file}...")
        raw = select_channels_from_fif(fif_filepath, channels)
        save_filtered_fif(raw, output_file)
        print(f"已将过滤后的数据保存到 {output_file}")

        # 在Listbox中展示处理的文件
        listbox_fif.insert(END, fif_filename)
        listbox_mapping.insert(END, f"{txt_filename} -> {fif_filename}")

def select_directory(label):
    """选择目录"""
    directory = filedialog.askdirectory()
    if directory:
        label.config(text=directory)
    return directory

def run_processing(txt_label, input_label, output_label, listbox_txt, listbox_fif, listbox_mapping):
    txt_dir = txt_label.cget("text")
    input_dir = input_label.cget("text")
    output_dir = output_label.cget("text")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    process_fif_files(input_dir, output_dir, txt_dir, listbox_txt, listbox_fif, listbox_mapping)

def main():
    # 初始化主窗口
    root = tk.Tk()
    root.title("EEG 通道选择处理器")

    # 定义标签和按钮
    tk.Label(root, text="TXT 目录:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
    txt_label = tk.Label(root, text="", width=50, anchor="w")
    txt_label.grid(row=0, column=1, padx=10, pady=5)
    tk.Button(root, text="浏览", command=lambda: select_directory(txt_label)).grid(row=0, column=2, padx=10, pady=5)

    tk.Label(root, text="输入 FIF 目录:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    input_label = tk.Label(root, text="", width=50, anchor="w")
    input_label.grid(row=1, column=1, padx=10, pady=5)
    tk.Button(root, text="浏览", command=lambda: select_directory(input_label)).grid(row=1, column=2, padx=10, pady=5)

    tk.Label(root, text="输出目录:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
    output_label = tk.Label(root, text="", width=50, anchor="w")
    output_label.grid(row=2, column=1, padx=10, pady=5)
    tk.Button(root, text="浏览", command=lambda: select_directory(output_label)).grid(row=2, column=2, padx=10, pady=5)

    # Listbox显示加载的txt文件
    listbox_txt = Listbox(root, width=80, height=5)
    listbox_txt.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

    # Listbox显示加载的fif文件
    listbox_fif = Listbox(root, width=80, height=5)
    listbox_fif.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

    # Listbox显示txt文件和fif文件的对应关系
    listbox_mapping = Listbox(root, width=80, height=10)
    listbox_mapping.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

    # 开始处理的按钮
    tk.Button(root, text="开始处理", command=lambda: run_processing(txt_label, input_label, output_label, listbox_txt, listbox_fif, listbox_mapping)).grid(row=6, column=0, columnspan=3, padx=10, pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()