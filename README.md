# Yandex Transport Webdriver API

A "sort of API" to access Yandex Transport/Masstransit data, designed to work in conjunction with [YandexTransportProxy](https://github.com/OwlSoul/YandexTransportProxy).

Своеобразное "API" для доступа к данным Яндекс Транспорт (Masstransit API), предназначено для работы в паре с [YandexTransportProxy](https://github.com/OwlSoul/YandexTransportProxy).

*This project is for "Yandex.Maps" and "Yandex.Transport" services, so it's expected that majority of potential users are from Russian Federation, thus the README is written in russian language.*

## Предназначение проекта

Данное "API" позволяет автоматизировать получение данных от Яндекс.Транспорт Masstransit API (закрытого на данный момент для сторонних пользователей). Получить данные вроде "покажи координаты всего общественного транспорта в таком-то районе" или "выдай мне данные о координатах транспорта по всему городу в данный момент" с помощью этой штуковины просто так нельзя. Зато с ее помощью можно автоматизировать получение данных  по конкретной остановке, или по конкретному маршруту, и получить их именно в том формате в котором Яндекс их пересылает - здоровенные такие JSON-структуры (до 150 килобайт и больше). 

Полученные данные можно использовать для сбора статистики по конкретному маршруту, создания своего собственного табло для конкретной остановки, и автоматизации каких-либо событий на основе данных о транспорте (редко ходящий, но жизненно важный автобус вышел на маршрут - включаем будильник).

## Принцип работы

У каждой остановки или маршрута в Яндекс.Картах есть свой URL, узнать его просто, достаточно просто нажать на интересующую остановку/маршрут и посмотреть что будет в адресной строке.

### Примеры:

----

**Остановка "Метро Бауманская", Москва**:

https://yandex.ru/maps/213/moscow/?ll=37.678708%2C55.772438&masstransit%5BstopId%5D=stop__9643291&mode=stop&z=19

Здесь самая важная часть - "*masstransit[stopId]=stop__9643291*". Это ID нашей остановки, в целом достаточно только его, ссылка https://yandex.ru/maps/213/moscow/?masstransit[stopId]=stop__9643291 точно также будет работать в браузере.

----

**Маршрут "Трамвай Б", Москва**:

https://yandex.ru/maps/213/moscow/?ll=37.679549%2C55.772203&masstransit%5BrouteId%5D=B_tramway_default&masstransit%5BstopId%5D=stop__9643291&masstransit%5BthreadId%5D=BA_tramway_default&mode=stop&z=18

Здесь важная часть - *"masstransit[routeId]=B_tramway_default"*, и ссылка https://yandex.ru/maps/213/moscow/?masstransit%5BrouteId%5D=B_tramway_default точно так же будет работать в браузере.

----

Подобные URL и используются в работе данного API. Хотя с "короткими" URL проблем пока не было, на всякий случай параноидально рекомендуется использовать "длинные" API.

При выполнении этих запросов в браузере производятся несколько AJAX запросов, в которых приходит вся необходимая информация по транспорту, в формате JSON. За получение этих запросов и передачу в данный API отвечает [YandexTransportProxy](https://github.com/OwlSoul/YandexTransportProxy), данный же API является простой оболочкой, позволяющей выполнить, например вот такие вещи:

```
# Получение информации об остановке, прокси-сервер находится по адресу 127.0.0.1:25555
proxy = YandexTransportProxy('127.0.0.1', 25555)
stop_url = https://yandex.ru/maps/213/moscow/?ll=37.678708%2C55.772438&masstransit%5BstopId%5D=stop__9643291&mode=stop&z=19
result_json = proxy.getStopInfo(stop_url)
```

```
# Получение информации о маршруте и транспорте, прокси-сервер находится по адресу 127.0.0.1:25555
proxy = YandexTransportProxy('127.0.0.1', 25555)
stop_url = https://yandex.ru/maps/213/moscow/?masstransit%5BrouteId%5D=B_tramway_default
result_json_route = proxy.getRouteInfo(stop_url)
result_json_vehicles = proxy.getVehiclesInfo(stop_url)
```

Результатом подобных запросов будут как раз те самые данные в формате JSON, приходящие от Yandex Transport/Masstransit API. Примеры таких ответов можно посмотреть в [YandexTransportProxy wiki](https://github.com/OwlSoul/YandexTransportProxy/wiki).

Прокси-сервер [YandexTransportProxy](https://github.com/OwlSoul/YandexTransportProxy) реализует из себя очередь, где полученные от данного API команды выполняются в один поток, с определенной задержкой между запросами. Такое поведение заложено по дизайну, для максимального имитирования работы обычного пользователя, и снижения потенциальной нагрузки на сервера Яндекс (в том числе с целью избежания временного бана за слишком частые запросы, и мы не хотим его злить).

## Установка

Проект можно поставить через pip3:

```
pip3 install yandex-transport-webdriver-api
```

Либо просто скачав данную библиотеку из [релизов](https://github.com/OwlSoul/YandexTransportWebdriverAPI-Python/releases) или через "git clone".

Каких-то важных зависимостей у библиотеки нет, только стандартные библиотеки Python3.

Не забывайте, что для работы нужен запущенный и доступный по сети сервер [YandexTransportProxy](https://github.com/OwlSoul/YandexTransportProxy), хотя бы один (а можно и Kubernetes кластер из них сгородить).

## Реализованые функции
Функции для получения информации от Яндекс.Транспорта могут работать как в блокирующем (синхронном), так и в неблокирующем (асинхронном) режимах.

Функции данного API имеют общую структуру, виде get_something(params, query_id=None, blocking=True, timeout=0, callback=None)

Параметры, общие для всех функций:

* - query_id - строка (string),ID данного запроса, все ответы на него будут содержать данный ID. Важно для асинхронного режима, для синхронного можно опустить (сгенерируется автоматически случайным образом).
* - blocking - если **True**, функция блокирует до окончания выполнения, или до истечения таймаута (следующий параметр). Если **False** - функция завершается немедленно, и при каждом полученном ответе будет вызываться функция callback.
* - timeout, целое число (int), таймаут в секундах. Если в течении данного промежутка времени никакого ответа от сервера не будет получено, будет брошено исключение. Важно помнить что у прокси-сервера может быть приличный промежуток между выполнениями запросов, если указывается данный параметр. При значении = 0 таймаут не учитывается, и функция будет ждать бесконечно, или пока не придут данные сигнализирующие что "обработка запроса окончена, новых данных можн оне ждать".
* - callback - callback функция, будет вызываться каждый раз при получении данных в асинхронном режиме.

### get_echo (внутренняя команда - getEcho, функция Masstransit API - нет)
```get_echo(text, query_id=None, blocking=True, timeout=0, callback=None):```

Тестовая функция, помещает команду ```getEcho``` в очередь YandexTransportProxy, и возвращает переданную строку (text) при выполнении. Остальные функции построены по такому же принципу (особено в той части которая касается асинхронного режима).

Параметры:
* **text** - текст (string), который необходимо вернуть
* **query_id** - см. общие параметры для всех функций.
* **blocking** - см. общие параметры для всех функций.
* **timeout** - см. общие параметры для всех функций.
* **callback** - см. общие параметры для всех функций.

Пример использования, синхронный режим:

```
from yandex_transport_webdriver_api import YandexTransportProxy

# Прокси-сервер находится на 172.17.0.1:25555
proxy = YandexTransportProxy('172.17.0.1', 25555)
result = proxy.get_echo("Hello!")
print(result)
```

Результат: \
```Hello!```

Пример использования, асинхронный режим:

```
import time
from yandex_transport_webdriver_api import YandexTransportProxy

def callback_fun(data):
    print('Received', data)

# Прокси-сервер находится на 172.17.0.1:25555
proxy = YandexTransportProxy('172.17.0.1', 25555)
result = proxy.get_echo("Hello!", query_id='ID001', blocking=False, callback=callback_fun)
print("Async function terminated!")
# Пусть основной поток немного подождет. 
time.sleep(20)

```

Результат:
```
Async function terminated!
Received {'id': 'ID001', 'response': 'OK', 'queue_position': 0}
Received {'id': 'ID001', 'method': 'getEcho', 'error': 0, 'message': 'OK', 'expect_more_data': False, 'data': 'Hello!'}
```

При асинхронном режиме данные приходят в виде JSON, параметр data - словарь (dictionary), содержащий в себе весь результат: \
Первый ответ приходит сразу при успешном добавлении запроса в очередь на прокси-сервере.
```{'id': 'ID001', 'response': 'OK', 'queue_position': 0}```
Здесь:
* **id** - ID запроса, был передан при вызове get_echo
* **response** - ОК, если нет ошибок.
* **queue_position** - количество запросов в очереди до нашего запроса.

Второй ответ придет спустя некоторое время: \
```{'id': 'ID001', 'method': 'getEcho', 'error': 0, 'message': 'OK', 'expect_more_data': False, 'data': 'Hello!'}```
Здесь:
* **id** - ID запроса, был передан при вызове get_echo
* **method** - запрошеный метод API, во внутреннем, приближенном к MasstransitAPI формате (camelCase), getEcho в данном случае.
* **error** - код ошибки, 0 если все хорошо.
* **message** - сообщение об ошибке, 'OK' если все в порядке
* **expect_more_data** - если False, то это последнее сообщение от сервера по запросу с указанным ID (ID001),  больше данных не придет.
* **data** - словарь (dictionary), непосредственно данные, при выполнении сложных запросов masstransitAPI здесь будет находиться полученный от Яндекса JSON.

----

### get_stop_info (внутренняя команда - getStopInfo, функция Masstransit API - getStopInfo)
```get_stop_info(url, query_id=None, blocking=True, timeout=0, callback=None):```

Получение информации об остановке по URL.

Параметры:
* **url** - url остановки.
* **query_id** - см. общие параметры для всех функций.
* **blocking** - см. общие параметры для всех функций.
* **timeout** - см. общие параметры для всех функций.
* **callback** - см. общие параметры для всех функций.

Пример использования, синхронный режим :

```
import json
from yandex_transport_webdriver_api import YandexTransportProxy

# Прокси-сервер находится на 172.17.0.1:25555
proxy = YandexTransportProxy('172.17.0.1', 25555)
url = "https://yandex.ru/maps/213/moscow/?masstransit[stopId]=stop__9643291"
result = proxy.get_stop_info(url)
# Вытаскиваем координаты остановки
coords = result['data']['geometries'][0]['coordinates']
print("Stop coordinates: ", coords)
```

Результат:
```
Stop coordinates:  [37.678450655, 55.772332049]
```

Пример использования, асинхронный режим:

```
import time
import json
from yandex_transport_webdriver_api import YandexTransportProxy

def callback_fun(data):
    if 'data' in data:
        result = data['data']
        # Вытаскиваем координаты остановки
        coords = result['data']['geometries'][0]['coordinates']
        print("Stop coordinates: ", coords)

# Прокси-сервер находится на 172.17.0.1:25555
proxy = YandexTransportProxy('172.17.0.1', 25555)
url = "https://yandex.ru/maps/213/moscow/?masstransit[stopId]=stop__9643291"
result = proxy.get_stop_info(url, query_id='ID001', blocking=False, callback=ca$
print("Async function terminated!")
# Пусть основной поток немного подождет. 
time.sleep(20)
```

Результат:
```
Async function terminated!
Stop coordinates:  [37.678450655, 55.772332049]
```
----

### get_route_info (внутренняя команда - getRouteInfo, функция Masstransit API - getRouteInfo)
```get_route_info(url, query_id=None, blocking=True, timeout=0, callback=None):```

Получение информации омаршруте по URL.

Параметры:
* **url** - url остановки.
* **query_id** - см. общие параметры для всех функций.
* **blocking** - см. общие параметры для всех функций.
* **timeout** - см. общие параметры для всех функций.
* **callback** - см. общие параметры для всех функций.

Пример использования, синхронный режим :

```
import json
from yandex_transport_webdriver_api import YandexTransportProxy

# Прокси-сервер находится на 172.17.0.1:25555
proxy = YandexTransportProxy('172.17.0.1', 25555)
url = "https://yandex.ru/maps/213/moscow/?masstransit%5BrouteId%5D=B_tramway_de$
result = proxy.get_route_info(url)
# Вытаскиваем назвение первой остановки на маршруте
stop_name = result['data']['features'][0]['features'][0]['properties']['name']
print("1st stop: ", stop_name)
```

Результат:
```
1st stop:  Курский вокзал
```
----

### get_vehicles_info (внутренняя команда - getVehiclesInfo, функция Masstransit API - getVehiclesInfo)
```get_vehicles_info(url, query_id=None, blocking=True, timeout=0, callback=None):```

Получение информации о транспорте на маршруте по URL.

Параметры:
* **url** - url остановки.
* **query_id** - см. общие параметры для всех функций.
* **blocking** - см. общие параметры для всех функций.
* **timeout** - см. общие параметры для всех функций.
* **callback** - см. общие параметры для всех функций.

Пример использования, синхронный режим :

```
import json
from yandex_transport_webdriver_api import YandexTransportProxy

# Прокси-сервер находится на 172.17.0.1:25555
proxy = YandexTransportProxy('172.17.0.1', 25555)
url = "https://yandex.ru/maps/213/moscow/?masstransit%5BrouteId%5D=B_tramway_de$
result = proxy.get_vehicles_info(url)
```
----

### get_vehicles_info_with_region (внутренняя команда - getVehiclesInfoWithRegion, функция Masstransit API - getVehiclesInfoWithRegion)
```get_vehicles_info(url, query_id=None, blocking=True, timeout=0, callback=None):```

Получение информации о транспорте на маршруте по URL, с дополнительной информацией о регионе. Возможно скоро полностью сменит предыдущий метод.

Параметры:
* **url** - url остановки.
* **query_id** - см. общие параметры для всех функций.
* **blocking** - см. общие параметры для всех функций.
* **timeout** - см. общие параметры для всех функций.
* **callback** - см. общие параметры для всех функций.

Пример использования, синхронный режим :

```
import json
from yandex_transport_webdriver_api import YandexTransportProxy

# Прокси-сервер находится на 172.17.0.1:25555
proxy = YandexTransportProxy('172.17.0.1', 25555)
url = "https://yandex.ru/maps/213/moscow/?masstransit%5BrouteId%5D=B_tramway_de$
result = proxy.get_vehicles_info_with_region(url)
```
----



## Обратная связь

## Лицензия / License

## Титры / Credits
