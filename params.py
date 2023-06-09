from string import ascii_letters, digits
from dataclasses import dataclass, field
from typing import List, Dict


# дата класс, с переменными, которые отвечают за все текстовое содержание кода
@dataclass(frozen=True)
class ParamGame:
    # типы карт в игре бункер
    all_carts: List = field(
        default_factory=lambda: [
            "Багаж",
            "Биология",
            "Здоровье",
            "Катастрофа",
            "Особые условия",
            "Особые условия",
            "Профессия",
            "Факты",
            "Хобби",
        ]
    )

    # карты которые раздаются пользователю, при запросе
    cart_for_game: List = field(
        default_factory=lambda: [
            "Багаж",
            "Биология",
            "Здоровье",
            "Профессия",
            "Факты",
            "Хобби",
            "Особые условия", 
            "Особые условия"
        ]
    )

    # текст,который будет на пользовательских кнопках
    buttons_text: Dict = field(
        default_factory=lambda: {
            "go_start": ("/go",),
            "all_step": ("/all",),
            "default_state": ("текущий_игрок", "порядок_игроков"),
            "profession": ("Профессия",),
            "carts_specifications": (
                "Багаж",
                "Биология",
                "Здоровье",
                "Профессия",
                "Факты",
                "Хобби",
            ),
        }
    )

    # рандомные слова, одно из случайных слов надо будет написать чтобы оповестить бота об участии
    worlds_joining_game: List = field(
        default_factory=lambda: [
            "/кровать",
            "/листы",
            "/очки",
            "/дверь",
            "/брюки",
            "/нож",
            "/колесо",
            "/клавиатура",
            "/книжный",
            "/магазин",
            "/звезда",
            "/молоток",
            "/чечевица",
            "/гостинная",
            "/зоопарк",
            "/пояс",
            "/горячий",
            "/колледж",
            "/воды",
            "/инструмент",
            "/книга",
            "/вкладка",
            "/плоский",
            "/вилка",
            "/сообщение",
            "/стейк",
            "/обезьяна",
            "/линзы",
            "/салат",
            "/собака",
            "/конфеты",
            "/гитара",
            "/солнце",
            "/ручка",
            "/снег",
            "/портфель",
            "/град",
            "/человек",
            "/нефть",
            "/замок",
            "/обезьяна",
            "/рука",
            "/горы",
            "/взрыв",
            "/дождь",
            "/птица",
            "/винт",
            "/монитор",
            "/сверлить",
            "/металл",
            "/часы",
            "/цветок",
            "/грусть",
            "/кресло",
            "/леденец",
            "/пластик",
            "/здание",
            "/школа",
            "/звук",
            "/трава",
            "/машина",
            "/лодка",
            "/разрешение",
            "/телефон",
            "/лодка",
            "/ноутбук",
            "/наушники",
            "/бегемот",
            "/луг",
            "/пиджак",
            "/палка",
            "/парусная",
            "/ключи",
            "/спутник",
            "/детская",
            "/кроватка",
            "/звенеть",
            "/мясо",
            "/мобильный",
            "/офис",
            "/ракета",
            "/храм",
            "/спальная",
            "/проектор",
            "/книги",
            "/картина",
            "/комната",
            "/пистолет",
            "/футболка",
            "/открытки",
            "/бритва",
            "/экран",
            "/руккола",
            "/отделение",
            "/локоть",
            "/диван",
            "/контейнер",
            "/стул",
            "/перчатки",
            "/пуля",
            "/растение",
            "/карандаш",
            "/дезодорант",
            "/принтер",
            "/дневники",
            "/замок",
            "/навесной",
            "/галстук",
            "/бутылка",
            "/стена",
            "/матч",
            "/обувь",
            "/шоколад",
            "/древесина",
            "/карта",
            "/бомбить",
            "/фонарь",
            "/телевизор",
            "/слепой",
            "/алюминий",
            "/салфетка",
            "/утюг",
            "/облако",
            "/убежище",
            "/кофе",
            "/газета",
            "/планета",
            "/колледж",
            "/ключ",
            "/радио",
            "/рубашка",
            "/компьютер",
            "/зуб",
            "/шариковая",
            "/ручка",
            "/дом",
            "/лайм",
            "/блюдо",
            "/окно",
            "/лодка",
            "/вешалка",
            "/свет",
            "/волосы",
            "/кремовый",
            "/цвет",
            "/глаз",
            "/вечеринка",
            "/дайвер",
            "/дерево",
            "/говорящий",
            "/зуб",
        ]
    )

    # символы, которые допустима для nickname-a пользователя
    nickname_symbols: str = ascii_letters + digits + "_"
