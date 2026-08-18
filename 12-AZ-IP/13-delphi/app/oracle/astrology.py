"""
DelPhi — Astrology Oracle Engine
Western astrology: Sun sign, Moon sign, Rising sign, daily horoscopes.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

# ---------------------------------------------------------------------------
# Zodiac sign data
# ---------------------------------------------------------------------------

SIGNS: list[dict] = [
    {
        "name": "Aries", "symbol": "♈", "glyph": "♈",
        "element": "Fire", "modality": "Cardinal", "ruler": "Mars",
        "date_range": "March 21 – April 19",
        "start_month": 3, "start_day": 21, "end_month": 4, "end_day": 19,
        "keywords": "courage, leadership, initiative, impulsive, pioneer",
        "description": (
            "Aries is the first sign of the zodiac — bold, pioneering, and full of raw energy. "
            "Ruled by Mars, Aries charges headlong into new experiences with infectious enthusiasm. "
            "The Ram embodies the spirit of fresh beginnings and fearless action."
        ),
        "upright_traits": "Courageous, determined, confident, enthusiastic, optimistic",
        "shadow_traits": "Impulsive, impatient, aggressive, confrontational, short-tempered",
        "compatible_with": ["Leo", "Sagittarius", "Gemini", "Aquarius"],
        "lucky_numbers": [1, 8, 17],
        "lucky_colors": ["red", "orange"],
    },
    {
        "name": "Taurus", "symbol": "♉", "glyph": "♉",
        "element": "Earth", "modality": "Fixed", "ruler": "Venus",
        "date_range": "April 20 – May 20",
        "start_month": 4, "start_day": 20, "end_month": 5, "end_day": 20,
        "keywords": "stability, sensuality, determination, patience, material comfort",
        "description": (
            "Taurus is the steadfast Bull — patient, reliable, and deeply connected to the physical world. "
            "Ruled by Venus, Taurus savors beauty, comfort, and the pleasures of the earth. "
            "Their strength lies in endurance and unwavering commitment."
        ),
        "upright_traits": "Reliable, patient, practical, devoted, responsible",
        "shadow_traits": "Stubborn, possessive, materialistic, resistant to change",
        "compatible_with": ["Virgo", "Capricorn", "Cancer", "Pisces"],
        "lucky_numbers": [2, 6, 9, 12],
        "lucky_colors": ["green", "pink"],
    },
    {
        "name": "Gemini", "symbol": "♊", "glyph": "♊",
        "element": "Air", "modality": "Mutable", "ruler": "Mercury",
        "date_range": "May 21 – June 20",
        "start_month": 5, "start_day": 21, "end_month": 6, "end_day": 20,
        "keywords": "communication, curiosity, adaptability, wit, duality",
        "description": (
            "Gemini, the Twins, is the great communicator of the zodiac. "
            "Ruled by Mercury, Gemini moves quickly between ideas, people, and perspectives. "
            "They excel at connecting dots, storytelling, and adapting to any situation."
        ),
        "upright_traits": "Versatile, expressive, curious, affectionate, quick-witted",
        "shadow_traits": "Nervous, inconsistent, indecisive, two-faced, scattered",
        "compatible_with": ["Libra", "Aquarius", "Aries", "Leo"],
        "lucky_numbers": [5, 7, 14, 23],
        "lucky_colors": ["yellow", "light green"],
    },
    {
        "name": "Cancer", "symbol": "♋", "glyph": "♋",
        "element": "Water", "modality": "Cardinal", "ruler": "Moon",
        "date_range": "June 21 – July 22",
        "start_month": 6, "start_day": 21, "end_month": 7, "end_day": 22,
        "keywords": "nurturing, intuition, home, emotion, protective",
        "description": (
            "Cancer, the Crab, is ruled by the Moon and deeply attuned to emotion and intuition. "
            "Cancers are the nurturers of the zodiac — deeply loving, protective of those they care for, "
            "and profoundly connected to home and family."
        ),
        "upright_traits": "Tenacious, imaginative, loyal, protective, sympathetic",
        "shadow_traits": "Moody, suspicious, manipulative, insecure, pessimistic",
        "compatible_with": ["Scorpio", "Pisces", "Taurus", "Virgo"],
        "lucky_numbers": [2, 3, 15, 20],
        "lucky_colors": ["white", "silver", "sea green"],
    },
    {
        "name": "Leo", "symbol": "♌", "glyph": "♌",
        "element": "Fire", "modality": "Fixed", "ruler": "Sun",
        "date_range": "July 23 – August 22",
        "start_month": 7, "start_day": 23, "end_month": 8, "end_day": 22,
        "keywords": "creativity, generosity, leadership, drama, pride",
        "description": (
            "Leo, the Lion, is ruled by the Sun and radiates warmth, confidence, and creative power. "
            "Leos are natural leaders and performers who light up every room they enter. "
            "At their best they are generous, loyal, and inspiring."
        ),
        "upright_traits": "Creative, passionate, generous, warm-hearted, cheerful",
        "shadow_traits": "Arrogant, stubborn, self-centered, lazy, inflexible",
        "compatible_with": ["Aries", "Sagittarius", "Gemini", "Libra"],
        "lucky_numbers": [1, 3, 10, 19],
        "lucky_colors": ["gold", "yellow", "orange"],
    },
    {
        "name": "Virgo", "symbol": "♍", "glyph": "♍",
        "element": "Earth", "modality": "Mutable", "ruler": "Mercury",
        "date_range": "August 23 – September 22",
        "start_month": 8, "start_day": 23, "end_month": 9, "end_day": 22,
        "keywords": "analysis, service, precision, health, perfectionism",
        "description": (
            "Virgo, the Virgin, is ruled by Mercury and approaches life with analytical precision. "
            "Detail-oriented and service-minded, Virgo excels at improving systems and supporting others. "
            "Their gift is discernment — seeing what needs refining."
        ),
        "upright_traits": "Analytical, loyal, hardworking, practical, kind",
        "shadow_traits": "Shyness, worry, critical, overcritical, fussy",
        "compatible_with": ["Taurus", "Capricorn", "Cancer", "Scorpio"],
        "lucky_numbers": [5, 14, 15, 23, 32],
        "lucky_colors": ["grey", "beige", "pale yellow"],
    },
    {
        "name": "Libra", "symbol": "♎", "glyph": "♎",
        "element": "Air", "modality": "Cardinal", "ruler": "Venus",
        "date_range": "September 23 – October 22",
        "start_month": 9, "start_day": 23, "end_month": 10, "end_day": 22,
        "keywords": "balance, harmony, justice, beauty, partnership",
        "description": (
            "Libra, the Scales, is ruled by Venus and seeks balance, harmony, and beauty in all things. "
            "Libras are natural diplomats — fair-minded, cooperative, and gifted at seeing all sides of an issue. "
            "Partnership and justice are their core values."
        ),
        "upright_traits": "Cooperative, diplomatic, gracious, fair-minded, social",
        "shadow_traits": "Indecisive, avoids confrontations, self-pity, resentful",
        "compatible_with": ["Gemini", "Aquarius", "Leo", "Sagittarius"],
        "lucky_numbers": [4, 6, 13, 15, 24],
        "lucky_colors": ["pink", "light blue"],
    },
    {
        "name": "Scorpio", "symbol": "♏", "glyph": "♏",
        "element": "Water", "modality": "Fixed", "ruler": "Pluto/Mars",
        "date_range": "October 23 – November 21",
        "start_month": 10, "start_day": 23, "end_month": 11, "end_day": 21,
        "keywords": "transformation, depth, power, mystery, intensity",
        "description": (
            "Scorpio, the Scorpion, is ruled by Pluto and Mars — the most intense and transformative sign. "
            "Scorpios dive fearlessly into the depths of emotion, mystery, and power. "
            "Their greatest gift is the ability to transform themselves and others."
        ),
        "upright_traits": "Resourceful, brave, passionate, stubborn, true friend",
        "shadow_traits": "Distrusting, jealous, secretive, violent, manipulative",
        "compatible_with": ["Cancer", "Pisces", "Virgo", "Capricorn"],
        "lucky_numbers": [8, 11, 18, 22],
        "lucky_colors": ["scarlet", "red", "rust"],
    },
    {
        "name": "Sagittarius", "symbol": "♐", "glyph": "♐",
        "element": "Fire", "modality": "Mutable", "ruler": "Jupiter",
        "date_range": "November 22 – December 21",
        "start_month": 11, "start_day": 22, "end_month": 12, "end_day": 21,
        "keywords": "adventure, philosophy, freedom, optimism, travel",
        "description": (
            "Sagittarius, the Archer, is ruled by Jupiter and is the great adventurer and philosopher of the zodiac. "
            "Restless and freedom-loving, Sagittarius seeks truth through experience, travel, and big ideas. "
            "Their optimism is boundless and infectious."
        ),
        "upright_traits": "Generous, idealistic, curious, adventurous, enthusiastic",
        "shadow_traits": "Promises more than can deliver, very impatient, blunt",
        "compatible_with": ["Aries", "Leo", "Libra", "Aquarius"],
        "lucky_numbers": [3, 7, 9, 12, 21],
        "lucky_colors": ["blue", "purple"],
    },
    {
        "name": "Capricorn", "symbol": "♑", "glyph": "♑",
        "element": "Earth", "modality": "Cardinal", "ruler": "Saturn",
        "date_range": "December 22 – January 19",
        "start_month": 12, "start_day": 22, "end_month": 1, "end_day": 19,
        "keywords": "ambition, discipline, responsibility, tradition, mastery",
        "description": (
            "Capricorn, the Sea-Goat, is ruled by Saturn and is the most disciplined achiever of the zodiac. "
            "Patient, strategic, and deeply responsible, Capricorn climbs every mountain through sheer determined effort. "
            "Their rewards come through mastery and perseverance."
        ),
        "upright_traits": "Responsible, disciplined, self-control, good managers",
        "shadow_traits": "Know-it-all, unforgiving, condescending, expecting worst",
        "compatible_with": ["Taurus", "Virgo", "Scorpio", "Pisces"],
        "lucky_numbers": [4, 8, 13, 22],
        "lucky_colors": ["brown", "black"],
    },
    {
        "name": "Aquarius", "symbol": "♒", "glyph": "♒",
        "element": "Air", "modality": "Fixed", "ruler": "Uranus/Saturn",
        "date_range": "January 20 – February 18",
        "start_month": 1, "start_day": 20, "end_month": 2, "end_day": 18,
        "keywords": "innovation, humanitarianism, independence, originality, technology",
        "description": (
            "Aquarius, the Water-Bearer, is ruled by Uranus and is the visionary rebel of the zodiac. "
            "Original, independent, and deeply humanitarian, Aquarius thinks in systems and futures. "
            "They are ahead of their time — the inventors and activists who shift paradigms."
        ),
        "upright_traits": "Progressive, original, independent, humanitarian, logical",
        "shadow_traits": "Runs from emotional expression, temperamental, aloof",
        "compatible_with": ["Gemini", "Libra", "Aries", "Sagittarius"],
        "lucky_numbers": [4, 7, 11, 22, 29],
        "lucky_colors": ["light blue", "silver"],
    },
    {
        "name": "Pisces", "symbol": "♓", "glyph": "♓",
        "element": "Water", "modality": "Mutable", "ruler": "Neptune/Jupiter",
        "date_range": "February 19 – March 20",
        "start_month": 2, "start_day": 19, "end_month": 3, "end_day": 20,
        "keywords": "spirituality, compassion, imagination, sensitivity, transcendence",
        "description": (
            "Pisces, the Fish, is ruled by Neptune and is the dreamer and mystic of the zodiac. "
            "Deeply empathic and spiritually attuned, Pisces dissolves the boundaries between self and other. "
            "Their gift is compassion — they feel the entire ocean of human experience."
        ),
        "upright_traits": "Compassionate, artistic, intuitive, gentle, wise",
        "shadow_traits": "Fearful, overly trusting, sad, escapist, victim or martyr",
        "compatible_with": ["Cancer", "Scorpio", "Taurus", "Capricorn"],
        "lucky_numbers": [3, 9, 12, 15, 18, 24],
        "lucky_colors": ["sea green", "violet", "light blue"],
    },
]

SIGN_INDEX: dict[str, dict] = {s["name"]: s for s in SIGNS}

# Approximate Moon sign table (simplified — days from Jan 1 for moon position)
# Moon spends ~2.5 days per sign, completing 12 signs in ~29.5 days
MOON_SIGN_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Daily horoscope templates per sign
HOROSCOPE_TEMPLATES: dict[str, list[str]] = {
    "Aries": [
        "Bold energy surges through you today — trust your instincts and take decisive action.",
        "Mars energizes your ambitions. A new project or initiative gains momentum.",
        "Your natural leadership shines. Others look to you for direction and courage.",
        "Channel your fire constructively today. Patience will amplify your results.",
        "An unexpected opportunity appears. Move swiftly — Aries fortune favors the bold.",
    ],
    "Taurus": [
        "Financial matters come into focus. Your patience and steady approach pay dividends.",
        "Venus blesses your aesthetic sense — beautify your space and nourish your senses.",
        "Your reliability is your greatest asset today. Others depend on your steady presence.",
        "Resist the urge to overindulge. Balance pleasure with productive effort.",
        "A creative project benefits from your careful, thorough attention.",
    ],
    "Gemini": [
        "Your communication gifts are heightened — networking and outreach yield great results.",
        "Mercury sharpens your wit. Conversations lead to surprising insights.",
        "Your curiosity opens new doors. Follow that thread of interest wherever it leads.",
        "Avoid scattering your energy — choose one focus and commit to it fully today.",
        "An exchange of ideas sparks something new. Share your thoughts freely.",
    ],
    "Cancer": [
        "Emotional intelligence is your superpower today. Trust your gut completely.",
        "Home and family matters receive positive energy. Nurture your inner circle.",
        "The Moon heightens your intuition — what you sense is accurate.",
        "Create boundaries that protect your sensitive energy. Self-care is productive.",
        "A memory or dream offers guidance. The past illuminates the present path.",
    ],
    "Leo": [
        "Your creative fire burns bright. Express yourself boldly and unapologetically.",
        "The Sun amplifies your natural magnetism. Leadership opportunities arise.",
        "Generosity returns to you tenfold today. Give freely from your abundant heart.",
        "Your enthusiasm is contagious — inspire those around you with your vision.",
        "Recognition for your efforts is coming. Stay true to your authentic self.",
    ],
    "Virgo": [
        "Your analytical gifts solve a problem that has stumped others. Details matter.",
        "Mercury supports your practical efforts. Systems and routines run smoothly.",
        "Service to others brings deep satisfaction today. Your help is genuinely needed.",
        "Health and wellness routines deserve attention — small adjustments create lasting change.",
        "Your eye for improvement is valuable. Offer your insights constructively.",
    ],
    "Libra": [
        "Harmony and balance are your north stars today. Seek the middle path in all things.",
        "Venus enhances your social grace — relationships flourish under your diplomatic touch.",
        "A decision that has lingered becomes clearer. Trust your sense of fairness.",
        "Beauty in all forms uplifts you today. Surround yourself with what you love.",
        "Partnership energies are strong — collaboration yields better results than solo effort.",
    ],
    "Scorpio": [
        "Your penetrating insight reveals hidden truths that others miss entirely.",
        "Pluto's power supports deep transformation. What must end makes way for rebirth.",
        "Trust your instincts in all matters today — your radar is precisely calibrated.",
        "Research and investigation uncover valuable information. Dig deeper.",
        "Emotional honesty — especially with yourself — unlocks something profound.",
    ],
    "Sagittarius": [
        "Your optimism is entirely justified today. Expand your horizons boldly.",
        "Jupiter opens doors to adventure, learning, and philosophical breakthrough.",
        "Travel, study, or spiritual practice brings the insight you've been seeking.",
        "Share your hard-won wisdom freely. Your perspective is needed.",
        "A burst of inspiration points toward your next great adventure. Follow the arrow.",
    ],
    "Capricorn": [
        "Your disciplined effort is building toward a significant milestone. Keep climbing.",
        "Saturn rewards your patience. A long-term plan shows signs of bearing fruit.",
        "Practical matters move smoothly under your steady management today.",
        "Your reputation for reliability opens an important door. Be consistent.",
        "Strategic planning pays off. Think long-term and act with precision.",
    ],
    "Aquarius": [
        "Your innovative thinking solves a collective problem in an unexpected way.",
        "Uranus sparks brilliant ideas — capture every one of them today.",
        "Community and group efforts benefit from your visionary leadership.",
        "Your independence is your strength. Trust the unconventional path.",
        "Technology, science, or humanitarian work brings a meaningful breakthrough.",
    ],
    "Pisces": [
        "Your intuition and creativity flow at their peak. Art, music, or writing opens a channel.",
        "Neptune heightens your spiritual sensitivity — meditation and dreams carry messages.",
        "Compassion extended to others returns as grace. Be the kindness the world needs.",
        "Boundaries protect your sensitive energy today. Choose your environments carefully.",
        "A creative vision crystallizes. What you imagine, you can create.",
    ],
}


# ---------------------------------------------------------------------------
# Sun sign calculation
# ---------------------------------------------------------------------------

def get_sun_sign(birth_date: date) -> dict:
    """Return the zodiac sign for a given birth date."""
    m, d = birth_date.month, birth_date.day
    for sign in SIGNS:
        sm, sd = sign["start_month"], sign["start_day"]
        em, ed = sign["end_month"], sign["end_day"]
        if sm <= em:
            if (m == sm and d >= sd) or (m == em and d <= ed) or (sm < m < em):
                return sign
        else:
            # wraps year (Capricorn: Dec 22 – Jan 19)
            if (m == sm and d >= sd) or m > sm or m < em or (m == em and d <= ed):
                return sign
    return SIGNS[0]  # fallback


# ---------------------------------------------------------------------------
# Moon sign approximation
# ---------------------------------------------------------------------------

def get_moon_sign(birth_date: date) -> dict:
    """Approximate Moon sign based on birth date using a simplified cycle."""
    # Moon completes a full cycle every ~29.5 days
    # Use Julian day number mod 29.5 to find position
    ref_date = date(2000, 1, 1)  # Jan 1 2000 — Moon in Aries (approx)
    days_since = (birth_date - ref_date).days
    moon_cycle_position = days_since % 29.5306
    sign_index = int(moon_cycle_position / (29.5306 / 12)) % 12
    sign_name = MOON_SIGN_ORDER[sign_index]
    return SIGN_INDEX[sign_name]


# ---------------------------------------------------------------------------
# Rising sign approximation
# ---------------------------------------------------------------------------

def get_rising_sign(birth_date: date, birth_hour: int = 6, birth_minute: int = 0) -> dict:
    """Approximate Ascendant (Rising sign) from birth date and time."""
    # Rising sign changes every ~2 hours
    # Sun sign at noon is a reference point
    sun_sign = get_sun_sign(birth_date)
    sun_sign_index = next(i for i, s in enumerate(SIGNS) if s["name"] == sun_sign["name"])
    # Each 2 hours = 1 sign shift from the sun sign at noon
    birth_minutes_from_noon = (birth_hour - 6) * 60 + birth_minute
    sign_shifts = int(birth_minutes_from_noon / 120)
    rising_index = (sun_sign_index + sign_shifts) % 12
    return SIGNS[rising_index]


# ---------------------------------------------------------------------------
# Daily horoscope
# ---------------------------------------------------------------------------

def get_daily_horoscope(sign_name: str, for_date: Optional[date] = None) -> str:
    """Return a daily horoscope for the given sign."""
    if for_date is None:
        for_date = date.today()
    templates = HOROSCOPE_TEMPLATES.get(sign_name, ["The stars are quiet today. Reflect and rest."])
    day_of_year = for_date.timetuple().tm_yday
    idx = day_of_year % len(templates)
    return templates[idx]


# ---------------------------------------------------------------------------
# Reading builder
# ---------------------------------------------------------------------------

def build_astrology_reading(
    birth_date_str: str,
    birth_time_str: Optional[str] = None,
    user_id: str = "anonymous",
) -> dict:
    """Build a complete astrology reading."""
    bd = date.fromisoformat(birth_date_str)
    birth_hour = 6
    birth_minute = 0
    if birth_time_str:
        try:
            t = datetime.strptime(birth_time_str, "%H:%M").time()
            birth_hour = t.hour
            birth_minute = t.minute
        except ValueError:
            pass

    sun = get_sun_sign(bd)
    moon = get_moon_sign(bd)
    rising = get_rising_sign(bd, birth_hour, birth_minute)
    horoscope = get_daily_horoscope(sun["name"])

    return {
        "user_id": user_id,
        "birth_date": birth_date_str,
        "birth_time": birth_time_str,
        "sun_sign": sun,
        "moon_sign": moon,
        "rising_sign": rising,
        "daily_horoscope": horoscope,
        "natal_summary": (
            f"Sun in {sun['name']} ({sun['element']}, {sun['modality']}), "
            f"Moon in {moon['name']}, Rising in {rising['name']}. "
            f"Ruler: {sun['ruler']}. {sun['description']}"
        ),
    }


def get_sign_by_name(name: str) -> Optional[dict]:
    return SIGN_INDEX.get(name)


def list_all_signs() -> list[dict]:
    return SIGNS


# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, and synthesis: GitHub Copilot (AI).
