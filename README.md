# hw05_final

### Описание

Cоциальная сеть для публикации личных дневников. Можно создавать свои посты, комментировать их и подписываться на других авторов.

### Технологии

- Python 3.8.10
- Django 2.2.16

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/KlementevaE/hw05_final.git
```

```
cd hw05_final

```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
cd yatube
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Автор

Клементьева Евгения
