import working_data

# my_quiz = await bot.send_poll(message.chat.id, 'Мессенджер, автор которого Павел Дуров', ['Telegram', 'Viber', 'WhatsApp', 'Messenger'], type='regular', is_anonymous=False)

async def create_voting(state, topic: str, variants: list=[], id_people=False, type_voting="regular", is_anonymous=False) -> dict:
    if id_people:
        variants = [await working_data.players_prop(state, nickname=player, key="nickname") for player in variants]


    voting_params = {"topic": topic, "variants": variants, "type": type_voting, "is_anonymous": is_anonymous}

    return voting_params



