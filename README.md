# Реестр ПО

## Описание

Проект на данном этапе находится в стадии разработки. Проект предназначен для
сохранения всей необходимой информации о ПО в базе данных. В дальнейшем будет
реализована печать отчетов. Для каждого разработанного ПО можно открыть историю
доработок.

## Чек-лист

- [x] База данных;

- [x] Интерфейс приложения;

- [x] CRUD операции;

- [ ] Резервное копирование файла БД;

- [ ] Логирование;

- [ ] Сортировка и фильтрация;

- [ ] Печать отчета в Excel.

## Технологии

- Python 3.9;
- SQLite3;
- Tkinter.

## Запуск проекта

- Установите и активируйте виртуальное окружение

- Установите зависимости из файла requirements.txt

```text
pip install -r requirements.txt
```

- В корне проекта создайте базу данных:

```text
python create_db.py
```

- В корне проекта выполните команду:

```text
python software_registry.py
```

- Или если установлен GNU Make (На MacOS и Linux он уже установлен), то из
папки проекта выполните команду:

```text
make run
```

## Автор

Пилипенко Артем
