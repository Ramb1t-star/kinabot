import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN
from logic import (
    ensure_files,
    get_movies_text,
    save_rating,
    get_recommendations,
    load_movies
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "Я бот для рекомендаций фильмов.\n\n"
        "Команды:\n"
        "/movies — список фильмов\n"
        "/recommend — получить рекомендации\n\n"
        "Чтобы оценить фильм, напиши:\n"
        "`номер,оценка`\n"
        "Пример: `1,5`"
    )


async def movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = get_movies_text()
    await update.message.reply_text(
        f"🎬 <b>Список фильмов:</b>\n\n<code>{text}</code>",
        parse_mode="HTML"
    )


async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    user_id = update.effective_user.id

    if "," not in text:
        return

    try:
        parts = text.split(",", 1)
        if len(parts) != 2:
            await update.message.reply_text("❌ Формат: `номер,оценка`\nПример: `3,5`")
            return

        movie_id = int(parts[0].strip())
        rating = int(parts[1].strip())

        if not (1 <= rating <= 5):
            await update.message.reply_text("Оценка должна быть от 1 до 5.")
            return

        success = save_rating(user_id, movie_id, rating)
        if not success:
            await update.message.reply_text(f"Фильм с номером {movie_id} не найден.")
            return

        movies_dict = load_movies()
        title = movies_dict.get(movie_id, f"№{movie_id}")
        await update.message.reply_text(f"✅ Оценка {rating} для «{title}» сохранена!")

    except ValueError:
        await update.message.reply_text("❌ Номер и оценка должны быть числами.\nПример: `1,5`")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("Не удалось сохранить оценку.")


async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    titles = get_recommendations(user_id, top_n=5)

    if not titles:
        await update.message.reply_text(
            "ℹ️ Пока нет рекомендаций.\n"
            "Оцени несколько фильмов на 4 или 5, и я подберу похожие."
        )
        return

    response = "🍿 <b>Рекомендую:</b>\n\n" + "\n".join(f"• {t}" for t in titles)
    await update.message.reply_text(response, parse_mode="HTML")


def main():
    ensure_files()  # создаём файлы при первом запуске

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("movies", movies))
    application.add_handler(CommandHandler("recommend", recommend))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rating))

    logger.info("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()