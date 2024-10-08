import pandas as pd

# 指定Excel文件的路径
file_path = r'C:\Users\dengyufeng\Desktop\cjh-mate分析\数据预处理版本二分类数据信息.xlsx'

# 读取Excel文件
df = pd.read_excel(file_path, sheet_name='Sheet1', skiprows=2, nrows=5, usecols=[0, 2], parse_dates=[0])

# 显示前5行数据
print(df)
