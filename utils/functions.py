import random
import colorama

def level_time(seconds):
    if seconds < 15: return "Tiny"
    if seconds < 30: return "Short"
    if seconds < 60: return "Medium"
    if seconds < 120: return "Long"
    return "XL"

def predict_level_completion(level, user):
    final_result = 0

    level_difficulty = level['difficulty']
    max_user_difficulty = user['hardest'][0]
    levels_at_max_difficulty = user['hardest'][1]
    level_id = level.get('level_id')
    played_data = user['played'][str(level_id)]
    attempts = played_data['attempts']
    record = played_data['record']
    length = level['time']

    if level_difficulty == 1:
        final_result = 100
    else:
        def base_attempts(difficulty):
            return 0.14105 * difficulty**4 - 3.65008 * difficulty**3 + 39.1527 * difficulty**2 - 149.3046 * difficulty + 199.5352

        expected_attempts = base_attempts(level_difficulty)
        difficulty_difference = max_user_difficulty - level_difficulty
        skill_factor = max(0.1, 1 - 0.15 * difficulty_difference - 0.05 * levels_at_max_difficulty)
        adjusted_attempts = max(1, expected_attempts * skill_factor)

        length_multiplier = 2 / (1 + length / 90)
        average_atts = int(adjusted_attempts * random.uniform(1.35, 1.65) * length_multiplier)

        win_probability = 1 / (adjusted_attempts * 0.5 + 1)
        fluke_multiplier = max(0.01, record / 100.0)

        attempts_multiplier = 1.0
        if average_atts > 0:
            ratio = attempts / average_atts
            if ratio > 1/2:
                attempts_multiplier = ratio*2

        final_win_probability = win_probability * fluke_multiplier * attempts_multiplier

        if random.random() <= final_win_probability:
            final_result = 100
        else:
            skill_gap_penalty = max(0.2, 1 - 0.1 * (level_difficulty - max_user_difficulty))
            experience_bonus = min(1.0, 0.05 * levels_at_max_difficulty)
            max_theoretical_record = int(min(99, 90 * skill_gap_penalty + 10 * experience_bonus))

            roll = random.random()
            max_possible = min(max_theoretical_record, int(40 + attempts * 0.5 + record * 0.5))
            progress_chance = (1 - win_probability * attempts_multiplier * 10)

            if roll < progress_chance * 0.6 and record > 1:
                percent = max(1, int(record * random.uniform(0.20, 0.60)))
            elif roll < progress_chance or (record >= 95 and random.random() <= 0.95):
                percent = int(record * random.uniform(0.60, 1.00))
            else:
                max_gain = max(1, int((max_possible - record) * 0.3))
                percent = record + random.randint(1, max_gain)

            final_result =  max(1, min(percent, max_possible))

    print(f"\
{colorama.Fore.YELLOW}WP: {win_probability:.4f}, {colorama.Style.RESET_ALL}\
FM: {fluke_multiplier:.4f}, \
AM: {attempts_multiplier:.4f}, \
LM: {length_multiplier:.4f}, \
{colorama.Fore.CYAN}FWP: {final_win_probability:.4f}, \
{colorama.Fore.CYAN}FRP: {final_result}, \
{colorama.Fore.GREEN}AA: {average_atts} {colorama.Style.RESET_ALL}"
    )

    return final_result

def get_advanced_ranking(top):
    if top <= 10: return 1
    if top <= 50: return 2
    if top <= 100: return 3
    if top <= 200: return 4
    if top <= 500: return 5
    if top <= 1000: return 6
    return 7

def get_ranking(top):
    if top <= 1: return 1
    if top <= 2: return 2
    if top <= 5: return 3
    if top <= 10: return 4
    if top <= 20: return 5
    if top <= 100: return 6
    return 7
