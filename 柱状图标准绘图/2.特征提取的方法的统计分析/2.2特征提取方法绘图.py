import pandas as pd
import matplotlib.pyplot as plt

# 设置字体为 New Roman
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['axes.unicode_minus'] = False  # 处理负号显示

def load_data(csv_file):
    """加载CSV文件并返回DataFrame。"""
    return pd.read_csv(csv_file)

def map_methods(df, method_mapping):
    """将DataFrame中的特征提取方法替换为其英文缩写。"""
    df['Feature Extraction Method'] = df['特征提取方法'].map(method_mapping)
    return df

def count_method_occurrences(df):
    """统计每种特征提取方法的出现次数。"""
    return df['Feature Extraction Method'].value_counts()

def plot_method_occurrences(method_counts, output_image):
    """绘制特征提取方法的出现次数并保存图像。"""
    colors = ['#87CEEB', '#90EE90', '#FF7F50', '#FFD700', '#FF69B4',
              '#E6E6FA', '#FFB6C1', '#FFFACD', '#FFA07A',
              '#20B2AA', '#B0E0E6', '#D3D3D3', '#ADD8E6']

    plt.figure(figsize=(14, 8))
    bars = method_counts.plot(kind='bar', color=[colors[i] for i in range(len(method_counts))], edgecolor='black')
    plt.title('Feature Extraction Method Occurrence Statistics', fontsize=18, fontweight='bold')
    plt.xlabel('Feature Extraction Method', fontsize=14)
    plt.ylabel('Occurrence Count', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)

    # 在每个柱上方添加文本注释
    for i, count in enumerate(method_counts):
        plt.text(i, count + 0.1, str(count), ha='center', fontsize=12, fontweight='bold')

    # 创建完整的方法名称映射以用于图例
    full_method_names = {
        'HFEM': 'Hybrid Feature Extraction Method',
        'CSP': 'CSP',
        'M-CSP': 'Modified CSP',
        'OM': 'Other Methods',
        'M-WT': 'Modified Wavelet Transform',
        'CNN': 'Convolutional Network',
        'PSD': 'PSD',
        'OT': 'Other Transforms',
        'A8': 'A8',
        'M-AR': 'Modified AR',
        'DWT': 'DWT',
        'ICA': 'ICA',
        'M-PSD': 'Modified PSD'
    }

    # 创建图例并放置在柱状图外部
    legend_elements = [plt.Line2D([0], [0], color=color, lw=4, label=full_method_names[method])
                       for method, color in zip(full_method_names.keys(), colors)]

    plt.legend(handles=legend_elements, title='Feature Extraction Methods', loc='upper left', fontsize=12, markerscale=1.5, bbox_to_anchor=(1, 1))

    # 调整边距，以确保图例显示
    plt.subplots_adjust(right=0.75)  # 右边距调整为75%

    plt.savefig(output_image, bbox_inches='tight')  # 保存图像时调整边界
    plt.close()  # 关闭图形

def main():
    csv_file = r'C:\Users\pc\Desktop\cjh 10.8\数据预处理版本二分类数据信息.csv'
    output_image = r'C:\Users\pc\Desktop\cjh 10.8\2.特征提取的方法的统计分析\Feature_Extraction_Method_Occurrence_Statistics.png'

    method_mapping = {
        '混合特征提取方法': 'HFEM',
        'CSP': 'CSP',
        '改良CSP': 'M-CSP',
        '其他方法': 'OM',
        '改良小波变换': 'M-WT',
        '卷积网络': 'CNN',
        'PSD': 'PSD',
        '其他变换': 'OT',
        'A8': 'A8',
        '改良AR': 'M-AR',
        'DWT': 'DWT',
        'ICA': 'ICA',
        '改良PSD': 'M-PSD'
    }

    df = load_data(csv_file)
    df = map_methods(df, method_mapping)
    method_counts = count_method_occurrences(df)
    plot_method_occurrences(method_counts, output_image)

    print(f"图表已保存到: {output_image}")

if __name__ == "__main__":
    main()
