from datetime import datetime

from flask import Flask, request, jsonify
from flasgger import Swagger
from Обучение.Rest_API.DatabaseHandler import DatabaseHandler

# Создание приложения Flask
app = Flask(__name__)

# Инициализация Swagger
swagger = Swagger(app)

# Создание экземпляра DatabaseHandler
db_handler = DatabaseHandler()



@app.route('/submitData', methods=['POST'])
def submit_data():
    """
    Обработка данных перевала
    ----
       tags:
         - Pereval
       parameters:
         - in: body
           name: body
           schema:
             type: object
             properties:
               beauty_title:
                 type: string
               title:
                 type: string
               add_time:
                 type: string
                 format: date-time
               user:
                 type: object
                 properties:
                   email:
                     type: string
                   fam:
                     type: string
                   name:
                     type: string
                   otc:
                     type: string
                   phone:
                     type: string
               coords:
                 type: object
                 properties:
                   latitude:
                     type: number
                   longitude:
                     type: number
                   height:
                     type: number
               level:
                 type: object
                 properties:
                   winter:
                     type: string
                   summer:
                     type: string
                   autumn:
                     type: string
                   spring:
                     type: string
               images:
                 type: array
                 items:
                   type: object
                   properties:
                     data:
                       type: string
                     title:
                       type: string
       responses:
         200:
           description: Данные успешно отправлены
         400:
           description: Неверный формат данных
         500:
           description: Внутренняя ошибка сервера
    """
    try:
        # Получение данных из запроса
        data = request.json

        # Проверка типа данных
        if not isinstance(data, dict):
            # Возвращение ошибки, если данные не являются словарем
            return jsonify(status=400, message="Неверный формат данных"), 400

        # Определение обязательных полей
        required_fields = ['beauty_title', 'title', 'add_time', 'user', 'coords', 'level', 'images']

        # Проверка обязательных полей
        for field in required_fields:
            if field not in data:
                # Возвращение ошибки, если обязательное поле отсутствует
                return jsonify(status=400, message=f"Отсутствует обязательное поле {field}"), 400

        # Получение информации о пользователе
        user_info = data.get('user', {})

        # Проверка типа данных
        if not isinstance(user_info, dict):
            # Возвращение ошибки, если данные не являются словарем
            return jsonify(status=400, message="Неверный формат информации о пользователе"), 400

        # Определение обязательных полей для пользователя
        required_user_fields = ['email', 'fam', 'name', 'otc', 'phone']

        # Проверка обязательных полей для пользователя
        for field in required_user_fields:
            if field not in user_info:
                # Возвращение ошибки, если обязательное поле отсутствует
                return jsonify(status=400,
                               message=f"Отсутствует обязательное поле {field} в информации о пользователе"), 400

        # Получение координат
        coords = data.get('coords', {})

        # Проверка типа данных
        if not isinstance(coords, dict):
            # Возвращение ошибки, если данные не являются словарем
            return jsonify(status=400, message="Неверный формат координат"), 400

        # Определение обязательных полей для координат
        required_coords_fields = ['latitude', 'longitude', 'height']

        # Проверка обязательных полей для координат
        for field in required_coords_fields:
            if field not in coords:
                # Возвращение ошибки, если обязательное поле отсутствует
                return jsonify(status=400, message=f"Отсутствует обязательное поле {field} в координатах"), 400

        # Получение уровня
        level = data.get('level', {})

        # Проверка типа данных
        if not isinstance(level, dict):
            # Возвращение ошибки, если данные не являются словарем
            return jsonify(status=400, message="Неверный формат уровня"), 400

        # Определение обязательных полей для уровня
        required_level_fields = ['winter', 'summer', 'autumn', 'spring']

        # Проверка обязательных полей для уровня
        for field in required_level_fields:
            if field not in level:
                # Возвращение ошибки, если обязательное поле отсутствует
                return jsonify(status=400, message=f"Отсутствует обязательное поле {field} в уровне"), 400

        # Получение изображений
        images = data.get('images', [])

        # Проверка типа данных
        if not isinstance(images, list) or not all(isinstance(image, dict) for image in images):
            # Возвращение ошибки, если данные не являются списком словарей
            return jsonify(status=400, message="Изображения должны быть списком словарей"), 400

        try:
            # Проверка существования пользователя
            if db_handler.check_user_exists(user_info.get('email')):
                # Возвращение ошибки, если пользователь уже существует
                return jsonify(status=400, message="Пользователь уже существует"), 400

            # Добавление пользователя
            user_id = db_handler.add_user(
                user_info.get('email'),
                user_info.get('fam'),
                user_info.get('name'),
                user_info.get('otc'),
                user_info.get('phone')
            )

            # Добавление координат
            coord_id = db_handler.add_coord(
                coords.get('latitude'),
                coords.get('longitude'),
                coords.get('height')
            )

            # Добавление перевала
            pereval_id = db_handler.add_pereval(
                beauty_title=data.get('beauty_title'),
                title=data.get('title'),
                other_titles=data.get('other_titles', ""),
                connect=data.get('connect', ""),
                add_time=data.get('add_time'),
                user_id=user_id,
                coord_id=coord_id,
                level_winter=level.get('winter'),
                level_summer=level.get('summer'),
                level_autumn=level.get('autumn'),
                level_spring=level.get('spring'),
                status='new'
            )

            # Добавление изображений
            for image in images:
                image_id = db_handler.add_image(
                    image.get('data'),
                    image.get('title'),
                    pereval_id
                )
                # Если не удалось добавить изображение, то возвращаем ошибку
                if image_id is None:
                    return jsonify(status=500, message="Ошибка при добавлении изображения"), 500

            if pereval_id is not None:
                return jsonify(status=200, id=pereval_id, message="Отправлено успешно"), 200
            else:
                return jsonify(status=500, message="Ошибка при добавлении перевала"), 500
        except Exception as e:
            return jsonify(status=500, message=f"Внутренняя ошибка {e}"), 500
    except Exception as e:
        return jsonify(status=500, message=f"Внутренняя ошибка {e}"), 500



@app.route('/submitData/<int:id>', methods=['GET'])
def get_submit_data(id):
    """
    Получение данных перевала по ID
    ---
    tags:
      - Pereval
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID перевала для получения данных
    responses:
      200:
        description: Данные перевала успешно получены
        schema:
          type: object
          properties:
            status:
              type: integer
            data:
              type: object
              properties:
                id:
                  type: integer
                beauty_title:
                  type: string
                title:
                  type: string
                other_titles:
                  type: string
                connect:
                  type: string
                add_time:
                  type: string
                  format: date-time
                user_id:
                  type: integer
                coord_id:
                  type: integer
                level:
                  type: object
                  properties:
                    winter:
                      type: string
                    summer:
                      type: string
                    autumn:
                      type: string
                    spring:
                      type: string
                status:
                  type: string
      404:
        description: Запись не найдена
      500:
        description: Внутренняя ошибка сервера
    """
    try:
        record = db_handler.get_pereval_by_id(id)
        if record:
            # Формирование ответа с правильным форматированием даты
            response_data = {
                "id": record[0],  # ID перевала
                "beauty_title": record[1],  # Красивое название
                "title": record[2],  # Заголовок
                "other_titles": record[3],  # Другие названия
                "connect": record[4],  # Связь
                "add_time": record[5].strftime("%a, %d %b %Y %H:%M:%S GMT") if isinstance(record[5], datetime) else
                record[5],  # Форматирование времени
                "user_id": record[6],  # ID пользователя
                "coord_id": record[7],  # ID координат
                "level": {
                    "winter": record[8],  # Уровень зимы
                    "summer": record[9],  # Уровень лета
                    "autumn": record[10],  # Уровень осени
                    "spring": record[11]  # Уровень весны
                },
                "status": record[12]  # Статус
            }
            return jsonify(status=200, data=response_data), 200
        else:
            return jsonify(status=404, message="Запись не найдена"), 404
    except Exception as e:
        return jsonify(status=500, message=f"Внутренняя ошибка {e}"), 500



@app.route('/submitData/<int:id>', methods=['PATCH'])
def patch_submit_data(id):
    """
    Обновление данных перевала по ID
    ---
    tags:
      - Pereval
    parameters:
      - in: path
        name: id
        type: integer
        required: true
        description: ID перевала для обновления данных
      - in: body
        name: body
        schema:
          type: object
          properties:
            beauty_title:
              type: string
            title:
              type: string
            other_titles:
              type: string
            connect:
              type: string
            add_time:
              type: string
              format: date-time
            level:
              type: object
              properties:
                winter:
                  type: string
                summer:
                  type: string
                autumn:
                  type: string
                spring:
                  type: string
    responses:
      200:
        description: Запись успешно обновлена
      400:
        description: Ошибка в данных запроса
      500:
        description: Внутренняя ошибка сервера
    """
    try:
        data = request.json
        result = db_handler.update_pereval(id, data)
        if result['state'] == 1:
            return jsonify(status=200, message="Запись успешно обновлена"), 200
        else:
            return jsonify(status=400, message=result['message']), 400
    except Exception as e:
        return jsonify(status=500, message=f"Внутренняя ошибка {e}"), 500


if __name__ == '__main__':
    app.run(debug=True)
