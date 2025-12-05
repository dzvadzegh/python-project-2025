"""
Генератор FSRS-данных для флэшкард-бота с персонализацией сложности
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

np.random.seed(42)


def generate_realistic_words(n_samples=10000):
    """Генерирует слова разной сложности"""
    easy_words = ['cat', 'dog', 'house', 'apple', 'run', 'eat', 'book']
    medium_words = ['photosynthesis', 'mitochondria', 'democracy', 'algorithm']
    hard_words = ['supercalifragilisticexpialidocious', 'floccinaucinihilipilification']

    word_types = np.random.choice(['easy', 'medium', 'hard'], n_samples, p=[0.5, 0.4, 0.1])

    words = []
    base_difficulties = []

    for word_type in word_types:
        if word_type == 'easy':
            words.append(np.random.choice(easy_words))
            base_difficulties.append(np.random.uniform(0.1, 0.4))
        elif word_type == 'medium':
            words.append(np.random.choice(medium_words))
            base_difficulties.append(np.random.uniform(0.4, 0.7))
        else:
            words.append(np.random.choice(hard_words))
            base_difficulties.append(np.random.uniform(0.7, 1.0))

    return words, base_difficulties


def generate_user_profiles(n_users=50):
    """Разные пользователи имеют разную склонность к ошибкам"""
    return {
        uid: np.random.normal(0.5, 0.15)
        for uid in range(100, 100 + n_users)
    }


def fsrs_update(stability, difficulty, user_rating):
    """FSRS формула обновления stability"""
    if user_rating == 1:  # Again
        stability *= 0.2
    elif user_rating == 2:  # Hard
        stability *= 0.7
    elif user_rating == 3:  # Good
        stability *= 1.3
    elif user_rating == 4:  # Easy
        stability *= 2.0

    difficulty_factor = 3.0 / (1.25 + difficulty * 1.25)
    stability *= difficulty_factor

    return max(1.0, stability)


def main():
    n_samples = 10000
    print(f"Генерируем {n_samples} FSRS записей...")

    words, base_difficulties = generate_realistic_words(n_samples)

    user_profiles = generate_user_profiles()
    user_ids = np.random.choice(list(user_profiles.keys()), n_samples)

    data = {
        'word_id': range(1, n_samples + 1),
        'user_id': user_ids,
        'word_text': words,
        'base_difficulty': base_difficulties,
        'repeat_count': np.random.randint(1, 15, n_samples),
        'stability': np.random.exponential(5, n_samples).clip(1, 50),
        'created_days_ago': np.random.exponential(10, n_samples).clip(1, 60),
    }

    personal_difficulties = []
    for i, uid in enumerate(data['user_id']):
        user_bias = user_profiles[uid]
        base_diff = data['base_difficulty'][i]
        personal_diff = base_diff + user_bias * 0.3
        personal_diff = np.clip(personal_diff, 0.1, 1.0)
        personal_difficulties.append(personal_diff)

    data['personal_difficulty'] = personal_difficulties
    data['difficulty'] = np.array(base_difficulties) * 0.7 + np.array(personal_difficulties) * 0.3
    success_prob = 0.8 * (1 - data['difficulty']) + 0.2 * np.log(data['repeat_count'])
    data['user_rating'] = np.random.choice([1, 2, 3, 4], n_samples, p=[0.1, 0.2, 0.4, 0.3])

    new_stabilities = []
    for i in range(n_samples):
        new_stab = fsrs_update(
            data['stability'][i],
            data['difficulty'][i],
            data['user_rating'][i]
        )
        new_stabilities.append(new_stab)
    data['stability'] = new_stabilities

    stability_arr = np.array(data['stability'], dtype=float)
    noise = np.random.uniform(0.8, 1.2, size=len(stability_arr))

    data['next_interval_days'] = np.clip(
        stability_arr * noise,
        a_min=1,
        a_max=90,
    ).astype(int)

    data['ml_score'] = np.clip(
        0.5 + 0.3 * (1 - data['difficulty']) + 0.2 * np.log(data['repeat_count']),
        0.1, 1.0
    )

    df = pd.DataFrame(data)

    os.makedirs('../data', exist_ok=True)
    output_path = '../data/fsrs_synthetic_data.csv'
    df.to_csv(output_path, index=False)

    print(f"\nДанные сохранены: {output_path}")
    print(f"{df.shape[0]} строк, {df.shape[1]} столбцов")
    print("\nКлючевые метрики:")
    print(f"Сложность: {df['difficulty'].mean():.2f} ± {df['difficulty'].std():.2f}")
    print(f"Stability: {df['stability'].mean():.1f} дней")
    print(f"Next interval: {df['next_interval_days'].mean():.1f} дней")
    print(f"ML score: {df['ml_score'].mean():.2f}")
    print(f"User ratings: {df['user_rating'].value_counts().sort_index().to_dict()}")

    print("\nПервые 5 записей:")
    print(
        df[['word_text', 'user_id', 'difficulty', 'stability', 'user_rating', 'next_interval_days', 'ml_score']].head())


if __name__ == "__main__":
    main()