# Демо проект к курсу "Domain Driven Design и Clean Architecture на языке C#"

📚 Подробнее о курсе: [microarch.ru/courses/ddd/languages/csharp](http://microarch.ru/courses/ddd/languages/csharp)

---

## Условия использования

Вы можете использовать и модифицировать данный код **в образовательных целях**, при условии сохранения ссылки на курс и оригинального источника.

---

# OpenApi
Вызывать из папки DeliveryApp.Api/Adapters/Http/Contract
```
cd DeliveryApp.Api/Adapters/Http/Contract/
openapi-generator generate -i https://gitlab.com/microarch-ru/microservices/dotnet/system-design/-/raw/main/services/delivery/contracts/openapi.yml -g aspnetcore -o . --package-name OpenApi --additional-properties classModifier=abstract --additional-properties operationResultTask=true
```
# БД
```
dotnet tool install --global dotnet-ef
dotnet tool update --global dotnet-ef
dotnet add package Microsoft.EntityFrameworkCore.Design
```
[Подробнее про dotnet cli](https://learn.microsoft.com/ru-ru/ef/core/cli/dotnet)

# Миграции
```
dotnet ef migrations add Init --startup-project ./DeliveryApp.Api --project ./DeliveryApp.Infrastructure --output-dir ./Adapters/Postgres/Migrations
dotnet ef database update --startup-project ./DeliveryApp.Api --connection "Server=localhost;Port=5432;User Id=username;Password=secret;Database=delivery;"
```

# Запросы к БД
```
-- Выборки
SELECT * FROM public.couriers;
SELECT * FROM public.transports;
SELECT * FROM public.orders;

SELECT * FROM public.outbox;

-- Очистка БД (все кроме справочников)
DELETE FROM public.couriers;
DELETE FROM public.transports;
DELETE FROM public.orders;
DELETE FROM public.outbox;

-- Добавить курьеров

-- Пеший
INSERT INTO public.transports(
    id, name, speed)
VALUES ('921e3d64-7c68-45ed-88fb-97ceb8148a7e', 'Пешком', 1);
INSERT INTO public.couriers(
    id, name, transport_id, location_x, location_y, status)
VALUES ('bf79a004-56d7-4e5f-a21c-0a9e5e08d10d', 'Пеший', '921e3d64-7c68-45ed-88fb-97ceb8148a7e', 1, 3, 'free');

-- Вело
INSERT INTO public.transports(
    id, name, speed)
VALUES ('b96a9d83-aefa-4d06-99fb-e630d17c3868', 'Велосипед', 2);
INSERT INTO public.couriers(
    id, name, transport_id, location_x, location_y, status)
VALUES ('db18375d-59a7-49d1-bd96-a1738adcee93', 'Вело', 'b96a9d83-aefa-4d06-99fb-e630d17c3868', 4,5, 'free');

-- Авто
INSERT INTO public.transports(
    id, name, speed)
VALUES ('c24d3116-a75c-4a4b-9b22-1a7dc95a8c79', 'Машина', 3);
INSERT INTO public.couriers(
    id, name, transport_id, location_x, location_y, status)
VALUES ('407f68be-5adf-4e72-81bc-b1d8e9574cf8', 'Авто', 'c24d3116-a75c-4a4b-9b22-1a7dc95a8c79', 7,9, 'free');
```

## Лицензия

Код распространяется под лицензией [MIT](./LICENSE).
© 2025 microarch.ru
