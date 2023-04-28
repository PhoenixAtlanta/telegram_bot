import logging

from art import tprint
from aiogram.utils import executor

from app import dp


async def bot_start(_):
    logging.basicConfig(
        level=logging.INFO,
        filename="login_project.log",
        filemode="w",
        format="%(asctime)s %(levelname)s %(message)s",
    )

    print("█ login start █")


from handlers import client, game

# регистрируем хендлеры
client.register_handlers_client(dp)
game.register_handler_game(dp)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=bot_start)
    tprint("bot disconnected")  # оповещаем, что бот выключен
