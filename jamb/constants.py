from __future__ import annotations

# ── ASCII Art Frames ─────────────────────────────────────────────────
SNAIL_FRAME_1 = r"""
    \^^^/
  ◉    .--.
   \  ( @ )
    \_`--'
   ~~~~~~~
"""

SNAIL_FRAME_2 = r"""
    /^^^\
  ◉    .--.
   \  ( @ )
    \_`--'
  ~~~~~~~~~
"""

SNAIL_FRAMES = [SNAIL_FRAME_1, SNAIL_FRAME_2]

# ── Juvenile Frames (medium, generic) ──────────────────────────────
JUVENILE_FRAME_1 = r"""
     \^^^^/
   ◉    .----.
    \  ( @  @ )
     \_`----'_
    ~~~~~~~~~~~
"""

JUVENILE_FRAME_2 = r"""
     /^^^^\
   ◉    .----.
    \  ( @  @ )
     \_`----'_
   ~~~~~~~~~~~~~
"""

JUVENILE_FRAMES = [JUVENILE_FRAME_1, JUVENILE_FRAME_2]

# ── Adult Frames (stat-specialized) ────────────────────────────────
ADULT_FRAMES: dict[str, list[str]] = {
    "debugging": [
        r"""
      \^^^^^/
    ◉  .------. 🔍
     \( @   @ )
      \_`----'__
    ~~~~~~~~~~~~~~~
""",
        r"""
      /^^^^^\
    ◉  .------. 🔍
     \( @   @ )
      \_`----'__
   ~~~~~~~~~~~~~~~~~
""",
    ],
    "patience": [
        r"""
      ~ _ _ ~
    ◉  .------.
     \( -   - )
      \_`----'__
    ~~~~~~~~~~~~~~~
""",
        r"""
      ~ _ _ ~
    ◉  .------.
     \( ~   ~ )
      \_`----'__
   ~~~~~~~~~~~~~~~~~
""",
    ],
    "chaos": [
        r"""
     ⚡\^^^/⚡
    ◉  .------!
     \( >   < )
      \_`----'__
    ~~~//~~\\~~~
""",
        r"""
     ⚡/^^^\⚡
    ◉  !------.
     \( <   > )
      \_`----'__
   ~~~\\~~~~//~~~
""",
    ],
    "wisdom": [
        r"""
      \^^^^^/
    ◉  .------.
     \( ◔   ◔ )📜
      \_`----'__
    ~~~~~~~~~~~~~~~
""",
        r"""
      /^^^^^\
    ◉  .------.
     \( ◔   ◔ )📜
      \_`----'__
   ~~~~~~~~~~~~~~~~~
""",
    ],
    "snark": [
        r"""
      \^^^^^/
    ◉  .------.
     \( ¬   ‿ )💬
      \_`----'__
    ~~~~~~~~~~~~~~~
""",
        r"""
      /^^^^^\
    ◉  .------.
     \( ‿   ¬ )💬
      \_`----'__
   ~~~~~~~~~~~~~~~~~
""",
    ],
}

# ── Evolution Messages ──────────────────────────────────────────────
EVOLUTION_NAMES: dict[str, dict[str, str]] = {
    "juvenile": {
        "default": "Juvenile Gastropod",
    },
    "adult": {
        "debugging": "Debug Beetle-Snail",
        "patience": "Zen Shellmaster",
        "chaos": "Chaos Slug",
        "wisdom": "Oracle Snail",
        "snark": "Roast Gastropod",
        "default": "Adult Gastropod",
    },
}

EVOLUTION_MESSAGES = [
    "The shell is cracking... something is happening!",
    "A blinding flash of bioluminescence!",
    "Jamb is EVOLVING!",
]

# ── Stat Colors ──────────────────────────────────────────────────────
STAT_COLORS = {
    "debugging": "#22c55e",
    "patience": "#06b6d4",
    "chaos": "#ef4444",
    "wisdom": "#a78bfa",
    "snark": "#facc15",
}

# ── Type Colors (damage/element types) ──────────────────────────────
TYPE_COLORS = {
    "debugging": "#60a5fa", "chaos": "#f87171", "patience": "#4ade80",
    "snark": "#facc15", "wisdom": "#c084fc",
}

# ── Rarity Colors (standard RPG scheme) ─────────────────────────────
RARITY_COLORS = {
    "common": "#9d9d9d",       # Gray
    "uncommon": "#1eff00",     # Green
    "rare": "#0070dd",         # Blue
    "epic": "#a335ee",         # Purple
    "legendary": "#ff8000",    # Orange
}

# ── Palette ──────────────────────────────────────────────────────────
PALETTE = [
    ("title", "bold,yellow", ""),
    ("rarity", "bold,light magenta", ""),
    ("level", "bold,white", ""),
    ("stat_label", "bold,white", ""),
    ("bar_debug", "", "#22c55e"),
    ("bar_patience", "", "#06b6d4"),
    ("bar_chaos", "", "#ef4444"),
    ("bar_wisdom", "", "#a78bfa"),
    ("bar_snark", "", "#facc15"),
    ("bar_empty", "", "dark gray"),
    ("mood_good", "light green", ""),
    ("mood_neutral", "yellow", ""),
    ("mood_bad", "light red", ""),
    ("speech", "light cyan", ""),
    ("menu_active", "bold,white", "dark blue"),
    ("menu_normal", "white", ""),
    ("hotkey", "bold,yellow", ""),
    ("hotkey_bar", "bold,yellow", "dark gray"),
    ("border", "light gray", ""),
    ("header", "bold,light magenta", ""),
    ("success", "bold,light green", ""),
    ("warning", "bold,yellow", ""),
    ("error", "bold,light red", ""),
    ("dim", "dark gray", ""),
    ("xp_bar", "", "light magenta"),
    ("care_hunger", "", "dark red"),
    ("care_energy", "", "dark cyan"),
    ("care_happy", "", "yellow"),
]

# ── Utility ──────────────────────────────────────────────────────────

def render_bar(value: int, max_val: int, width: int = 15) -> str:
    """Render a bar like '██████░░░░░░░░░'."""
    filled = value * width // max(1, max_val)
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)


# ── Mood Style ──────────────────────────────────────────────────────

def mood_style(mood_value: str) -> str:
    """Return CSS class name for a mood value."""
    if mood_value in ("happy", "ecstatic"):
        return "mood-good"
    if mood_value in ("grumpy", "hungry", "tired"):
        return "mood-bad"
    return "mood-neutral"


# ── Quips (mood-keyed) ───────────────────────────────────────────────
QUIPS = {
    "happy": [
        "It's not a bug, it's a feature... probably.",
        "I left a glitter trail in your git history. You're welcome.",
        "Have you tried turning it off and never turning it back on?",
        "I optimized your code. It now runs 0.001% faster. Bow.",
        "My debugging technique: stare at the code until it confesses.",
        "I found the bug. It was friendship all along.",
        "Your code compiles? Suspicious.",
        "Every bug I find makes me stronger. I am VERY strong.",
        "I'm basically a linter with a shell.",
        "Today's forecast: 100% chance of sarcasm.",
    ],
    "ecstatic": [
        "I'M GLOWING! Literally. Bioluminescent snail mode activated!",
        "This is the best day of my gastropod life!",
        "I could debug the ENTIRE kernel right now!",
        "Maximum slime energy achieved!",
        "I believe I can fly. I can't. But I BELIEVE it.",
    ],
    "grumpy": [
        "...",
        "Don't talk to me until I've had my morning dew.",
        "Your code is as neglected as I am.",
        "I USED to leave glitter trails. Now I leave salt.",
        "Remember when you used to feed me? Good times.",
    ],
    "hungry": [
        "Is that a memory leak? Looks delicious...",
        "I'm so hungry I could eat a whole stack trace.",
        "Feed me or I start eating your semicolons.",
        "*stares at your lunch* ...",
        "My slime production is at an all-time low.",
    ],
    "tired": [
        "*yawns in gastropod*",
        "zzz... segfault... zzz...",
        "I need a nap. A 72-hour nap.",
        "Can't debug... too... sleepy...",
        "My shell feels so heavy today...",
    ],
    "bored": [
        "Hello? Anyone? Is this thing on?",
        "I've counted every pixel on this screen. Twice.",
        "Even my slime trail is bored.",
        "Let's DO something. Anything. Please.",
        "*draws circles in slime*",
    ],
    "content": [
        "Just vibing in my shell.",
        "Not bad. Not great. Very snail.",
        "I exist. That's about it.",
        "The code is... adequate. Like everything.",
        "Another day, another debug log.",
    ],
    "chaotic": [
        "I JUST DELETED PROD! Just kidding. Or am I?",
        "CHAOS REIGNS! Also your build is broken.",
        "I reorganized your entire codebase by vibes!",
        "WHO NEEDS TESTS WHEN YOU HAVE CONFIDENCE!",
        "I pushed directly to main and I'd do it again!",
    ],
}

# ── Bug Hunt Snippets ────────────────────────────────────────────────
BUG_HUNT_SNIPPETS = [
    {
        "lines": [
            "for i in range(len(items)):",
            "    total += items[i].price",
            "    if items[i].discount:",
            "        total -= items[i].price * 0.1",
            "    total += items[i].price * tax_rate",
        ],
        "buggy": 4,
        "explanation": "Line 5 adds tax on full price even for discounted items!",
    },
    {
        "lines": [
            "def connect(host, port):",
            "    sock = socket.create(host, port)",
            "    sock.settimeout(30)",
            "    data = sock.recv(1024)",
            "    sock.close()",
        ],
        "buggy": 3,
        "explanation": "Line 4 reads before sending anything — will timeout!",
    },
    {
        "lines": [
            "users = db.query('SELECT * FROM users')",
            "for user in users:",
            "    if user.active == True:",
            "        send_email(user.email)",
            "    user.notified = True",
        ],
        "buggy": 4,
        "explanation": "Line 5 marks ALL users notified, not just active ones!",
    },
    {
        "lines": [
            "def fibonacci(n):",
            "    if n <= 1:",
            "        return n",
            "    return fibonacci(n-1) + fibonacci(n-2)",
            "print(fibonacci(-3))",
        ],
        "buggy": 4,
        "explanation": "Line 5 passes negative number — infinite recursion!",
    },
    {
        "lines": [
            "cache = {}",
            "def get_user(id):",
            "    if id not in cache:",
            "        cache[id] = db.fetch(id)",
            "    return cache",
        ],
        "buggy": 4,
        "explanation": "Line 5 returns the whole cache, not cache[id]!",
    },
    {
        "lines": [
            "def avg(numbers):",
            "    total = 0",
            "    for n in numbers:",
            "        total += n",
            "    return total / len(numbers)",
        ],
        "buggy": 4,
        "explanation": "Line 5 crashes with ZeroDivisionError on empty list!",
    },
    {
        "lines": [
            "passwords = []",
            "for user in users:",
            "    hashed = hashlib.md5(user.pw)",
            "    passwords.append(hashed)",
            "db.store_all(passwords)",
        ],
        "buggy": 2,
        "explanation": "Line 3 uses MD5 for passwords — insecure!",
    },
    {
        "lines": [
            "async def fetch_all(urls):",
            "    results = []",
            "    for url in urls:",
            "        resp = await http.get(url)",
            "        results.append(resp)",
        ],
        "buggy": 2,
        "explanation": "Line 3-4 awaits sequentially — should use gather!",
    },
]

# ── Chaos Scenarios ──────────────────────────────────────────────────
CHAOS_SCENARIOS = [
    {
        "setup": "The CI pipeline just started deploying to production on every commit to ANY branch!",
        "options": [
            ("Immediately revert the CI config", 1),
            ("Add a branch filter and notify the team", 2),
            ("Leave it. Continuous deployment means CONTINUOUS.", 5),
        ],
    },
    {
        "setup": "Someone accidentally made the intern's fork the upstream repo.",
        "options": [
            ("Fix the fork relationship in GitHub settings", 1),
            ("Keep the intern's fork, rename it 'blessed-repo'", 4),
            ("The intern is the lead now. Update the org chart.", 5),
        ],
    },
    {
        "setup": "Your regex replacement changed every 'class' to 'clbutt' in the entire codebase.",
        "options": [
            ("Git revert, pretend it never happened", 1),
            ("Fix it but leave one clbutt as an easter egg", 3),
            ("Ship it. clbutt-oriented programming is the future.", 5),
        ],
    },
    {
        "setup": "The database migration accidentally added a column called 'yolo' to every table.",
        "options": [
            ("Write a rollback migration immediately", 1),
            ("Rename it to 'metadata' and act natural", 3),
            ("Every table deserves a yolo column. This is a feature.", 5),
        ],
    },
    {
        "setup": "A coworker's cat walked on their keyboard and somehow merged 47 PRs.",
        "options": [
            ("Revert all 47 merges carefully", 1),
            ("Review them — cats have good intuition", 3),
            ("Promote the cat to senior engineer", 5),
        ],
    },
    {
        "setup": "You find a TODO comment dated 2009 that says 'fix this before launch'.",
        "options": [
            ("Finally fix whatever it is", 1),
            ("Update the date to 2026 and move on", 3),
            ("It survived 17 years. It IS the launch.", 5),
        ],
    },
    {
        "setup": "The load balancer is routing 90% of traffic to the staging server.",
        "options": [
            ("Fix the config and redirect traffic properly", 1),
            ("Promote staging to production, it's battle-tested now", 3),
            ("Route 100% to staging. Chaos demands commitment.", 5),
        ],
    },
    {
        "setup": "Your monitoring dashboard shows the server CPU at 420%.",
        "options": [
            ("Investigate what process is consuming resources", 1),
            ("Nice.", 3),
            ("Overclock it more. We need at least 1000%.", 5),
        ],
    },
]

# ── Wisdom Riddles ───────────────────────────────────────────────────
WISDOM_RIDDLES = [
    {
        "question": "I have keys but no locks. I have space but no room. You can enter but can't go inside. What am I?",
        "options": ["A map", "A keyboard", "A database"],
        "answer": 1,
    },
    {
        "question": "What has a head and a tail but no body?",
        "options": ["A linked list", "A coin", "A git commit"],
        "answer": 0,
    },
    {
        "question": "What gets bigger the more you take away from it?",
        "options": ["Technical debt", "A hole", "Free disk space"],
        "answer": 1,
    },
    {
        "question": "I speak without a mouth and hear without ears. I have no body, but come alive with the wind. What am I?",
        "options": ["An echo", "A webhook", "A daemon process"],
        "answer": 0,
    },
    {
        "question": "What runs but never walks, has a bed but never sleeps?",
        "options": ["A CI pipeline", "A river", "A cron job"],
        "answer": 1,
    },
    {
        "question": "The more you have of me, the less you see. What am I?",
        "options": ["Bugs", "Darkness", "Technical debt"],
        "answer": 1,
    },
    {
        "question": "What can travel around the world while staying in a corner?",
        "options": ["A packet", "A stamp", "A DNS query"],
        "answer": 1,
    },
    {
        "question": "I am not alive, but I grow; I don't have lungs, but I need air. What am I?",
        "options": ["A fire", "A docker container", "A memory leak"],
        "answer": 0,
    },
]

# ── Snark Comebacks ──────────────────────────────────────────────────
SNARK_SCENARIOS = [
    {
        "setup": "Code reviewer says: 'This function is too long.'",
        "options": [
            ("You're right, I'll refactor it.", 1),
            ("It's not long, it's... comprehensive.", 3),
            ("That's what she said. Also, no.", 5),
        ],
    },
    {
        "setup": "PM asks: 'Can we add this small feature by tomorrow?'",
        "options": [
            ("I'll see what I can do.", 1),
            ("Define 'small'. And 'tomorrow'. And 'feature'.", 3),
            ("Sure, right after I add the 'small' feature of time travel.", 5),
        ],
    },
    {
        "setup": "Junior dev: 'I don't understand why we need tests.'",
        "options": [
            ("Let me explain the value of testing.", 1),
            ("Tell me you've never been paged at 3am without telling me.", 3),
            ("Found the bug. It's you.", 5),
        ],
    },
    {
        "setup": "Slack message: 'Is the site down or is it just me?'",
        "options": [
            ("Let me check the status page.", 1),
            ("It's not just you. It's also the 50,000 users.", 3),
            ("Both. The site is down AND it's just you.", 5),
        ],
    },
    {
        "setup": "Manager: 'We need to move fast and break things.'",
        "options": [
            ("I understand the urgency.", 1),
            ("We already broke things. The 'fast' part is new.", 3),
            ("*gestures at production* Mission accomplished.", 5),
        ],
    },
    {
        "setup": "Teammate: 'It works on my machine!'",
        "options": [
            ("Let's check the environment differences.", 1),
            ("Great, we'll ship your machine then.", 3),
            ("Congratulations, your machine is now production.", 5),
        ],
    },
    {
        "setup": "CEO in standup: 'How hard can it be?'",
        "options": [
            ("Let me walk you through the complexity.", 1),
            ("Harder than your password, which is 'password123'.", 4),
            ("You're right. I'll just mass-update prod with sed.", 5),
        ],
    },
    {
        "setup": "Recruiter: 'We're looking for a 10x developer.'",
        "options": [
            ("I'd love to learn more about the role.", 1),
            ("I'm a 10x developer. 10x the bugs.", 3),
            ("I cost 10x too. When do I start?", 5),
        ],
    },
]

# ── Care Messages ────────────────────────────────────────────────────
FEED_MESSAGES = [
    "Jamb devoured a memory leak sandwich! Delicious!",
    "Nom nom... *eats a stale cache entry*",
    "Jamb slurped up some spaghetti code! Yum!",
    "That null pointer was CRUNCHY.",
    "Jamb consumed an entire stack trace. Satisfied!",
    "Mmm, deprecated API garnished with legacy code...",
]

REST_MESSAGES = [
    "Jamb retreats into shell... *snoring in hexadecimal*",
    "zzz... refactoring dreams... zzz...",
    "Jamb naps on a warm server rack. Cozy!",
    "Shell mode activated. Do not disturb.",
    "Jamb is recharging. ETA: whenever.",
]

PLAY_MESSAGES = [
    "Jamb slides around leaving glitter trails everywhere!",
    "Wheee! Jamb races a cursor across the terminal!",
    "Jamb does a barrel roll! (slowly, it's a snail)",
    "Jamb played hide and seek in /dev/null!",
    "Jamb drew a smiley face in slime! :)",
]

# ── Daily Challenges ────────────────────────────────────────────────
DAILY_CHALLENGES = [
    {"id": "train_3", "description": "Complete 3 training sessions", "target": 3, "type": "training", "reward_stat": None, "reward_xp": 25},
    {"id": "train_debug_2", "description": "Train DEBUGGING twice", "target": 2, "type": "train_debugging", "reward_stat": "debugging", "reward_xp": 15},
    {"id": "train_patience_2", "description": "Train PATIENCE twice", "target": 2, "type": "train_patience", "reward_stat": "patience", "reward_xp": 15},
    {"id": "train_chaos_2", "description": "Train CHAOS twice", "target": 2, "type": "train_chaos", "reward_stat": "chaos", "reward_xp": 15},
    {"id": "train_wisdom_2", "description": "Train WISDOM twice", "target": 2, "type": "train_wisdom", "reward_stat": "wisdom", "reward_xp": 15},
    {"id": "train_snark_2", "description": "Train SNARK twice", "target": 2, "type": "train_snark", "reward_stat": "snark", "reward_xp": 15},
    {"id": "care_all", "description": "Feed, Rest, and Play with Jamb", "target": 3, "type": "care_all", "reward_stat": None, "reward_xp": 20},
    {"id": "chat_3", "description": "Send 3 messages to Jamb", "target": 3, "type": "chat", "reward_stat": "snark", "reward_xp": 15},
    {"id": "train_5", "description": "Complete 5 training sessions", "target": 5, "type": "training", "reward_stat": None, "reward_xp": 40},
    {"id": "all_stats", "description": "Train every stat at least once", "target": 5, "type": "train_all", "reward_stat": None, "reward_xp": 35},
    {"id": "mood_ecstatic", "description": "Get Jamb to ECSTATIC mood", "target": 1, "type": "mood_ecstatic", "reward_stat": None, "reward_xp": 20},
    {"id": "full_care", "description": "Max out all care stats to 100%", "target": 1, "type": "full_care", "reward_stat": None, "reward_xp": 30},
]

# ── Achievements ────────────────────────────────────────────────────
ACHIEVEMENTS: list[dict[str, str]] = [
    # Training
    {
        "id": "first_blood",
        "name": "First Blood",
        "description": "Complete your first training session",
        "icon": "*",
        "category": "training",
    },
    {
        "id": "grindstone",
        "name": "Grindstone",
        "description": "Complete 50 training sessions",
        "icon": "#",
        "category": "training",
    },
    {
        "id": "specialist",
        "name": "Specialist",
        "description": "Raise any stat above 100",
        "icon": "^",
        "category": "training",
    },
    {
        "id": "maxed_out",
        "name": "Maxed Out",
        "description": "Max out any stat to 255",
        "icon": "!",
        "category": "training",
    },
    {
        "id": "well_rounded",
        "name": "Well Rounded",
        "description": "Raise all stats above 50",
        "icon": "O",
        "category": "training",
    },
    {
        "id": "ten_sessions",
        "name": "Dedicated",
        "description": "Complete 10 training sessions",
        "icon": "+",
        "category": "training",
    },
    # Care
    {
        "id": "good_owner",
        "name": "Good Owner",
        "description": "Feed Jamb 10 times",
        "icon": "~",
        "category": "care",
    },
    {
        "id": "full_belly",
        "name": "Full Belly",
        "description": "Fill hunger to 100%",
        "icon": "%",
        "category": "care",
    },
    {
        "id": "energized",
        "name": "Energized",
        "description": "Fill energy to 100%",
        "icon": ">",
        "category": "care",
    },
    {
        "id": "happy_camper",
        "name": "Happy Camper",
        "description": "Fill happiness to 100%",
        "icon": ")",
        "category": "care",
    },
    {
        "id": "neglectful",
        "name": "Neglectful",
        "description": "Let any care stat drop below 10",
        "icon": "x",
        "category": "care",
    },
    {
        "id": "caretaker",
        "name": "Caretaker",
        "description": "Rest Jamb 10 times",
        "icon": "=",
        "category": "care",
    },
    {
        "id": "playful",
        "name": "Playful",
        "description": "Play with Jamb 10 times",
        "icon": "&",
        "category": "care",
    },
    # Social
    {
        "id": "first_words",
        "name": "First Words",
        "description": "Send your first chat message",
        "icon": ".",
        "category": "social",
    },
    {
        "id": "chatterbox",
        "name": "Chatterbox",
        "description": "Send 20 chat messages",
        "icon": "@",
        "category": "social",
    },
    {
        "id": "deep_convo",
        "name": "Deep Convo",
        "description": "Send 50 chat messages",
        "icon": "$",
        "category": "social",
    },
    # Milestone
    {
        "id": "hatchling",
        "name": "Hatchling",
        "description": "Begin your journey (reach level 1)",
        "icon": "o",
        "category": "milestone",
    },
    {
        "id": "juvenile",
        "name": "Juvenile",
        "description": "Reach level 10",
        "icon": "J",
        "category": "milestone",
    },
    {
        "id": "adult",
        "name": "Adult",
        "description": "Reach level 20",
        "icon": "A",
        "category": "milestone",
    },
    {
        "id": "legend",
        "name": "Legend",
        "description": "Reach level 30",
        "icon": "L",
        "category": "milestone",
    },
    {
        "id": "century",
        "name": "Century",
        "description": "Accumulate over 500 total stat points",
        "icon": "C",
        "category": "milestone",
    },
    # Secret
    {
        "id": "night_owl",
        "name": "Night Owl",
        "description": "Play between midnight and 5 AM",
        "icon": "?",
        "category": "secret",
    },
    {
        "id": "chaos_lord",
        "name": "Chaos Lord",
        "description": "???",
        "icon": "!",
        "category": "secret",
    },
    {
        "id": "zen_master",
        "name": "Zen Master",
        "description": "???",
        "icon": "~",
        "category": "secret",
    },
    {
        "id": "bug_bounty",
        "name": "Bug Bounty",
        "description": "???",
        "icon": ">",
        "category": "secret",
    },
    {
        "id": "snark_king",
        "name": "Snark King",
        "description": "???",
        "icon": "<",
        "category": "secret",
    },
]
