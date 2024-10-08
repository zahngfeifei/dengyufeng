import pandas as pd

# 读取CSV文件
csv_file = r'C:\Users\dengyufeng\Desktop\cjh-mate分析\数据预处理版本二分类数据信息.csv'
df = pd.read_csv(csv_file)

# 展示列名称
print("CSV文件的列名称：")
print(df.columns)
