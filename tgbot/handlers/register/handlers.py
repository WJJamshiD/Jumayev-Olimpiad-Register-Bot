import os
from sys import path_importer_cache
from PIL import Image, ImageFont, ImageDraw
from dtb.settings import BASE_DIR
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext
from tgbot.models import User, Region, District
from tgbot.handlers.admin.handlers import export_users
from .keyboards import (
    make_keyboard_for_start_command,
    make_region_btns,
    make_district_btns,
    make_grade_btns,
    make_share_contact_btn,
)
from . import static_text


def command_start(update: Update, context: CallbackContext):
    u, created = User.get_user_and_created(update, context)
    if created:
        text = static_text.start_created
    else:
        text = static_text.start_not_created.format(first_name=u.first_name)
    update.message.reply_text(
        text=text,
        reply_markup=make_keyboard_for_start_command(u.is_contestant)
    )
    return 0


def register_0(update: Update, context: CallbackContext):
    """ OnClick "Ro'yxatdan o'tish": START REGISTRATION """
    update.effective_chat.send_action('typing')
    context.user_data['state'] = 1
    update.message.reply_html(
        "Iltimos <b>ism, familiya va sharif</b>ingizni kiriting.",
        reply_markup=ReplyKeyboardRemove()
    )
    return 1


def register_1(update: Update, context: CallbackContext):
    """ OnEnter "F.I.SH": ENTER FULLNAME """
    fullname = update.message.text
    if len(fullname.split()) < 3:
        update.message.reply_text("Iltimos ism-sharifingizni to'liq va to'g'ri kiriting.")
        return 1
    context.user_data['fullname'] = update.message.text
    context.user_data['state'] = 2
    update.message.reply_text("Viloyatingizni tanlang.", reply_markup=make_region_btns())
    return 2

 
def register_2(update: Update, context: CallbackContext):
    """ OnEnter "Viloyat": ENTER REGION """
    region_name = update.message.text
    region = Region.objects.get_or_none(name=region_name)
    if not region:
        update.message.reply_text(
            "Iltimos quyidagi viloyatlardan birini tanlang.",
            reply_markup=make_region_btns()
        )
        return 2
    context.user_data['region'] = region.id
    context.user_data['state'] = 3
    update.message.reply_text(
        "Tumaningizni tanglang.",
        reply_markup=make_district_btns(region.id)
    )
    return 3

 
def register_3(update: Update, context: CallbackContext):
    """ OnEnter "Tuman": ENTER DISTRICT """
    district_name = update.message.text
    district = District.objects.get_or_none(name=district_name)
    if not district:
        update.message.reply_text(
            "Iltimos quyidagi tumanlardan birini tanlang.",
            reply_markup=make_district_btns(context.user_data['region'])
        )
        return 3
    context.user_data['district'] = district.id
    context.user_data['state'] = 4
    update.message.reply_text(
        "Maktabingiz nomini kiriting.",
        reply_markup=ReplyKeyboardRemove()
    )
    return 4

 
def register_4(update: Update, context: CallbackContext):
    """ OnEnter "Maktab": ENTER SCHOOL """
    school_name = update.message.text
    if len(school_name) < 5:
        update.message.reply_text("Iltimos maktabingiz nomini to'liq yozing.")
        return 4
    context.user_data['school'] = school_name
    context.user_data['state'] = 5
    update.message.reply_text(
        "Sinfingizni tanlang.",
        reply_markup=make_grade_btns()
    )
    return 5

 
def register_5(update: Update, context: CallbackContext):
    """ OnEnter "Sinf": ENTER GRADE """
    grade = update.message.text
    all_grades = [
        '5-sinf', '6-sinf', '7-sinf',
        '8-sinf', '9-sinf', '10-sinf',
        '11-sinf', 'I bosqich', 'II bosqich',
        'III bosqich'
    ]

    if grade not in all_grades:
        update.message.reply_text(
            "Iltimos quyidagilardan birini tanlang.",
            reply_markup=make_grade_btns()
        )
        return 5
    context.user_data['grade'] = grade
    context.user_data['state'] = 6
    update.message.reply_text(
        "Telefon raqamingizni kiriting.",
        reply_markup=make_share_contact_btn()
    )
    return 6


def register_6(update: Update, context: CallbackContext):
    contact = update.message.contact
    phone = update.message.text
    if update.message.contact and update.message.contact['phone_number']:
        context.user_data['phone'] = update.message.contact['phone_number']
    elif len(phone) == 12 and phone.isdigit():
        context.user_data['phone'] = phone
    elif len(phone) == 13 and phone[1:].isdigit():
        context.user_data['phone'] = phone
    else:
        update.message.reply_text(
            "Iltimos quyidagi tugma orqali bizga telefon raqamingizni ulashing"
            " yoki telefon raqamingizni '+998907776644' yoki '998907776644' ko'rinishida kiriting."
        )
        return 6
    user, created = User.get_user_and_created(update, context)
    user.last_name = context.user_data['fullname']
    user.region_id = context.user_data['region']
    user.district_id = context.user_data['district']
    user.school = context.user_data['school']
    user.grade = context.user_data['grade']
    user.phone = context.user_data['phone']
    user.is_contestant = True
    user.save()
    context.user_data['state'] = 'menu'
    update.message.reply_text(
        "Ro'yxatdan o'tish yakunlandi.✔️✔️✔️\n\n"
        "Olimpiadada qatnashish istagini bilirganingiz uchun tashakkur.😊😊😊\n\n"
        "Bizni kuzatib boring. Yangiliklarni bot orqali yetkazib boramiz.⚡️⚡️⚡️",
        reply_markup=make_keyboard_for_start_command(True)
    )
    return 'menu'


def my_profile(update: Update, context: CallbackContext):
    user, created = User.get_user_and_created(update, context)
    if user.is_contestant:
        update.message.reply_html(
            f"      <u>Ma'lumotlaringiz</u>:\n<b>F.I.SH:</b> {user.last_name} \n"
            f"<b>Viloyat:</b> {user.region} \n<b>Tuman:</b> {user.district} \n"
            f"<b>Maktab:</b> {user.school} \n<b>Sinf:</b> {user.grade}",
            reply_markup=make_keyboard_for_start_command(user.is_contestant)
        )
    else:
        update.message.reply_text()


def get_results(update: Update, context: CallbackContext):
    user, created = User.get_user_and_created(update, context)
    update.message.reply_text(
        "Olimpiada yakunlangach umumiy natijalarni ushbu bo'limda ko'rishingiz mumkin.",
        reply_markup=make_keyboard_for_start_command(user.is_contestant)
    )


def get_certificate(update: Update, context: CallbackContext):
    user, created = User.get_user_and_created(update, context)
    if not user.is_contestant:
        update.message.reply_text(
            "Siz ro'yxatdan o'tmagansiz.",
            reply_markup=make_keyboard_for_start_command(user.is_contestant)
        )
    else:
        if user.certificate:
            with open(user.certificate.path, "rb") as certificate:
                update.message.reply_photo(
                    photo=certificate,
                    reply_markup=make_keyboard_for_start_command(user.is_contestant)
                )
            print('replied')
            return 'menu'

        path_to_template = os.path.join(BASE_DIR, "certificate.jpg")
        path_to_font = os.path.join(BASE_DIR, "Source_Serif_Pro", "SourceSerifPro-SemiBoldItalic.ttf")
        certificate_template = Image.open(path_to_template)
        text_font = ImageFont.truetype(path_to_font, 45)
        text = user.last_name
        certificate_editable = ImageDraw.Draw(certificate_template)
        certificate_editable.text((230, 435), text, (0, 0, 0), font=text_font)
        path_for_new_certificate = os.path.join(BASE_DIR, "certificates", f"certificate-user-{user.user_id}.jpg")
        print('path for new', path_for_new_certificate)
        user.certificate = os.path.join("certificates", f"certificate-user-{user.user_id}.jpg")
        user.save()
        certificate_template.save(path_for_new_certificate)
        print('saved', certificate_template)
        with open(path_for_new_certificate, "rb") as certificate:
            print(' read new cer', certificate)
            update.message.reply_photo(
                photo=certificate,
                reply_markup=make_keyboard_for_start_command(user.is_contestant)
            )
        print('replied')

def get_info(update: Update, context: CallbackContext):
    user, created = User.get_user_and_created(update, context)
    if user.is_admin:
        export_users(update, context)
    else:
        update.message.reply_text(
            "Tez orada ushbu bo'limga olimpiada haqidagi batafsil ma'lumotlarni joylaymiz.",
            reply_markup=make_keyboard_for_start_command(user.is_contestant)
        )


def get_statistics(update: Update, context: CallbackContext):
    user, created = User.get_user_and_created(update, context)
    contestants = User.objects.filter(is_contestant=True).count()
    update.message.reply_html(
        "Olimpiada to'g'risidagi umumiy statistika:\n"
        f"Ayni paytda <u>ro'yxatdan o'tgan ishtirokchilar soni</u> - <b>{contestants}</b> ta",
        reply_markup=make_keyboard_for_start_command(user.is_contestant)
    )


def get_partners(update: Update, context: CallbackContext):
    user, created = User.get_user_and_created(update, context)
    update.message.reply_text(
        "Hamkorlarimiz...",
        reply_markup=make_keyboard_for_start_command(user.is_contestant)
    )


def get_results(update: Update, context: CallbackContext):
    user, created = User.get_user_and_created(update, context)
    update.message.reply_text(
        "Olimpiada yakunlangach umumiy natijalarni ushbu bo'limda ko'rishingiz mumkin.",
        reply_markup=make_keyboard_for_start_command(user.is_contestant)
    )


def main_menu(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)
    return "menu"


def delete_msg(update: Update, context: CallbackContext):
    update.message.delete()
