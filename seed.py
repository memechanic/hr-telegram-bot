from db.setup_session import get_async_session
from db.models import User, StatusEnum


import asyncio
"""
    Файл для предварительной настройки - добавление админа в бд
    Измените данные для добавления админа и запустите данный скрипт
"""
async def main():
    async with get_async_session() as session:
        admin = User(
            tg_id = 123456789,              # Для получения айди напишите @check_my_tg_id_bot
            tg_username='username',         # Имя пользователя при @
            first_name='first_name',        # Имя
            last_name='last_name',          # Фамилия
            # patronym='patronym'           # Отчество
            phone_number='80001112233',     # Номер телефона обязательно, в формате +7 или 8 и 10 цифр
            email='email@email.ru',         # Почта обязательно
            status=StatusEnum.accept.value, # Не менять, показывает статус заявки пользователя
            is_admin=True                   # Поле для определения админа
        )
        try:
            session.add(admin)
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при запуске файла seed.py: {e}")
        else:
            print('Админ добавлен')

if __name__ == '__main__':
    asyncio.run(main())