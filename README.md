# comexp_test

Цель: мини-сервис, предоставляющий возможность загрузить и обработать видео из разных источников. 
сделано API для трёх источников
- для загрузки файлов, 
- загрузки youtube-видео
- записи стрима на странице http://www.freeintertv.com/view/id-1099  Стрим разбивается на видеофрагменты определенной длины. Входные параметры: общая длительность записи и длительность видеофрагмента

Реализовано при помощи разделения API и обработчиков в разных docker-контейнерах взаимодействующих при помощи сelery 

## Структура
```bash
project
|   main.py       - скрипт реализующий API создания задач и постановки их в очередь + минимальный веб интерфейс для него
|   worker.py     - основной файл реализующий обработку очереди, загрузка файлов и потока 
|   download_stream_worker.py - скрипт для загрузки потока из командной строки в контейнере обработчика или сервера 
|   static        - веб интерфейс
|   templates     - и статика для него
|   downloads     - папка для загрузки видео
|   logs          - логи celery 
```

## загрузка потока
``` ./download_stream_worker.py [-h] [-r RECORDING_DURATION] [-f MAX_FRAGMENT_DURATION] playlist_url ```


# Что бы хотелось еще сделать
- переделать обработку очереди, на асинхронную работу 
- добавить базу для сохранения результатов 
- добавить нормальное взаимодействие с файловым хранилищем 
- в рамках теста все грузится в одну папку, без нормализации имен и проверки на дублирующиеся файлы 
- добавить тесты 