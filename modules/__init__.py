import discord
import discord.utils
from discord.ext import commands

import ast
import time
import asyncio
from datetime import datetime, timedelta

from database import *
from utils import *

# Disposable memory
current_levels = {}
cheat_modes = {}

def permission(level: int):
    helpers, moderators, admins, owner = [], [], [], []
    if level <= 1: helpers = botDB.get('helpers') or []
    if level <= 2: moderators = botDB.get('moderators') or []
    if level <= 3: admins = botDB.get('admins') or []
    if level <= 4: owner = Config.OWNER
    return helpers + moderators + admins + owner

def get_difficulty_visual(user_id, difficulty):
    user_data = userDB.get(user_id)
    if not user_data:
        return EMOJIS["na"]

    visuals = user_data.get("visuals", [0, 0])
    if len(visuals) < 2:
        visuals += [0] * (2 - len(visuals))

    name = DIFFICULTIES[difficulty - 1]

    if difficulty >= 10:
        if visuals[0]:
            return EMOJIS[name]
        else:
            if name in [
                "supremedemon", "ultimatedemon", "legendarydemon",
                "mythicaldemon", "infinitedemon", "grandpademon"
            ]:
                return EMOJIS["extremedemon"]
            return EMOJIS[name]
    else:
        if visuals[1]:
            return EMOJIS[name]
        else:
            fallback_map = {
                "casual": "hard",
                "tough": "harder",
                "cruel": "insane"
            }
            name = fallback_map.get(name, name)
            return EMOJIS[name]
        
def get_search_difficulties(user_id, name):
    user_data = userDB.get(user_id)
    visuals = user_data.get("visuals", [0, 0])
    name = name.lower()

    result = []

    difficulty_map = {
        "hard": ["hard", "casual"],
        "harder": ["harder", "tough"],
        "insane": ["insane", "cruel"],
        "extremedemon": [
            "extremedemon", "supremedemon", "ultimatedemon",
            "legendarydemon", "mythicaldemon", "infinitedemon", "grandpademon"
        ]
    }

    if name not in DIFFICULTIES:
        return []

    for base, group in difficulty_map.items():
        if name in group:
            if name in ["hard", "harder", "insane"] and visuals[1] == 0:
                names_to_check = group
            elif name == "extremedemon" and visuals[0] == 0:
                names_to_check = group
            else:
                names_to_check = [name]
            break
    else:
        names_to_check = [name]

    for diff in names_to_check:
        if diff in DIFFICULTIES:
            result.append(DIFFICULTIES.index(diff) + 1)

    return result
