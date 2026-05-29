from keep_alive import keep_alive

import json
import uuid
import asyncio
import nest_asyncio

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

keep_alive()
nest_asyncio.apply()

# ========= تنظیمات =========

TOKEN = "8337431205:AAEwtWGLLeDymM7N3sFdN_CHhkIOZWjmvzY"

ADMIN_PASSWORD = "pink1234"

STORAGE_CHANNEL = -1003815866775

CHANNELS = [

    ("Pink Channel | محافظ", "@pinklov3rs"),
    ("CleanSheetX", "@CleanSheetX"),
]

# ===========================

db = {}

waiting_upload = set()

admins = set()

users = set()

total_downloads = 0


# ========= دیتابیس =========

def save_db():

    with open(
        "db.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            db,
            f
        )


def load_db():

    global db

    try:

        with open(
            "db.json",
            "r",
            encoding="utf-8"
        ) as f:

            db = json.load(f)

    except:

        db = {}


load_db()


# ========= حذف خودکار =========

async def auto_delete(
    sent,
    context,
    user_id,
    file_key
):

    await asyncio.sleep(20)

    try:

        await context.bot.delete_message(
            chat_id=user_id,
            message_id=sent.message_id
        )

    except:
        pass

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬇️ دانلود مجدد",
                callback_data=f"redownload_{file_key}"
            )
        ]
    ])

    await context.bot.send_message(
        user_id,
        "برای دانلود مجدد کلیک کنید",
        reply_markup=keyboard
    )


# ========= چک جوین =========

async def is_joined(
    user_id,
    bot
):

    not_joined = []

    for name, username in CHANNELS:

        try:

            member = await bot.get_chat_member(
                username,
                user_id
            )

            if member.status not in [
                "member",
                "administrator",
                "creator"
            ]:

                not_joined.append(
                    (name, username)
                )

        except:

            not_joined.append(
                (name, username)
            )

    return not_joined


# ========= دکمه های جوین =========

def join_keyboard(
    not_joined,
    button_data
):

    keyboard = []

    for name, username in not_joined:

        keyboard.append([
            InlineKeyboardButton(
                name,
                url=f"https://t.me/{username.replace('@', '')}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "✅ عضو شدم",
            callback_data=button_data
        )
    ])

    return InlineKeyboardMarkup(
        keyboard
    )


# ========= استارت =========

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    global total_downloads

    user_id = update.effective_user.id

    users.add(user_id)

    file_key = None

    if context.args:

        file_key = context.args[0]

    # ========= چک جوین =========

    not_joined = await is_joined(
        user_id,
        context.bot
    )

    # ========= اگر جوین نبود =========

    if not_joined:

        if file_key:

            button_data = f"check_join_file_{file_key}"

        else:

            button_data = "check_join"

        await update.message.reply_text(
            "داخل چنل های زیر عضو شوید",
            reply_markup=join_keyboard(
                not_joined,
                button_data
            )
        )

        return

    # ========= اگر لینک فایل بود =========

    if file_key:

        if file_key not in db:

            await update.message.reply_text(
                "❌ لینک نامعتبره"
            )

            return

        total_downloads += 1

        file_data = db[file_key]

        msg = await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=STORAGE_CHANNEL,
            message_id=file_data["message_id"],
            caption="فایل را در سیو مسیج خود ذخیره کنید\n\nفایل بعد از 20 ثانیه حذف میشود"
        )

        asyncio.create_task(
            auto_delete(
                msg,
                context,
                user_id,
                file_key
            )
        )

        return

    # ========= استارت عادی =========

    await update.message.reply_text(
        "Welcome @pinklov3er"
    )


# ========= چک عضو شدم =========

async def check_join(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    global total_downloads

    query = update.callback_query

    user_id = query.from_user.id

    data = query.data

    await query.answer()

    not_joined = await is_joined(
        user_id,
        context.bot
    )

    # ========= هنوز جوین نشده =========

    if not_joined:

        await query.message.edit_text(
            "❌ هنوز عضو همه چنلا نشدی",
            reply_markup=join_keyboard(
                not_joined,
                data
            )
        )

        return

    # ========= اگر لینک فایل بود =========

    if data.startswith(
        "check_join_file_"
    ):

        file_key = data.replace(
            "check_join_file_",
            ""
        )

        try:
            await query.message.delete()
        except:
            pass

        if file_key not in db:

            await context.bot.send_message(
                user_id,
                "❌ فایل پیدا نشد"
            )

            return

        total_downloads += 1

        file_data = db[file_key]

        msg = await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=STORAGE_CHANNEL,
            message_id=file_data["message_id"],
            caption="فایل را در سیو مسیج خود ذخیره کنید\n\nفایل بعد از 20 ثانیه حذف میشود"
        )

        asyncio.create_task(
            auto_delete(
                msg,
                context,
                user_id,
                file_key
            )
        )

        return

    # ========= استارت عادی =========

    try:
        await query.message.delete()
    except:
        pass

    await context.bot.send_message(
        user_id,
        "Welcome @pinklov3er"
    )


# ========= لاگین ادمین =========

async def admin_login(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not context.args:

        await update.message.reply_text(
            "رمز رو وارد کن"
        )

        return

    password = context.args[0]

    if password != ADMIN_PASSWORD:

        await update.message.reply_text(
            "رمز اشتباهه"
        )

        return

    user_id = update.effective_user.id

    admins.add(user_id)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📤 آپلود",
                callback_data="upload"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 آمار",
                callback_data="stats"
            )
        ]
    ])

    await update.message.reply_text(
        "✅ پنل ادمین فعال شد",
        reply_markup=keyboard
    )


# ========= پنل =========

async def panel_buttons(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    global total_downloads

    query = update.callback_query

    data = query.data

    user_id = query.from_user.id

    await query.answer()

    try:
        await query.message.delete()
    except:
        pass

    if user_id not in admins:
        return

    # ========= آپلود =========

    if data == "upload":

        waiting_upload.add(
            user_id
        )

        await context.bot.send_message(
            user_id,
            "فایل یا ویدیو ارسال کن"
        )

    # ========= آمار =========

    elif data == "stats":

        await context.bot.send_message(
            user_id,
            f"👤 تعداد کاربران:\n{len(users)}\n\n"
            f"📥 تعداد دانلود فایل:\n{total_downloads}"
        )

    # ========= دانلود مجدد =========

    elif data.startswith(
        "redownload_"
    ):

        file_key = data.replace(
            "redownload_",
            ""
        )

        if file_key not in db:
            return

        total_downloads += 1

        file_data = db[file_key]

        msg = await context.bot.copy_message(
            chat_id=user_id,
            from_chat_id=STORAGE_CHANNEL,
            message_id=file_data["message_id"],
            caption="فایل را در سیو مسیج خود ذخیره کنید\n\nفایل بعد از 20 ثانیه حذف میشود"
        )

        asyncio.create_task(
            auto_delete(
                msg,
                context,
                user_id,
                file_key
            )
        )


# ========= آپلود فایل =========

async def upload_file(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if user_id not in waiting_upload:
        return

    if not (
        update.message.video
        or update.message.document
    ):
        return

    waiting_upload.remove(
        user_id
    )

    sent = await update.message.copy(
        STORAGE_CHANNEL
    )

    file_key = str(
        uuid.uuid4()
    )[:8]

    db[file_key] = {
        "message_id": sent.message_id
    }

    save_db()

    link = (
        f"https://t.me/"
        f"{context.bot.username}"
        f"?start={file_key}"
    )

    await context.bot.send_message(
        STORAGE_CHANNEL,
        f"🔗 لینک فایل:\n{link}",
        reply_to_message_id=sent.message_id
    )

    await update.message.reply_text(
        f"✅ ذخیره شد\n\n🔗 {link}"
    )


# ========= اجرا =========

app = ApplicationBuilder().token(
    TOKEN
).build()

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    CommandHandler(
        "admin",
        admin_login
    )
)

app.add_handler(
    CallbackQueryHandler(
        check_join,
        pattern="^check_join.*"
    )
)

app.add_handler(
    CallbackQueryHandler(
        panel_buttons
    )
)

app.add_handler(
    MessageHandler(
        filters.VIDEO
        | filters.Document.ALL,
        upload_file
    )
)

print("Bot Started...")

app.run_polling()
