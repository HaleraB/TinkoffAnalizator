# TinkoffAnalizator
Создано для Сириус.ИИ 2024

Данный проект представлен граф-приложением в котором присутсвует:

-меню бар с кнопками "файл" и "настройки": "файл" - открыть/сохранить, "настройки" - настроить кол-во получаемых отзывов и страницу с которой начать их парсинг([для сравниру](https://www.sravni.ru/bank/tinkoff-bank/otzyvy/) и [банкиру](https://www.banki.ru/services/responses/bank/tcs/))

-кнопка "Собрать отзывы" и круговая диаграмма - при нажатии происходит парсинг, в ходе которого мы получаем отзывы и происходит загрузка диаграммы на которой мы видим соотношение положительных и отрицательных отзывов

-кнопка "Проанализировать отзывы" и лист-виджет - при нажатии кнопки начинается анализ отзывов и в конце в лист-виджете отображаются итоги анализа

-кнопка "Найти схожие отзывы", лист-виджет и поля ввода - при нажатии происходит обработка ввода пользователя и вывод наиболее похожих отзывов на веденный пользователем


/app/App.py - главный файл
/app/settings/settings.json - json-файл с настройками
/requirements.txt - файл с библиотеками

# Внимание: иногда могут быть зависания, т.к. идёт обработка больших данных. Так же первый запуск будет долгим, т.к. для работы будет устанавливаться ru-модель для fasttext 
