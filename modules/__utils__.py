import discord
import discord.utils
from discord.ext import commands

import ast
import time
import asyncio
import aiohttp
from datetime import datetime, timedelta

from database import *
from utils import *

# Disposable memory
current_levels = {}
cheat_modes = {}
