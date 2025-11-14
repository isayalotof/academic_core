import os
from pathlib import Path
import aiomax
from aiomax import buttons
import logging

# Настройка базового логирования (до загрузки .env)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Загрузка переменных окружения из корневого .env файла
# Сначала пробуем корневой .env (на уровень выше), затем локальный
root_env_path = Path(__file__).parent.parent / '.env'
local_env_path = Path(__file__).parent / '.env'
env_loaded = False
try:
    from dotenv import load_dotenv
    # Пробуем загрузить корневой .env
    if root_env_path.exists():
        env_path = root_env_path
    elif local_env_path.exists():
        env_path = local_env_path
    else:
        env_path = None
    
    if env_path and env_path.exists():
        # Пробуем разные кодировки
        for encoding in ['utf-8', 'utf-8-sig', 'cp1251', 'latin-1']:
            try:
                load_dotenv(env_path, encoding=encoding)
                test_token = os.getenv('BOT_TOKEN')
                if test_token:
                    env_loaded = True
                    logging.info(f"✓ Загружен .env файл: {env_path} (кодировка: {encoding})")
                    logging.info(f"✓ BOT_TOKEN найден в .env (длина: {len(test_token)})")
                    break
            except Exception as enc_error:
                logging.debug(f"Не удалось загрузить с кодировкой {encoding}: {enc_error}")
                continue
        
        if not env_loaded:
            # Последняя попытка без указания кодировки
            load_dotenv(env_path)
            test_token = os.getenv('BOT_TOKEN')
            if test_token:
                env_loaded = True
                logging.info(f"✓ Загружен .env файл: {env_path} (автоопределение кодировки)")
            else:
                # Альтернативный способ: читаем файл напрямую
                logging.warning(f"⚠ .env файл загружен через dotenv, но BOT_TOKEN не найден. Пробуем прямой парсинг...")
                try:
                    for encoding in ['utf-8', 'utf-8-sig', 'cp1251', 'latin-1']:
                        try:
                            with open(env_path, 'r', encoding=encoding) as f:
                                for line in f:
                                    line = line.strip()
                                    if line and not line.startswith('#') and '=' in line:
                                        key, value = line.split('=', 1)
                                        key = key.strip()
                                        value = value.strip().strip('"').strip("'")
                                        if key == 'BOT_TOKEN' and value:
                                            os.environ['BOT_TOKEN'] = value
                                            env_loaded = True
                                            logging.info(f"✓ BOT_TOKEN загружен напрямую из файла (кодировка: {encoding})")
                                            break
                            if env_loaded:
                                break
                        except Exception:
                            continue
                except Exception as e:
                    logging.error(f"✗ Ошибка при прямом чтении .env файла: {e}")
    else:
        logging.warning(f"⚠ .env файл не найден. Искали в: {root_env_path} и {local_env_path}")
except ImportError:
    # python-dotenv не установлен, используем только переменные окружения системы
    logging.warning("⚠ python-dotenv не установлен, используем только системные переменные окружения")
except Exception as e:
    logging.error(f"✗ Ошибка при загрузке .env файла: {e}")
    import traceback
    logging.error(traceback.format_exc())

# Обновление уровня логирования после загрузки .env
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.getLogger().setLevel(getattr(logging, log_level.upper(), logging.INFO))

# Токен бота из переменной окружения
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    error_msg = f"BOT_TOKEN не установлен. "
    if env_loaded:
        error_msg += f".env файл был загружен из {env_path}, но BOT_TOKEN не найден в файле."
    else:
        error_msg += f"Установите переменную окружения BOT_TOKEN или создайте .env файл в {env_path}."
    logging.error(error_msg)
    raise ValueError(error_msg)

logging.info(f"✓ BOT_TOKEN загружен (длина: {len(TOKEN)} символов)")

# Имя бота (username) для открытия миниприложения
# Оставьте пустым, чтобы использовать автоматическое определение
# Или укажите username бота (без @), например: "mybot"
BOT_USERNAME = os.getenv('BOT_USERNAME', None)  # Если None, будет использован WebAppButton без указания бота

# Инициализация бота
bot = aiomax.Bot(TOKEN, default_format="markdown")


@bot.on_bot_start()
async def info(pd: aiomax.BotStartPayload):
    """
    Обработчик запуска бота.
    """
    await pd.send("Привет! Отправь команду /start для начала работы.")


@bot.on_message()
async def handle_start(message: aiomax.Message):
    """
    Обработчик команды /start - отправляет приветственное сообщение с кнопкой миниприложения.
    """
    text = message.content
    
    # Проверяем, является ли сообщение командой /start
    if text and text.strip() == '/start':
        print("Получена команда /start")
        welcome_text = (
            "👋 Привет! Я бот Академическое Ядро.\n\n"
            "📚 Мы создали приложение для решения ваших повседневных задач в университете:\n\n"
            "📅 • Просмотр расписания занятий\n"
            "📅 • автоматическое составление расписания по предпочтениям преподавателя \n"
            "🎓 • Управление учебными процессами\n"
            "📝 • Подача заявлений и обращений\n"
            "🏫 • Информация об аудиториях и событиях\n"
            "🚀 Нажми на кнопку ниже, чтобы открыть миниприложение и начать пользоваться всеми возможностями!"
        )
        
        # Создаем кнопку для открытия миниприложения, прикрепленного к боту
        bot_username = None
        bot_id = None
        deeplink = None
        
        try:
            # Получаем информацию о боте для создания кнопки
            try:
                bot_info = await bot.get_me()
                bot_id = bot_info.id if hasattr(bot_info, 'id') else None
                bot_username = bot_info.username if hasattr(bot_info, 'username') else None
                print(f"Информация о боте: ID={bot_id}, username={bot_username}")
            except Exception as e:
                print(f"Не удалось получить информацию о боте: {e}")
                bot_username = BOT_USERNAME
            
            # Используем WebAppButton для открытия миниприложения, прикрепленного к боту
            # WebAppButton открывает миниприложение, связанное с указанным ботом
            if bot_username:
                # Если есть username, используем его (предпочтительный способ)
                miniapp_button = buttons.WebAppButton(
                    text='🚀 Открыть миниприложение',
                    bot=bot_username
                )
                print(f"Используется WebAppButton с username: {bot_username}")
            elif bot_id:
                # Если есть только ID, используем его
                miniapp_button = buttons.WebAppButton(
                    text='🚀 Открыть миниприложение',
                    bot=bot_id
                )
                print(f"Используется WebAppButton с ID: {bot_id}")
            elif BOT_USERNAME:
                # Если указан BOT_USERNAME в настройках, используем его
                miniapp_button = buttons.WebAppButton(
                    text='🚀 Открыть миниприложение',
                    bot=BOT_USERNAME
                )
                print(f"Используется WebAppButton с BOT_USERNAME: {BOT_USERNAME}")
            else:
                # Если ничего не указано, используем LinkButton с диплинком
                raise ValueError("Не удалось определить username или ID бота. Укажите BOT_USERNAME в настройках.")
            
            # Создаем клавиатуру (список списков кнопок)
            # Один ряд с одной кнопкой
            keyboard = [[miniapp_button]]
            
            # Отправляем сообщение с клавиатурой
            # Параметр keyboard автоматически преобразуется в inline_keyboard attachment
            await message.send(welcome_text, keyboard=keyboard)
            print("Отправлено приветственное сообщение с кнопкой миниприложения")
            
        except Exception as e:
            # Если не удалось отправить с кнопкой, выводим ошибку
            error_msg = str(e)
            print(f"Ошибка при отправке кнопки: {error_msg}")
            import traceback
            traceback.print_exc()
            
            # Fallback: отправляем сообщение со ссылкой в тексте
            # Используем уже полученную информацию о боте
            if bot_username:
                deeplink = f"https://max.ru/{bot_username}?startapp"
            elif BOT_USERNAME:
                deeplink = f"https://max.ru/{BOT_USERNAME}?startapp"
            else:
                deeplink = "https://max.ru"
            
            welcome_with_link = (
                f"{welcome_text}\n\n"
                f"🔗 [Открыть миниприложение]({deeplink})"
            )
            await message.send(welcome_with_link)
            print(f"Отправлено приветственное сообщение со ссылкой в тексте (fallback): {deeplink}")


if __name__ == "__main__":
    print("Бот MAX запущен...")
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nОстановка бота...")
