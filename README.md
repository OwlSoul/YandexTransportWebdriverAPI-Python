# Yandex Transport Webdriver API

A "sort of API" to access Yandex Transport/Masstransit data, designed to work in conjunction with [YandexTransportProxy](https://github.com/OwlSoul/YandexTransportProxy).

Своеобразное "API" для доступа к данным Яндекс Транспорт (Masstransit API), предназначено для работы в паре с [YandexTransportProxy](https://github.com/OwlSoul/YandexTransportProxy).

*This project is for "Yandex.Maps" and "Yandex.Transport" services, so it's expected that majority of potential users are from Russian Federation, thus the README is written in russian language.*

![Yandex Transport Proxy Logo](https://raw.githubusercontent.com/OwlSoul/Images/master/YandexTransportProxy/yandex_transport_logo_python.jpg)

## Предназначение проекта

Данное "API" позволяет автоматизировать получение данных от Яндекс.Транспорт Masstransit API (закрытого на данный момент для сторонних пользователей). Получить данные вроде "покажи координаты всего общественного транспорта в таком-то районе" или "выдай мне данные о координатах транспорта по всему городу в данный момент" с помощью этой штуковины просто так нельзя. Зато с ее помощью можно автоматизировать получение данных  по конкретной остановке, или по конкретному маршруту, и получить их именно в том формате в котором Яндекс их пересылает - здоровенные такие JSON-структуры (до 150 килобайт и больше). 

Полученные данные можно использовать для сбора статистики по конкретному маршруту, создания своего собственного табло для конкретной остановки, и автоматизации каких-либо событий на основе данных о транспорте (редко ходящий, но жизненно важный автобус вышел на маршрут - включаем будильник).

## Принцип работы

У каждой остановки или маршрута в Яндекс.Картах есть свой URL, узнать его просто, достаточно просто нажать на интересующую остановку/маршрут и посмотреть что будет в адресной строке.

### Примеры URL:

----

**Остановка "Метро Бауманская", Москва**:

https://yandex.ru/maps/213/moscow/?ll=37.678708,55.772438&masstransit[stopId]=stop__9643291&mode=stop&z=19

Здесь самая важная часть - "*masstransit[stopId]=stop__9643291*". Это ID нашей остановки, в целом достаточно только его, ссылка https://yandex.ru/maps/213/moscow/?masstransit[stopId]=stop__9643291 точно также будет работать в браузере.

----

**Маршрут "Трамвай Б", Москва**:

https://yandex.ru/maps/213/moscow/?ll=37.679549,55.772203&masstransit[routeId]=B_tramway_default&masstransit[stopId]=stop__9643291&masstransit[threadId]=BA_tramway_default&mode=stop&z=18

Здесь важная часть - *"masstransit[routeId]=B_tramway_default"*, и ссылка https://yandex.ru/maps/213/moscow/?masstransit%5BrouteId%5D=B_tramway_default точно так же будет работать в браузере.

----

Подобные URL и используются в работе данного API. Хотя с "короткими" URL проблем пока не было, на всякий случай параноидально рекомендуется использовать "длинные".

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
route_url = https://yandex.ru/maps/213/moscow/?masstransit%5BrouteId%5D=B_tramway_default
result_json_route = proxy.getRouteInfo(route_url)
result_json_vehicles = proxy.getVehiclesInfo(route_url)
```

Результатом подобных запросов будут как раз те самые данные в формате JSON, приходящие от Yandex Transport/Masstransit API. Примеры таких ответов можно посмотреть в [YandexTransportProxy wiki](https://github.com/OwlSoul/YandexTransportProxy/wiki).

Прокси-сервер [YandexTransportProxy](https://github.com/OwlSoul/YandexTransportProxy) реализует из себя очередь, где полученные от данного API команды выполняются в один поток, с определенной задержкой между запросами. Такое поведение заложено по дизайну, для максимального имитирования работы обычного пользователя, и снижения потенциальной нагрузки на сервера Яндекс (в том числе с целью избежания временного бана за слишком частые запросы, и мы не хотим его злить).

JSON данные от Яндекса очень таких приличных размеров, и самый простой способ посмотреть что именно приходит по запросу - просто сохранить данные в какой-либо файл, и потом визуализировать, например [здесь](http://jsonviewer.stack.hu/): 

```
#!/usr/bin/env python3

# Basic example, get stop info and save it to a file

import json
from yandex_transport_webdriver_api import YandexTransportProxy

proxy = YandexTransportProxy('127.0.0.1', 25555)
url = "https://yandex.ru/maps/213/moscow/?ll=37.742975%2C55.651185&masstransit%5BstopId%5D=stop__9647487&mode=stop&z=18"
data = proxy.get_stop_info(url)
with open('data.json', 'w') as file:
    file.write(json.dumps(data,indent=4, separators=(',', ': ')))
```

Данных приходит очень много, и лучше просто один раз взглянуть на них, чем пытаться здесь все задокументировать.
Примеры приходящих данных можно посмотреть в [wiki к YandexProxyServer](https://github.com/OwlSoul/YandexTransportProxy/wiki):

## Установка

Проект можно поставить через pip3:

```
pip3 install yandex-transport-webdriver-api
```

Либо просто скачав данную библиотеку из [релизов](https://github.com/OwlSoul/YandexTransportWebdriverAPI-Python/releases) или через "git clone".

Каких-то важных зависимостей у библиотеки нет, только стандартные библиотеки Python3.

Не забывайте, что для работы нужен запущенный и доступный по сети сервер [YandexTransportProxy](https://github.com/OwlSoul/YandexTransportProxy), хотя бы один (а можно и Kubernetes кластер из них создать).

## Реализованные функции
Функции для получения информации от Яндекс.Транспорта могут работать как в блокирующем (синхронном), так и в неблокирующем (асинхронном) режимах.

Функции данного API имеют общую структуру,обычно в виде get_something(params, query_id=None, blocking=True, timeout=0, callback=None)

Параметры, общие для всех функций:

* _query_id_ - строка (string),ID данного запроса, все ответы на него будут содержать данный ID. Важно для асинхронного режима, для синхронного можно опустить (сгенерируется автоматически случайным образом).
* _blocking_ - если **True**, функция блокирует до окончания выполнения, или до истечения таймаута (следующий параметр). Если **False** - функция завершается немедленно, и при каждом полученном ответе будет вызываться функция callback.
* _timeout_ - целое число (int), таймаут в секундах. Если в течении данного промежутка времени никакого ответа от сервера не будет получено, будет брошено исключение. Важно помнить что у прокси-сервера может быть приличный промежуток между выполнениями запросов, если указывается данный параметр. При значении = 0 таймаут не учитывается, и функция будет ждать бесконечно, или пока не придут данные сигнализирующие что "обработка запроса окончена, новых данных можн оне ждать".
* _callback_ - callback функция, будет вызываться каждый раз при получении данных в асинхронном режиме.

| Метод | Соответствующий метод Yandex Masstransit API | Назначение |
|-----|-----|-----|
| [get_echo](https://github.com/OwlSoul/YandexTransportWebdriverAPI-Python/wiki/%D0%9C%D0%B5%D1%82%D0%BE%D0%B4:-get_echo) | - | Тестовая функция, помещает команду getEcho в очередь YandexTransportProxy, и возвращает переданную строку (text) при выполнении |
| [get_stop_info](https://github.com/OwlSoul/YandexTransportWebdriverAPI-Python/wiki/%D0%9C%D0%B5%D1%82%D0%BE%D0%B4:-get_stop_info) | getStopInfo | Получить данные об остановки (проходящие маршруты, время прибытия и т.д.) |
| [get_route_info](https://github.com/OwlSoul/YandexTransportWebdriverAPI-Python/wiki/%D0%9C%D0%B5%D1%82%D0%BE%D0%B4:-get_route_info) | getRouteInfo | Получение информации о маршруте |
|[get_vehicles_info](https://github.com/OwlSoul/YandexTransportWebdriverAPI-Python/wiki/%D0%9C%D0%B5%D1%82%D0%BE%D0%B4:-get_vehicles_info)|getVehiclesInfo| Получить информацию о транспорте на маршруте|
|[get_vehicles_info_with_region](https://github.com/OwlSoul/YandexTransportWebdriverAPI-Python/wiki/%D0%9C%D0%B5%D1%82%D0%BE%D0%B4:-get_vehicles_info_with_region) | getVehiclesInfoWithRegion | Получение информации о транспорте на маршруте, с дополнительной информацией о регионе. Возможно скоро полностью сменит предыдущий метод. |
|[get_layer_regions](https://github.com/OwlSoul/YandexTransportWebdriverAPI-Python/wiki/%D0%9C%D0%B5%D1%82%D0%BE%D0%B4:-get_layer_regions)| getLayerRegions | "Running Gag" этого проекта, не ясно за что оно отвечает. |
|[get_all_info](https://github.com/OwlSoul/YandexTransportWebdriverAPI-Python/wiki/%D0%9C%D0%B5%D1%82%D0%BE%D0%B4:-get_all_info)| - |Универсальный метод, просто выдает все возможные методы по скормленому ему URL|

## F.A.Q.
**Q:** get_vehicles_info (getVehiclesInfo) не работает, хотя в браузере трнспорт на аршруте отображается. \
**A:** Возможно на данном маршруте getVehiclesInfo уже не применятся, стоит попробовать get_vehicles_info_with_region (getVehiclesInfoWithRegion), или get_all_info и просто посмотреть какие именно запросы Yandex Masstransit API выполняются по переданному 

## Обратная связь
Гарантий что эта штука будет работать долго и счастливо - никаких. Яндекс может в любой момент устроить что-нибудь что сделает работу этого проекта невозможным. Проект находится на постоянной системе мониторинга, и если что-то отваливается или перестает работать - автор об этом оперативно узнает, и поправит, если это возможно.

В любом случае, сообщить о возникшей проблеме всегда можно здесь: \
https://github.com/OwlSoul/YandexTransportWebdriverAPI-Python/issues/new

## Лицензия / License
Исходный код распространяется под лицензией MIT, "как есть (as is)", автор ответственности за возможные проблемы при его использовании не несет (но будет глубоко расстроен).

The code is distributed under MIT licence, AS IS, author do not bear any responsibility for possible problems with usage of this project (but he will be very sad).

## Зал славы / Credits
__Project author:__ [Yury D.](https://github.com/OwlSoul) (TheOwlSoul@gmail.com) \
__PEP-8 Evangelist, Good Cop:__ [Pavel Lutskov](https://github.com/ltskv) \
__PEP-8 Evangelist, Bad Cop:__ [Yury Alexeev](https://github.com/Kuma-San0217)

----
