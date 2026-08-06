#!/usr/bin/env python
# coding: utf-8

# # Анализ пользовательского поведения в сервисе Яндекс Книги
# 
# ## Описание и цель проекта
# В проекте проведен анализ данных о том, как пользовавзаимодействуют с контентом сервиса Яндекс книги. Исследуется, какие типы контента выбирают пользователи, сколько времения тратят на чтение и прослушивание, а также как меняется их поведение в будни и выходные. Отдельно рассмотрено влияние типа контента (взрослого и детского) на ссумарное время потребления. 
# 
# Результаты анализа помогут лучше понять предпочтения пользователей и могут быть использованы для улучшения рекомендаций и развития сервиса.
# 
# ## Опиание данных
# **Таблица bookmate.audition** - содержит данные об активности пользователей
# 
# 
# **Таблица bookmate.content** - описание контента
# 
# ## Ход исследования: 
# 1. Загрузить и изучить исходные таблицы с данными о контенте и пользователях
# 2. Проверить структуру и типы данных.
# 3. Выолнить преобразования: добавить расчетные столбцы, изменить типы данных.
# 4. Объединить таблицы по идентификатору контента, удалить лишние столбцы. 
# 5. Сформулировать выводы
# 

# 
# # Работа с данными бизнеса в PySpark

# ## Загрузка данных и знакомство с ними

# In[1]:


# Выгружаем данные
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

audition_df = spark.read.csv("audition.csv", header=False, inferSchema=True)
content_df = spark.read.csv("content.csv", header=False, inferSchema=True)

audition_df.show(10, truncate=False)
content_df.show(10, truncate=False)


# Чтение файла выполнено без загаловка. 
# Предполагаемая структура таблиц из заадния содержит 11 столбцов для таблицы audition и 6 для таблицы content, описание столбцов и их порядок приведены в описании.
# 
# При чтении файлов выявлено расхождение на два столбца в таблице  audition и в порядке столбцов в таблице content.
# 

# In[2]:


audition_df = audition_df.toDF(
    "n",
    "audition_id",
    "puid",
    "usage_platform_ru",
    "msk_business_dt_str",
    "app_version",
    "adult_content_flg",
    "hours",
    "hours_sessions_long",
    "kids_content_flg",
    "main_content_id",
    "usage_geo_id_name",
    "usage_country_name"
)

audition_df = audition_df.drop("n")

audition_df.printSchema()
audition_df.show(10, truncate=False)


# In[3]:


content_df = content_df.toDF(
    "main_content_id",
    "main_content_type",
    "main_content_name",
    "main_content_duration_hours",
    "published_topic_title_list",
    "main_author_id"
)

content_df.show(10, truncate=False)


# Заголовки присвоены вручную, в таблице audition удален первый столбец. 

# In[4]:


# просмотр схем
audition_df.printSchema()
content_df.printSchema()


# количество строк
audition_count = audition_df.count()
content_count = content_df.count()

print("audition rows:", audition_count)
print("content rows:", content_count)


# Разница в объемах ожидаема. Таблица audition  значительно больше таблицы content, потому что первая таблица фиксирует множество событий, тогда как вторая является справочников с описанием объектов контента. 

# ## Трансформация и преобразование таблиц

# In[5]:


from pyspark.sql import functions as F

audition_df = (
    audition_df
    .withColumn(
        "minutes_sessions_long",
        (F.col("hours_sessions_long") * 60).cast("int")
    )
    .withColumn(
        "event_date",
        F.to_date(F.col("msk_business_dt_str"), "yyyy-MM-dd")
    )
    .withColumn(
        "is_weekend",
        F.dayofweek(F.col("event_date")).isin([1, 7])
    )
)

audition_df_new = audition_df.select(
    "puid",
    "hours_sessions_long",
    "minutes_sessions_long",
    "is_weekend"
).show(10, truncate=False)

К датафрейму добавлено несколько столбцов для анализа потребления контента в зависимости 
от дня недели и возростных ограничений
# In[6]:


# Сумма minutes_sessions_long для выходных и будней 

weekend_totals = (
    audition_df
    .groupBy("is_weekend")
    .agg(F.sum("minutes_sessions_long").alias("total_minutes"))
    .orderBy("is_weekend")
)

weekend_totals.show(truncate=False)


# По результатам видно, что в будни суммарное время потребления контента выше - 17 995 153 минут, против6 598 993 минут в выходные. Из этого можно сделать вывод, что основная активность приходится на рабочие дни, в выходные потребление контента значительно ниже.
# 
# Вероятно, в  рабочие днисервис чаще используют, как ругулярную часть повседневной активности, в выходные реже или более короткими сессиями.

# In[7]:


# Аналогично по adult_content_flg и is_weekend, без пропусков 
adult_weekend_totals = (
    audition_df
    .groupBy("adult_content_flg", "is_weekend")
    .agg(F.sum("minutes_sessions_long").alias("total_minutes"))
    .dropna()
    .orderBy("adult_content_flg", "is_weekend")
)

adult_weekend_totals.show(truncate=False)


# Потребление контента значительно смещенов сторону взрослого контента, на него приходится большая доля, при этом сохраняется пропорцианальное деления длитильности активности в будни, этот патерн не зависит от возростных ограничений. Сегмент потребления детского контента заметно меньше, это может стать зоной роста, если есть цель диверсифицировать аудиторию.
# 
# В общих чертах можно сказать, что сервис используют преимущественно в повседневных сценариях. Но также результаты указывают на высокую зависимость вовлеченности от "взрослого" сегмента.

# ## Соединение таблиц

# In[8]:


# Соединяем таблицы

from pyspark.sql import functions as F

merged_df = audition_df.join(content_df, on="main_content_id", how="inner")

print("rows after join:", merged_df.count()) 
merged_df.show(5, truncate=False)


# In[9]:


#Удаляем лишних столбцов

merged_df = merged_df.drop("main_author_id", "app_version", "usage_geo_id")

merged_df.show(5, truncate=False)


# Объеденины две таблицы и удалены лишние столбцы: main.author_id, app_version, usage_geo_id

# In[10]:


# Считаем уникальных пользователей 

merged_users = merged_df.select("puid").distinct().count()
audition_users = audition_df.select("puid").distinct().count()

print("unique users in merged_users:", merged_users) 
print("unique users in audition_users:", audition_users) 


# Количество уникальных ползователей в объединенной таблице меньше, чем в исходной, потому что при объединении сохранились только строки с найденным соответствием в content_df. Таким образом 53 пользователя не включены в финальную таблицу из-за отсутствия совпадений. 
