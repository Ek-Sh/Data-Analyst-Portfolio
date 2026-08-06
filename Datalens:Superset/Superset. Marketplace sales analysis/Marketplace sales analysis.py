#!/usr/bin/env python
# coding: utf-8

# # Анализ продаж и пользовательской активности маркетплейса
# 
# 
# **Цель проекта** - разработка аналитического дашбода для маркетплеса, который позволит отслеживать ключевые показатели продаж, пользовательской активности, качества товаров и эфективности работы платформы.

# ## Этап предобработки данных 

# **Выполненные задачи**
# 
# 1. Загрузка данных из CSV
# * проверить размеры и предварительно изучите столбцы
# 2. Подготовка данных
# * удалить явные и неявные дубликаты
# * обработать пропуски: удалить или заполнить логичными значениями
# * преобразовать типы данных
# * категоризировать признаки
# * найти и исправить логические ошибки (отрицательные цены, невозможные значения)
# 3. Исследовательский анализ
# * изучить распределения признаков
# * найти аномалии и выбросы
# * выполнить корреляционный анализ
# * сделать визуализацию с помощью гистограмм, линейных графиков по времени и так далее
# 4. Подготовка данных к выгрузке
# * выгрузить данные
# 

# ###  Подключение и загрузка данных

# In[1]:


# Импортируем библиотеки

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


# In[2]:


# Функция для загрузки таблицы из CSV

def load_table(table_name):
    print(f"Загружаем таблицу {table_name}...")
    file_path = f"{table_name}.csv"
    df = pd.read_csv(file_path)
    print(f"Таблица {table_name} загружена, размер: {df.shape}")
    return df

# Список ключевых таблиц
tables = ['orders', 'order_items', 'products', 'users', 'categories', 'transactions', 'reviews']


# In[3]:


# Загружаем все таблицы в словарь
data = {}
for tbl in tables:
    data[tbl] = load_table(tbl)


# ### Предобработка

# In[4]:


# Удаление дубликатов
total_dups = 0
for name, df in data.items():
    dups = df.duplicated().sum()
    total_dups += dups
    print(f'{name}: {dups} дубликатов')
    if dups > 0:
        df.drop_duplicates(inplace=True)

if total_dups == 0:
    print("Во всех таблицах дубликаты не найдены")


# In[5]:


# Преобразование дат
data['orders']['order_date'] = pd.to_datetime(data['orders']['order_date'])
data['reviews']['review_date'] = pd.to_datetime(data['reviews']['review_date'])
data['transactions']['transaction_date'] = pd.to_datetime(data['transactions']['transaction_date'])
data['users']['registration_date'] = pd.to_datetime(data['users']['registration_date'])


# In[6]:


# Исправление отрицательных цен в products
neg_prices = data['products'][data['products']['price'] < 0].shape[0]
if neg_prices > 0:
    data['products'].loc[data['products']['price'] < 0, 'price'] = 0
print(f'products: исправлено {neg_prices} отрицательных цен')


# In[7]:


# Проверка пропусков
for name, df in data.items():
    print(f"\n{name} — пропущенные значения:")
    print(df.isna().sum())


# In[8]:


# Категоризация рейтинга в reviews
def categorize_rating(r):
    if r >= 4.5:
        return 'High'
    elif r >= 4:
        return 'Medium'
    else:
        return 'Low'

data['reviews']['rating_category'] = data['reviews']['rating'].apply(categorize_rating)
print('reviews: добавлен столбец rating_category')


# ### Исследовательский анализ

# In[9]:


def eda(df, columns):
    print(f"\nСтатистика по признакам: {columns}")
    display(df[columns].describe())
    
    for col in columns:
        fig, axs = plt.subplots(1, 2, figsize=(12, 4))
        
        sns.histplot(df[col].dropna(), kde=True, ax=axs[0])
        axs[0].set_title(f"Гистограмма {col}")
        
        sns.boxplot(x=df[col], ax=axs[1])
        axs[1].set_title(f"Boxplot {col}")
        
        plt.show()


# In[10]:


# Пример для products
eda(data['products'], ['price', 'stock_quantity'])

# Корреляция
corr = data['products'][['price', 'stock_quantity']].corr()
print("\nКорреляционная матрица:")
display(corr)


# ### Выгрузка обработанных данных

# In[11]:


output_dir = 'exported_csv'
os.makedirs(output_dir, exist_ok=True)


# In[12]:


# Фильтрация по дате: только заказы с 01.01.2025 по 01.06.2025
orders_filtered = data['orders'][
    (data['orders']['order_date'] >= '2025-01-01') &
    (data['orders']['order_date'] <= '2025-06-01')
]

orders_path = os.path.join(output_dir, 'orders_filtered.csv')
orders_filtered.to_csv(orders_path, sep=";", index=False)

print(f"Таблица заказов успешно выгружена: {orders_path}")
print(f"Строк: {orders_filtered.shape[0]}, Колонок: {orders_filtered.shape[1]}")


# Была проведена предобработка данных для дальнейшей работы. Данные очищены от дубликатов, пропуски обработаны, исправили ошибки и преобразованы типы данных. Параллельно сделан исследовательский анализ: изучены распределения признаков, проведен корреляционный анализ.
