import mne
import numpy as np

# 读取EEG数据
file_path = "C:/Users/pc/Desktop/自适应liang/5.剔除坏道后的数据/sub-01_task-motor-imagery_eeg_filtering_marked_tichu.fif"
raw = mne.io.read_raw_fif(file_path, preload=True)

# 获取数据
data = raw.get_data()

# 计算每个通道的均值和标准差
means = np.mean(data, axis=1, keepdims=True)
stds = np.std(data, axis=1, keepdims=True)

# 进行Z-score标准化
normalized_data = (data - means) / stds

# 将标准化后的数据放回Raw对象
raw._data = normalized_data

# 保存标准化后的数据到新的文件
output_file_path = r"C:\Users\pc\Desktop\自适应liang\去除共线性\1.fif"
raw.save(output_file_path, overwrite=True)

print("数据标准化完成，并保存到新的文件中。")