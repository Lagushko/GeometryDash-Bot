import random
import colorama

MAIN_LEVELS = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22)
JSON_FILE = "data/data.json"

GAMEMODES = ["cube", "ship", "ball", "ufo", "wave", "robot", "spider", "swing"]
PRICES = [0, 500, 500, 1000, 1000, 1500, 1500, 2000, 2000, 2500]

DIFFICULTIES = ["auto", "easy", "normal", "casual", "hard", "harder", "tough", "insane", "cruel", 
                "easydemon", "mediumdemon", "harddemon", "insanedemon", "extremedemon",
                "supremedemon", "ultimatedemon", "legendarydemon", 
                "mythicaldemon", "infinitedemon", "grandpademon"]
ORBS = [0, 50, 75, 125, 175, 225, 275, 350, 425, 500]
DIAMONDS = [0, 3, 5, 6, 7, 8, 9, 10, 11, 12]

ICONS = [
    [
        "<:cube0:1371433864924237834>", 
        "<:cube1:1372970036477558934>", "<:cube2:1372975018543288431>", "<:cube3:1372976688022945954>",
        "<:cube4:1372976699444035725>", "<:cube5:1372976707476127904>", "<:cube6:1372976717551108117>",
        "<:cube7:1372976727013195997>", "<:cube8:1372976733497594058>", "<:cube9:1372976757283623023>"
    ],
    [
        "<:ship0:1371434213353586729>", 
        "<:ship1:1372970050201325588>", "<:ship2:1372975030639525959>", "<:ship3:1372978104750047312>",
        "<:ship4:1372978117408329760>", "<:ship5:1372978125084037201>", "<:ship6:1372978133808054372>",
        "<:ship7:1372978142590930994>", "<:ship8:1372978151071813653>", "<:ship9:1372978159791640647>"
    ],
    [
        "<:ball0:1371434253547733022>", 
        "<:ball1:1372970057788952787>", "<:ball2:1372975041171423363>", "<:ball3:1372982563051929622>",
        "<:ball4:1372982573315395646>", "<:ball5:1372982588699840602>", "<:ball6:1372982595654127626>",
        "<:ball7:1372982628604706867>", "<:ball8:1372982636259180665>", "<:ball9:1372982661538250834>"
    ],
    [
        "<:ufo0:1371434281666215938>", 
        "<:ufo1:1372970067607818320>", "<:ufo2:1372975051061858395>", "<:ufo3:1372984235522265180>",
        "<:ufo4:1372984248763551898>", "<:ufo5:1372984267923128400>", "<:ufo6:1372984274772426833>",
        "<:ufo7:1372984287116263606>", "<:ufo8:1372984299011182634>", "<:ufo9:1372984306871566467>"
    ],
    [
        "<:wave0:1372970790043254874>", 
        "<:wave1:1372970075031605399>", "<:wave2:1372989117935386654>", "<:wave3:1372984894413733918>",
        "<:wave4:1372984902416466031>", "<:wave5:1372984908925894686>", "<:wave6:1372984919004807322>",
        "<:wave7:1372984926718136401>", "<:wave8:1372984933664034918>", "<:wave9:1372984943579496469>"
    ],
    [
        "<:robot0:1371434308157308948>", 
        "<:robot1:1372970084661858427>", "<:robot2:1372975066819858532>", "<:robot3:1372985664101945394>",
        "<:robot4:1372985671597428736>", "<:robot5:1372985679205634361>", "<:robot6:1372985686956970086>",
        "<:robot7:1372985694452060170>", "<:robot8:1372985705747185734>", "<:robot9:1372985712105885707>"
    ],
    [
        "<:spider0:1371434334006804561>", 
        "<:spider1:1372970093306450003>", "<:spider2:1372975104278925413>", "<:spider3:1372986457597149294>",
        "<:spider4:1372986465767788564>", "<:spider5:1372986475011899482>", "<:spider6:1372986483207573534>",
        "<:spider7:1372986491705229527>", "<:spider8:1372986500479717558>", "<:spider9:1372986509388681226>"
    ],
    [
        "<:swing0:1372968567632302090>", 
        "<:swing1:1372970103339225200>", "<:swing2:1372975113984806932>", "<:swing3:1372987133152858213>",
        "<:swing4:1372987147606560798>", "<:swing5:1372987156309610506>", "<:swing6:1372987163167162470>",
        "<:swing7:1372987172524658688>", "<:swing8:1372987179416027266>", "<:swing9:1372987186034770050>"
    ]
]
EMOJIS = {
    "na": "<:na:1373042293384286409>",
    "auto": "<:auto:1371216864935673936>",
    "easy": "<:easy:1371216926985949368>",
    "normal": "<:normal:1371216961064927332>",
    "casual": "<:casual:1373034993428987974>",
    "hard": "<:hard:1371216992308297830>",
    "harder": "<:harder:1371216999660781579>",
    "tough": "<:tough:1373034999703670846>",
    "insane": "<:insane:1371217009421058048>",
    "cruel": "<:cruel:1373035008360583319>",
    "easydemon": "<:easydemon:1371217022435721317>",
    "mediumdemon": "<:mediumdemon:1371217030841237645>",
    "harddemon": "<:harddemon:1371217042459459596>",
    "insanedemon": "<:insanedemon:1371217051418493010>",
    "extremedemon": "<:extremedemon:1371217245463646238>",
    "supremedemon": "<:supremedemon:1373032013791232171>",
    "ultimatedemon": "<:ultimatedemon:1373032049488957450>",
    "legendarydemon": "<:legendarydemon:1373032086193176717>",
    "mythicaldemon": "<:mythicaldemon:1373032114488082625>",
    "infinitedemon": "<:infinitedemon:1373032148084326512>",
    "grandpademon": "<:grandpademon:1373032194192445470>",
    "moon": "<:moon:1371217748511821956>",
    "diamond": "<:diamond:1371217831081021631>",
    "goldcoin": "<:goldcoin:1371218581185892442>",
    "usercoin": "<:usercoin:1371218644926988338>",
    "demon": "<:demon:1371218778771292313>",
    "star": "<:star:1371226265163399239>",
    "download": "<:download:1371226292845940796>",
    "like": "<:like:1371226330607386767>",
    "dislike": "<:dislike:1371545519595192360>",
    "time": "<:time:1371226375314477179>",
    "manaorbs": "<:manaorbs:1371376582962446417>",
    "creatorpoints": "<:creatorpoints:1371377460255653920>",
    "checkmark": "<:checkmark:1371854020108488904>",
    "moderator": "<:moderator:1371866138178355240>",
    "admin": "<:admin:1371866148756258976>",
    "lockedcoin": "<:lockedcoin:1371874459710914650>",
    "rank1": "<:rank1:1372534930986369064>",
    "rank2": "<:rank2:1372535305164427455>",
    "rank3": "<:rank3:1372535312672358481>",
    "rank4": "<:rank4:1372535829548892241>",
    "rank5": "<:rank5:1372535840387104889>",
    "rank6": "<:rank6:1372535847680868494>",
    "rank7": "<:rank7:1372535854924304404>",
}

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
