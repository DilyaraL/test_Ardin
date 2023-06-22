# test_Ardin

## Технологии
  - PostgreSQL
  - Flask
  - SQLAlchemy Core
  - github

## API

### Список пользователей
`GET api/users`
#### Параметры запроса
<sub>В скобках указаны значения по-умолчанию</sub>
```
email    STRING       - поиск по почте
position STRING       - поиск по должности
page     INTEGER (1)  - номер страницы
per_page INTEGER (10) - кол-во объектов на страницу
```

#### Тело ответа
`Content-Type: application/json`
```
[
  {
    id: UUID,
    email: STRING,
    position: STRING | null
  }
  ...
]
```

---

### Пользователь под идентификатору
`GET api/users/{user_id}`

#### Тело ответа
`Content-Type: application/json`
```
{
  id: UUID,
  email: STRING,
  position: STRING | null,
  permissions: [
    PERMISSION_ENUM
    ...
  ]
}
```

---

### Создание пользователя
`POST api/users`

#### Тело запроса
`Content-Type: application/json`
```
{
  email: STRING,
  position: STRING | null,
  permissions: [
    PERMISSION_ENUM
    ...
  ]
}
```

#### Тело ответа
`Content-Type: application/json`
```
{
  id: UUID,
  email: STRING,
  position: STRING | null,
  permissions: [
    PERMISSION_ENUM
    ...
  ]
}
```

---

### Изменение пользователя
`POST api/users/{user_id}`

#### Тело запроса
`Content-Type: application/json`
```
{
  email: STRING,
  position: STRING | null,
  permissions: [
    PERMISSION_ENUM
    ...
  ]
}
```

#### Тело ответа
`Content-Type: application/json`
```
{
  id: UUID,
  email: STRING,
  position: STRING | null,
  permissions: [
    PERMISSION_ENUM
    ...
  ]
}
```

### Удаление пользователя
`DELETE api/users/{user_id}`

#### Тело ответа
`204 No Content` <sup>Без тела ответа</sup>

---

### Список должностей
`GET api/positions`
#### Параметры запроса
<sub>В скобках указаны значения по-умолчанию</sub>
```
title    STRING       - поиск по названию
page     INTEGER (1)  - номер страницы
per_page INTEGER (10) - кол-во объектов на страницу
```

#### Тело ответа
`Content-Type: application/json`
```
[
  {
    id: UUID,
    title: STRING
  }
  ...
]
```

---

### Удаление должности
`DELETE api/positions/{position_id}`

#### Тело ответа
`204 No Content` <sup>Без тела ответа</sup>
