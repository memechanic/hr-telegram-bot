import asyncio
from pathlib import Path

from db.models import User, StatusEnum
from db.setup_session import get_async_session

"""
    Файл для предварительной настройки - добавление админа в бд, а также создание папок для модулей
    Измените данные для добавления админа и запустите данный скрипт
"""
async def main():
    media_path = Path(__file__).resolve().parent / 'media'
    folders = {
        'cafeteria': media_path / 'cafeteria',
        'company': media_path / 'company',
        'docs': media_path / 'docs',
        'docs_test': media_path / 'docs' / 'docs_test',
        'structure': media_path / 'structure',
        'vtours': media_path / 'vtours',
        'vtours_test': media_path / 'vtours' / 'vtours_test',
    }
    try:
        media_path.mkdir()
    except Exception as e:
        print(f"Ошибка создания папки: {e}")
    else:
        print("Папка media успешно создана")

    for p in folders.values():
        try:
            p.mkdir()
        except Exception as e:
            print(f"Ошибка создания папок: {e}")
    
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