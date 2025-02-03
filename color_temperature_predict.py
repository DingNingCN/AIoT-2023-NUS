import numpy as np
import pandas as pd
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# 读取数据
data = pd.read_csv('../data/filtered_data.csv')

# 打印值的分布情况
# print("Temp数据分布情况:")
# print(data['Temp'].value_counts())
# print()
#
# print("Humidity数据分布情况:")
# print(data['humidity'].value_counts())
# print()
#
# print("PM2.5数据分布情况:")
# print(data['pm2.5'].value_counts())
# print()

# 绘制直方图
# plt.figure(figsize=(12, 4))
#
# plt.subplot(1, 3, 1)
# sns.histplot(data['Temp'], kde=True)
# plt.xlabel('Temp')
# plt.title('Distribution of Temp')
#
# plt.subplot(1, 3, 2)
# sns.histplot(data['humidity'], kde=True)
# plt.xlabel('Humidity')
# plt.title('Distribution of Humidity')
#
# plt.subplot(1, 3, 3)
# sns.histplot(data['pm2.5'], kde=True)
# plt.xlabel('PM2.5')
# plt.title('Distribution of PM2.5')
#
# plt.tight_layout()
# plt.show()

temp = ctrl.Antecedent(np.arange(22.5, 33, 0.5), 'temp')
temp['t1'] = fuzz.gaussmf(temp.universe, 22.5, 2)
temp['t2'] = fuzz.gaussmf(temp.universe, 28, 2)
temp['t3'] = fuzz.gaussmf(temp.universe, 33, 2)
# print(data['Temp'].mean())

humidity = ctrl.Antecedent(np.arange(40, 100+1, 1), 'humidity')
humidity['h1'] = fuzz.gaussmf(humidity.universe, 40, 3.5)
humidity['h2'] = fuzz.gaussmf(humidity.universe, 80, 3.5)
humidity['h3'] = fuzz.gaussmf(humidity.universe, 100, 3.5)
# print(data['humidity'].mean())

pm25 = ctrl.Antecedent(np.arange(10, 130+1, 1), 'pm25')
pm25['p1'] = fuzz.gaussmf(pm25.universe, 10, 5)
pm25['p2'] = fuzz.gaussmf(pm25.universe, 53, 5)
pm25['p3'] = fuzz.gaussmf(pm25.universe, 130, 5)
#print(data['pm2.5'].mean())

c_temp = ctrl.Consequent(np.arange(3000, 6001, 1), 'c_temp')
c_temp['c1'] = fuzz.trimf(c_temp.universe, [3500, 3500, 4500])  # 低色温
c_temp['c2'] = fuzz.trimf(c_temp.universe, [4500, 5500, 6500])  # 中色温
c_temp['c3'] = fuzz.trimf(c_temp.universe, [5500, 6500, 6500])  # 高色温

# 定义模糊规则
rule1 = ctrl.Rule(temp['t1'], c_temp['c1'])
rule2 = ctrl.Rule(temp['t2'] & (humidity['h3'] | pm25['p3']), c_temp['c1'])
rule3 = ctrl.Rule(temp['t2'] & ((~humidity['h3'] & ~pm25['p3']) & (~(humidity['h1'] & pm25['p1']))), c_temp['c2'])
rule4 = ctrl.Rule(temp['t2'] & (humidity['h1'] & pm25['p1']), c_temp['c2'])
rule5 = ctrl.Rule(temp['t3'] & ((humidity['h3'] & pm25['p2']) | (humidity['h3'] & pm25['p3']) | (humidity['h2'] & pm25['p3'])), c_temp['c1'])
rule6 = ctrl.Rule(temp['t3'] & ((humidity['h3'] & pm25['p1']) | (humidity['h1'] & pm25['p3'])), c_temp['c2'])
rule7 = ctrl.Rule(temp['t3'] & ((humidity['h1'] & pm25['p2']) | (humidity['h2'] & pm25['p1']) | (humidity['h1'] & pm25['p1']) | (humidity['h2'] & pm25['p2'])), c_temp['c3'])


# 定义控制系统
system = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7])
prediction = ctrl.ControlSystemSimulation(system)

# 保存模型
filename = 'fuzzy_model.pkl'
joblib.dump(system, filename)

# 输入数据并进行预测
# input_temp_values = np.arange(21, 34, 1)
# input_humidity_values = np.arange(40, 100, 3)
# input_pm25_values = np.arange(0, 130, 5)
#
# predictions = []
#
# for input_temp in input_temp_values:
#     for input_humidity in input_humidity_values:
#         for input_pm25 in input_pm25_values:
#             prediction.input['temp'] = input_temp
#             prediction.input['humidity'] = input_humidity
#             prediction.input['pm25'] = input_pm25
#
#             prediction.compute()
#             output_c_temp = prediction.output['c_temp']
#
#             predictions.append({'Temp': input_temp, 'Humidity': input_humidity, 'PM2.5': input_pm25, 'Color Temperature': output_c_temp})
#
# # 输出预测结果到文件
# predictions_df = pd.DataFrame(predictions)
# predictions_df.to_csv('prediction_results.csv', index=False)
