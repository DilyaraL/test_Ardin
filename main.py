from FDataBase import *

app = Flask(__name__)
db_uri = 'postgresql+psycopg2://postgres:123456@localhost:5432/postgres'
engine = create_engine(db_uri)
app.engine = engine

Session = scoped_session(sessionmaker(bind=engine))
app.session = Session

metadata.create_all(engine)


@app.teardown_appcontext
def shutdown_session(exception=None):
    Session.remove()

def check_user_exists(email, user_id=None):
    """Проверка наличия пользователя с указанным email"""
    if id:
        select_query = select(user).where(user.c.email == email and user.c.id != user_id)
        result = app.session.execute(select_query).fetchone()
        if result:
            return True
        else:
            return False
    else:
        select_query = select(user).where(user.c.email == email)
        result = app.session.execute(select_query).fetchone()
        if result:
            return True
        else:
            return False


def validate_permissions(permissions):
    """Проверка валидности permissions"""
    invalid_permissions = [p for p in permissions if p not in ('USER_CREATE', 'USER_READ', 'USER_UPDATE', 'USER_DELETE')]
    if invalid_permissions:
        return False
    return True


def get_position_id_by_title(title):
    """Поиск идентификатора должности на основе должности"""
    select_id = select(position.c.id).where(position.c.title == title)
    position_id = app.session.execute(select_id).scalar()
    return position_id


@app.route('/api/users', methods=['GET'])
def get_users():
    """Получение списка пользователей"""
    # Извлечение параметров запроса
    email = request.args.get('email')
    position_name = request.args.get('position')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Формирование запроса SELECT с учетом параметров
    query = select(user.c.id, user.c.email, position.c.title).select_from(user.join(position, user.c.position_id==position.c.id))

    # Добавление условий WHERE в запрос, если указаны параметры поиска
    if email:
        query = query.where(user.c.email == email)
    if position_name:
        query = query.where(position.c.title == position_name)

    # Выполнение запроса с пагинацией
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    results = app.session.execute(query).fetchall()

    # Формирование и возврат JSON-ответа
    users = [{'id': str(row[0]), 'email': row[1], 'position': row[2]} for row in results]
    json_data = json.dumps(users)
    response = Response(json_data, content_type='application/json')

    return response


@app.route('/api/users/<uuid:user_id>', methods=['GET'])
def get_user(user_id):
    """Получение пользователя по id"""

    user_position = user.join(position, user.c.position_id == position.c.id)
    query = select(user.c.id, user.c.email, position.c.title).where(user.c.id == user_id).select_from(user_position)
    result = app.session.execute(query).fetchone()

    if result is None:
        return jsonify({'error': 'User not found'}), 404

    user_data = {
        'id': str(result.id),
        'email': result.email,
        'position': result.title,
        'permissions': []
    }

    permissions_query = select(role_permission.c.permission).where(role_permission.c.user_id == user_id)
    permissions_result = app.session.execute(permissions_query).fetchall()

    if permissions_result:
        user_data['permissions'] = [str(row.permission) for row in permissions_result]

    return jsonify(user_data)


@app.route('/api/users', methods=['POST'])
def create_user():
    """Создание нового пользователя"""
    data = request.json

    if not data or 'email' not in data:
        return jsonify({'error': 'Invalid request data'}), 404

    email = data.get('email')
    position_title = data.get('position')
    permissions = data.get('permissions')

    if check_user_exists(email):
        return jsonify({'error': 'User with this email already exists or email is empty'}), 404

    # Поиск идентификатора должности на основе строки должности
    position_id = get_position_id_by_title(position_title)

    if position_id is None:
        return jsonify({'error': 'Position not found'}), 404

    # Вставка пользователя в таблицу user
    insert_user = user.insert().values(email=email, position_id=position_id)
    result = app.session.execute(insert_user)
    user_id = result.inserted_primary_key[0]

    # Вставка разрешений пользователя в таблицу role_permission
    # фильтруем разрешения, оставляя только те, которые соответствуют значением в PERMISSION_ENUM
    if permissions:
        if not validate_permissions(permissions):
            return jsonify({'error': 'Invalid permissions'})

        role_permission_values = [{'user_id': user_id, 'permission': permission} for permission in permissions]
        insert_role_permission = role_permission.insert().values(role_permission_values)
        app.session.execute(insert_role_permission)

    app.session.commit()

    # Получение созданного пользователя из базы данных
    user_position = user.join(position, user.c.position_id == position.c.id)
    query = select(user.c.id, user.c.email, position.c.title).where(user.c.id == user_id).select_from(user_position)
    result = app.session.execute(query).fetchone()

    user_data = {
        'id': str(result.id),
        'email': result.email,
        'position': result.title,
        'permissions': []
    }

    permissions_query = select(role_permission.c.permission).where(role_permission.c.user_id == user_id)
    permissions_result = app.session.execute(permissions_query).fetchall()

    if permissions_result:
        user_data['permissions'] = [str(row.permission) for row in permissions_result]

    return jsonify(user_data)


@app.route('/api/users/<uuid:user_id>', methods=['POST'])
def change_user(user_id):
    """Изменение пользователя"""
    select_user = select(user).where(user.c.id == user_id)
    result = app.session.execute(select_user).fetchone()
    if result is None:
        return jsonify({'error': 'User not found'}), 404

    data = request.json

    if not data:
        return jsonify({'error': 'Invalid request data'}), 404

    email = data.get('email')
    position_title = data.get('position')
    permissions = data.get('permissions')

    update_values = dict()

    if email:
        if check_user_exists(email):
            return jsonify({'error': 'User with this email already exists'}), 404
        update_values['email'] = email

    if position_title:
        position_id = get_position_id_by_title(position_title)
        if position_id is None:
            return jsonify({'error': 'Position not found'}), 404

        update_values['position_id'] = position_id

    update_user = user.update().where(user.c.id == user_id).values(**update_values)
    app.session.execute(update_user)
    app.session.commit()

    if permissions:
        if not validate_permissions(permissions):
            return jsonify({'error': 'Invalid permissions'})

        # Удаление всех старых permissions пользователя
        delete_old_permissions = role_permission.delete().where(role_permission.c.user_id == user_id)
        app.session.execute(delete_old_permissions)
        # Вставка новых permissions пользователя
        role_permission_values = [{'user_id': user_id, 'permission': permission} for permission in permissions]
        insert_role_permission = role_permission.insert().values(role_permission_values)
        app.session.execute(insert_role_permission)
        app.session.commit()

    # Получение обновленного пользователя из базы данных
    user_position = user.join(position, user.c.position_id == position.c.id)
    query = select(user.c.id, user.c.email, position.c.title).where(user.c.id == user_id).select_from(user_position)
    result = app.session.execute(query).fetchone()

    if result is None:
        return jsonify({'error': 'User not found'})

    user_data = {
            'id': str(result.id),
            'email': result.email,
            'position': result.title,
            'permissions': []
        }

    permissions_query = select(role_permission.c.permission).where(role_permission.c.user_id == user_id)
    permissions_result = app.session.execute(permissions_query).fetchall()

    if permissions_result:
            user_data['permissions'] = [str(row.permission) for row in permissions_result]

    return jsonify(user_data)



@app.route('/api/users/<uuid:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Удаление пользователя"""
    # Проверка наличия пользователя в базе данных
    select_query = select(user.c.id).where(user.c.id == user_id)
    result = app.session.execute(select_query).fetchone()
    if result is None:
        return jsonify({'error': 'User not found'}), 404  # Возвращаем ошибку 404, если пользователь не найден

    delete_query = user.delete().where(user.c.id == user_id)
    app.session.execute(delete_query)
    app.session.commit()

    return '', 204


@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Список должностей"""
    # Получение параметров запроса
    title = request.args.get('title')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Построение базового запроса
    select_query = select(position.c.id, position.c.title)

    # Добавление фильтра по названию, если указано
    if title:
        select_query = select_query.where(position.c.title.ilike(f'%{title}%'))
        # метод ilike для регистронезависимого поиска

    # Ограничение количества результатов на страницу
    select_query = select_query.limit(per_page)

    # Вычисление смещения (offset) на основе номера страницы
    offset = (page - 1) * per_page
    select_query = select_query.offset(offset)

    # Выполнение запроса и получение результатов
    result = app.session.execute(select_query).fetchall()

    # Создание списка объектов должностей
    positions = [{'id': str(row.id), 'title': row.title} for row in result]

    return jsonify(positions)


@app.route('/api/positions/<uuid:position_id>', methods=['DELETE'])
def delete_position(position_id):
    """Удаление должности"""
    # Проверка наличия должности в базе данных
    select_query = select(position).where(position.c.id == position_id)
    result = app.session.execute(select_query).fetchone()
    if not result:
        return jsonify({'error': 'Position not found'}), 404

    # Удаление должности
    delete_query = position.delete().where(position.c.id == position_id)
    app.session.execute(delete_query)

    # Подтверждение изменений в базе данных
    app.session.commit()

    return '', 204


if __name__ == "__main__":
    app.run(debug=True)
