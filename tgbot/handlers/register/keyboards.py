from telegram import InlineKeyboardButton, InlineKeyboardMarkup,\
     ReplyKeyboardMarkup, KeyboardButton

from tgbot.models import Region, District
from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON
from tgbot.handlers.onboarding.static_text import github_button_text, secret_level_button_text


# def make_keyboard_for_start_command() -> InlineKeyboardMarkup:
#     buttons = [[
#         InlineKeyboardButton(github_button_text, url="https://github.com/ohld/django-telegram-bot"),
#         InlineKeyboardButton(secret_level_button_text, callback_data=f'{SECRET_LEVEL_BUTTON}')
#     ]]

#     return InlineKeyboardMarkup(buttons)


def make_keyboard_for_start_command(is_contestant) -> ReplyKeyboardMarkup:
    if not is_contestant:
        buttons = [
            ["📝 Ro'yxatdan o'tish"],
            [" ℹ️ Ma'lumot", "🤝 Hamkorlar"],
            ["🥇 Natijalar", "📈 Statistika"],
        ]
    else:
        buttons = [
            ["👤 Profilim", "🎫 Sertifikat",],
            ["🥇 Natijalar", "📈 Statistika"],
            [" ℹ️ Ma'lumot", "🤝 Hamkorlar"],
        ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def make_region_btns() -> ReplyKeyboardMarkup:
    buttons = []
    regions = Region.objects.all()
    for i in range(0, 14, 2):
        buttons.append([r.name for r in regions[i:i+2]])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def make_district_btns(region_id) -> ReplyKeyboardMarkup:
    buttons = []
    districts = District.objects.filter(region__id=region_id)
    for i in range(0, districts.count(), 2):
        buttons.append([d.name for d in districts[i:i+2]])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def make_grade_btns() -> ReplyKeyboardMarkup:
    buttons = [
        ['5-sinf', '6-sinf', '7-sinf'],
        ['8-sinf', '9-sinf', '10-sinf'],
        ['11-sinf'],
        ['I bosqich', 'II bosqich', 'III bosqich'],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def make_share_contact_btn() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton("📱 Telefon raqamimni jo'natish", request_contact=True)]]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)
