import time
import random

from loguru import logger
from fake_useragent import UserAgent

from src.client import Client
from config import LOGS_PATH, RES_PATH, PROXY_PATH, SLEEP_DELAY, MAX_ATTEMPTS


logger.add(LOGS_PATH, format='{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}', rotation="100 MB")

def main():
    logger.info("Скрипт начинает работу...")
    url = 'https://www.winamax.es/challenges/expresso/16-25/'
    driver.get(url)

    previous_data = []

    try:
        while True:
            try:
                data = Client.get_data_with_retry(driver, MAX_ATTEMPTS)
                if not data:
                    logger.error("Не удалось получить данные после нескольких попыток.")
                else:
                    logger.info("Таблица готова.")
                    for row in data:
                        print(row)
                    if Client.data_changed(previous_data, data):
                        Client.write_to_csv(data, RES_PATH)
                        logger.success("Данные изменились и были записаны в CSV-файл.")
                        previous_data = data.copy()
                    else:
                        logger.info("Данные не изменились. Пропуск записи.")
            except Exception as err:
                logger.error(f"Произошла ошибка: {err}")
            
            a = random.randint(SLEEP_DELAY[0], SLEEP_DELAY[1])
            logger.info(f"Ожидание {a} секунд до следующего обновления...")
            time.sleep(a)
    
    except KeyboardInterrupt:
        logger.info("Скрипт останавливается...")

    finally:
        driver.quit()

if __name__ == "__main__":
    user_agent = UserAgent().random
    proxies = Client.read_proxies_from_file(PROXY_PATH)

    if not proxies:
        logger.warning(f"Прокси не указаны. Продолжаю работу без них...")
        driver = Client.setup_driver(user_agent=user_agent)
        main()
    else:
        for proxy in proxies:
            proxy_parts = proxy.split(':')
            if len(proxy_parts) == 3:
                proxy_with_auth = f'http://{proxy_parts[0]}:{proxy_parts[1]}:{proxy_parts[2]}'
                driver = Client.setup_driver(user_agent=user_agent, proxy=proxy_with_auth)
                main()
