import os
import csv
from collections import defaultdict
from typing import List, Dict, Tuple

from config import MOVIES_FILE, RATINGS_FILE


def ensure_files():
    """Создаём нужные файлы, если их нет"""
    if not os.path.exists(RATINGS_FILE):
        with open(RATINGS_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["user_id", "movie_id", "rating"])

    if not os.path.exists(MOVIES_FILE):
        with open(MOVIES_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "title"])
            movies = [
                (1, "Интерстеллар"),
                (2, "Начало"),
                (3, "Матрица"),
                (4, "Бойцовский клуб"),
                (5, "Форрест Гамп"),
                (6, "Зелёная миля"),
                (7, "Побег из Шоушенка"),
                (8, "Криминальное чтиво"),
                (9, "Властелин колец"),
                (10, "Гладиатор"),
                (11, "Тёмный рыцарь"),
                (12, "Престиж"),
                (13, "Остров проклятых"),
                (14, "Игра в имитацию"),
                (15, "Джокер"),
                (16, "1+1"),
                (17, "Одержимость"),
                (18, "Достать ножи"),
                (19, "Паразиты"),
                (20, "Дюна"),
            ]
            writer.writerows(movies)


def load_movies() -> Dict[int, str]:
    movies = {}
    if not os.path.exists(MOVIES_FILE):
        return movies

    with open(MOVIES_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                movies[int(row["id"])] = row["title"]
            except (ValueError, KeyError):
                continue
    return movies


def get_movies_text(limit: int = 20) -> str:
    movies = load_movies()
    if not movies:
        return "Список фильмов пуст."
    lines = [f"{mid}. {title}" for mid, title in list(movies.items())[:limit]]
    return "\n".join(lines)


def save_rating(user_id: int, movie_id: int, rating: int) -> bool:
    movies = load_movies()
    if movie_id not in movies:
        return False

    with open(RATINGS_FILE, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, movie_id, rating])
    return True


def load_ratings() -> List[Tuple[int, int, int]]:
    ratings = []
    if not os.path.exists(RATINGS_FILE):
        return ratings

    with open(RATINGS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ratings.append((
                    int(row["user_id"]),
                    int(row["movie_id"]),
                    int(row["rating"])
                ))
            except (ValueError, KeyError):
                continue
    return ratings


def get_recommendations(user_id: int, top_n: int = 5) -> List[str]:
    """
    Простой рекомендатель:
    - Берём фильмы, которые пользователь оценил на 4-5
    - Ищем других пользователей с похожими вкусами
    - Рекомендуем фильмы, которые они высоко оценили
    """
    ratings = load_ratings()
    movies = load_movies()

    if not ratings or not movies:
        return []

    # Оценки текущего пользователя
    user_ratings = {mid: r for uid, mid, r in ratings if uid == user_id}
    if not user_ratings:
        return []

    liked = {mid for mid, r in user_ratings.items() if r >= 4}
    if not liked:
        return []

    # Находим похожих пользователей
    similar_users = defaultdict(int)
    for uid, mid, r in ratings:
        if uid == user_id:
            continue
        if mid in liked and r >= 4:
            similar_users[uid] += 1

    if not similar_users:
        return []

    # Собираем кандидатов
    candidates = defaultdict(float)
    for uid, mid, r in ratings:
        if uid not in similar_users:
            continue
        if mid in user_ratings:  # уже смотрел
            continue
        if r >= 4:
            candidates[mid] += r * similar_users[uid]

    if not candidates:
        return []

    sorted_candidates = sorted(candidates.items(), key=lambda x: x[1], reverse=True)

    result = []
    for mid, _ in sorted_candidates[:top_n]:
        if mid in movies:
            result.append(movies[mid])

    return result