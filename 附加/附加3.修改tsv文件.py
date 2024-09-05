import pandas as pd

# 定义输入和输出文件路径
input_file = r'C:\Users\pc\Desktop\自适应liang\task-motor-imagery_events.tsv'
output_file = r'C:\Users\pc\Desktop\自适应liang\merged_trials1.tsv'

# 读取 TSV 文件并选择需要的列
df = pd.read_csv(input_file, sep='\t')
selected_columns = ['onset', 'duration', 'trial_type']
df_selected = df[selected_columns]

# 初始化变量
merged_trials = []
current_trial_type = None
current_onset = None
current_duration = 0
trial_count = 0

# 遍历每一行
for index, row in df_selected.iterrows():
    if row['trial_type'] == current_trial_type:
        # 累加 duration
        current_duration += row['duration']
        trial_count += 1

        # 当累积到三个相同 trial_type 时，保存结果
        if trial_count == 3:
            merged_trials.append([current_onset, current_duration, current_trial_type])
            current_trial_type = None
            current_onset = None
            current_duration = 0
            trial_count = 0
    else:
        # 保存前一个 trial_type 的累积结果
        if current_trial_type is not None:
            merged_trials.append([current_onset, current_duration, current_trial_type])

        # 重置为当前行的值
        current_trial_type = row['trial_type']
        current_onset = row['onset']
        current_duration = row['duration']
        trial_count = 1

# 保存最后的累积结果
if current_trial_type is not None and trial_count == 3:
    merged_trials.append([current_onset, current_duration, current_trial_type])

# 转换为 DataFrame 并保存为新的 TSV 文件
merged_df = pd.DataFrame(merged_trials, columns=['onset', 'duration', 'trial_type'])
merged_df.to_csv(output_file, sep='\t', index=False)

print(f"Merged trials saved to '{output_file}'")