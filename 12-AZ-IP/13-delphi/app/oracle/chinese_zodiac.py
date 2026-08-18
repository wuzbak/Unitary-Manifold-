"""
DelPhi — Chinese Zodiac Oracle Engine
12-animal cycle, five elements, yin/yang, compatibility.
"""
from __future__ import annotations

from typing import Optional

# ---------------------------------------------------------------------------
# Chinese Zodiac Data
# ---------------------------------------------------------------------------

# Element cycle: Wood(4,5), Fire(6,7), Earth(8,9), Metal(0,1), Water(2,3) per year-end digit
ELEMENT_BY_DIGIT: dict[int, str] = {
    0: "Metal", 1: "Metal",
    2: "Water", 3: "Water",
    4: "Wood", 5: "Wood",
    6: "Fire", 7: "Fire",
    8: "Earth", 9: "Earth",
}

# Animals in order (Rat=0, Ox=1, ..., Pig=11), starting from 1900 (Rat)
ANIMAL_ORDER = [
    "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake",
    "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"
]

# Trine groups (highly compatible)
TRINE_GROUPS: dict[str, list[str]] = {
    "First Trine": ["Rat", "Dragon", "Monkey"],
    "Second Trine": ["Ox", "Snake", "Rooster"],
    "Third Trine": ["Tiger", "Horse", "Dog"],
    "Fourth Trine": ["Rabbit", "Goat", "Pig"],
}

# Opposite (incompatible) pairs
OPPOSITE_PAIRS: dict[str, str] = {
    "Rat": "Horse", "Horse": "Rat",
    "Ox": "Goat", "Goat": "Ox",
    "Tiger": "Monkey", "Monkey": "Tiger",
    "Rabbit": "Rooster", "Rooster": "Rabbit",
    "Dragon": "Dog", "Dog": "Dragon",
    "Snake": "Pig", "Pig": "Snake",
}

ANIMALS: list[dict] = [
    {
        "animal": "Rat",
        "element_affinity": "Water",
        "yin_yang": "Yang",
        "trine_group": "First Trine",
        "compatible_with": ["Dragon", "Monkey", "Ox"],
        "incompatible_with": ["Horse", "Rooster"],
        "lucky_numbers": [2, 3],
        "lucky_colors": ["blue", "gold", "green"],
        "description": (
            "The Rat is the first sign of the Chinese zodiac — clever, resourceful, and charming. "
            "People born in the Year of the Rat are quick-witted problem-solvers who excel at accumulating "
            "resources and spotting opportunities others miss. Their adaptability and intelligence make them "
            "successful in almost any field. At their best they are thrifty, versatile, and sociable; "
            "at their shadow they can be manipulative, selfish, or overly cautious."
        ),
        "famous_years": [1912, 1924, 1936, 1948, 1960, 1972, 1984, 1996, 2008, 2020],
        "strengths": "Intelligent, adaptable, quick-witted, charming, artistic, sociable",
        "weaknesses": "Stubborn, overcritical, restless, ruthless, intolerant, scheming",
    },
    {
        "animal": "Ox",
        "element_affinity": "Earth",
        "yin_yang": "Yin",
        "trine_group": "Second Trine",
        "compatible_with": ["Snake", "Rooster", "Rat"],
        "incompatible_with": ["Goat", "Dragon", "Horse"],
        "lucky_numbers": [1, 4],
        "lucky_colors": ["blue", "yellow", "green"],
        "description": (
            "The Ox is the tireless worker of the Chinese zodiac — patient, dependable, and strong. "
            "Born in the Year of the Ox, these individuals achieve success through determination and hard work "
            "rather than luck or cleverness. They are reliable, methodical, and deeply trustworthy. "
            "Their persistence makes them natural leaders in fields requiring sustained effort."
        ),
        "famous_years": [1913, 1925, 1937, 1949, 1961, 1973, 1985, 1997, 2009, 2021],
        "strengths": "Hardworking, honest, creative, trustworthy, ambitious, patient",
        "weaknesses": "Stubborn, narrow-minded, slow-moving, judgmental",
    },
    {
        "animal": "Tiger",
        "element_affinity": "Wood",
        "yin_yang": "Yang",
        "trine_group": "Third Trine",
        "compatible_with": ["Horse", "Dog", "Pig"],
        "incompatible_with": ["Monkey", "Snake", "Ox"],
        "lucky_numbers": [1, 3, 4],
        "lucky_colors": ["blue", "grey", "orange"],
        "description": (
            "The Tiger is the bold adventurer of the Chinese zodiac — courageous, unpredictable, and magnetic. "
            "Those born in the Year of the Tiger are natural leaders who command attention wherever they go. "
            "They are fierce protectors of those they love and relentless pursuers of their goals. "
            "Their energy is infectious but can also be consuming."
        ),
        "famous_years": [1914, 1926, 1938, 1950, 1962, 1974, 1986, 1998, 2010, 2022],
        "strengths": "Brave, confident, charismatic, enthusiastic, ambitious, leadership",
        "weaknesses": "Arrogant, impulsive, stubborn, reckless",
    },
    {
        "animal": "Rabbit",
        "element_affinity": "Wood",
        "yin_yang": "Yin",
        "trine_group": "Fourth Trine",
        "compatible_with": ["Goat", "Pig", "Dog"],
        "incompatible_with": ["Rooster", "Dragon", "Rat"],
        "lucky_numbers": [3, 4, 6],
        "lucky_colors": ["red", "pink", "purple"],
        "description": (
            "The Rabbit is the gentle diplomat of the Chinese zodiac — gracious, kind, and deeply intuitive. "
            "Born in the Year of the Rabbit, these individuals are peace-loving souls who navigate conflict "
            "with exceptional grace. They are tasteful, artistic, and possess a quiet strength that others "
            "often underestimate. Their sensitivity is both a gift and a vulnerability."
        ),
        "famous_years": [1915, 1927, 1939, 1951, 1963, 1975, 1987, 1999, 2011, 2023],
        "strengths": "Compassionate, diplomatic, elegant, sincere, kind, cautious",
        "weaknesses": "Moody, detached, superficial, self-indulgent",
    },
    {
        "animal": "Dragon",
        "element_affinity": "Earth",
        "yin_yang": "Yang",
        "trine_group": "First Trine",
        "compatible_with": ["Rat", "Monkey", "Rooster"],
        "incompatible_with": ["Dog", "Rabbit", "Dragon"],
        "lucky_numbers": [1, 6, 7],
        "lucky_colors": ["gold", "silver", "grey"],
        "description": (
            "The Dragon is the most auspicious and powerful sign of the Chinese zodiac — vibrant, magnetic, "
            "and full of life force. Those born in the Year of the Dragon are natural born leaders who attract "
            "success and admiration. Fearless and ambitious, they pursue their visions with extraordinary energy. "
            "The Dragon represents imperial power, good fortune, and celestial authority."
        ),
        "famous_years": [1916, 1928, 1940, 1952, 1964, 1976, 1988, 2000, 2012, 2024],
        "strengths": "Confident, intelligent, enthusiastic, ambitious, decisive, charismatic",
        "weaknesses": "Arrogant, impatient, intolerant, ruthless",
    },
    {
        "animal": "Snake",
        "element_affinity": "Fire",
        "yin_yang": "Yin",
        "trine_group": "Second Trine",
        "compatible_with": ["Ox", "Rooster"],
        "incompatible_with": ["Tiger", "Pig"],
        "lucky_numbers": [2, 8, 9],
        "lucky_colors": ["black", "red", "yellow"],
        "description": (
            "The Snake is the wise philosopher of the Chinese zodiac — intuitive, elegant, and deeply perceptive. "
            "Born in the Year of the Snake, these individuals are natural strategists who move quietly toward "
            "their goals. They possess great inner wisdom and a refined aesthetic sense. "
            "The Snake's enigmatic nature conceals both great intelligence and profound depth of feeling."
        ),
        "famous_years": [1917, 1929, 1941, 1953, 1965, 1977, 1989, 2001, 2013, 2025],
        "strengths": "Intuitive, wise, elegant, philosophical, determined, graceful",
        "weaknesses": "Secretive, jealous, possessive, lazy",
    },
    {
        "animal": "Horse",
        "element_affinity": "Fire",
        "yin_yang": "Yang",
        "trine_group": "Third Trine",
        "compatible_with": ["Tiger", "Dog", "Goat"],
        "incompatible_with": ["Rat", "Ox"],
        "lucky_numbers": [2, 3, 7],
        "lucky_colors": ["yellow", "green"],
        "description": (
            "The Horse is the free spirit of the Chinese zodiac — energetic, adventurous, and passionate. "
            "Those born in the Year of the Horse are sociable and love to be on the move. "
            "They are talented, independent souls with an insatiable appetite for freedom and new experiences. "
            "Their enthusiasm and warmth draw people to them naturally."
        ),
        "famous_years": [1918, 1930, 1942, 1954, 1966, 1978, 1990, 2002, 2014, 2026],
        "strengths": "Animated, active, energetic, optimistic, passionate, cheerful",
        "weaknesses": "Impatient, hot-headed, reckless, gullible",
    },
    {
        "animal": "Goat",
        "element_affinity": "Earth",
        "yin_yang": "Yin",
        "trine_group": "Fourth Trine",
        "compatible_with": ["Rabbit", "Pig", "Horse"],
        "incompatible_with": ["Ox", "Dog"],
        "lucky_numbers": [2, 7],
        "lucky_colors": ["brown", "red", "purple"],
        "description": (
            "The Goat (or Sheep/Ram) is the artistic dreamer of the Chinese zodiac — gentle, creative, and deeply feeling. "
            "Born in the Year of the Goat, these individuals have rich inner lives and refined aesthetic sensibilities. "
            "They are compassionate, generous, and deeply empathic. "
            "Their creativity flourishes when they feel safe and loved."
        ),
        "famous_years": [1919, 1931, 1943, 1955, 1967, 1979, 1991, 2003, 2015, 2027],
        "strengths": "Creative, charming, gentle, intuitive, calm, understanding",
        "weaknesses": "Indecisive, shy, pessimistic, over-reliant",
    },
    {
        "animal": "Monkey",
        "element_affinity": "Metal",
        "yin_yang": "Yang",
        "trine_group": "First Trine",
        "compatible_with": ["Rat", "Dragon"],
        "incompatible_with": ["Tiger", "Pig"],
        "lucky_numbers": [1, 7, 8],
        "lucky_colors": ["white", "blue", "gold"],
        "description": (
            "The Monkey is the clever trickster of the Chinese zodiac — inventive, witty, and endlessly curious. "
            "Those born in the Year of the Monkey are quick learners who can master almost anything they apply themselves to. "
            "Their playful intelligence and adaptability make them natural problem-solvers and entertainers. "
            "They thrive on mental stimulation and change."
        ),
        "famous_years": [1920, 1932, 1944, 1956, 1968, 1980, 1992, 2004, 2016, 2028],
        "strengths": "Sharp, smart, curious, innovative, sociable, naughty",
        "weaknesses": "Tricky, selfish, jealous, suspicious, arrogant",
    },
    {
        "animal": "Rooster",
        "element_affinity": "Metal",
        "yin_yang": "Yin",
        "trine_group": "Second Trine",
        "compatible_with": ["Ox", "Snake", "Dragon"],
        "incompatible_with": ["Rabbit", "Rooster", "Dog"],
        "lucky_numbers": [5, 7, 8],
        "lucky_colors": ["gold", "brown", "yellow"],
        "description": (
            "The Rooster is the meticulous perfectionist of the Chinese zodiac — observant, hardworking, and courageous. "
            "Born in the Year of the Rooster, these individuals are punctual, reliable, and highly detail-oriented. "
            "They take great pride in their appearance and their work. "
            "The Rooster's crow awakens others to truth and opportunity."
        ),
        "famous_years": [1921, 1933, 1945, 1957, 1969, 1981, 1993, 2005, 2017, 2029],
        "strengths": "Observant, hardworking, courageous, confident, humorous",
        "weaknesses": "Critical, selfish, vain, overconfident",
    },
    {
        "animal": "Dog",
        "element_affinity": "Earth",
        "yin_yang": "Yang",
        "trine_group": "Third Trine",
        "compatible_with": ["Tiger", "Horse", "Rabbit"],
        "incompatible_with": ["Dragon", "Goat", "Rooster"],
        "lucky_numbers": [3, 4, 9],
        "lucky_colors": ["green", "red", "purple"],
        "description": (
            "The Dog is the loyal protector of the Chinese zodiac — honest, faithful, and deeply just. "
            "Those born in the Year of the Dog are the most loyal of all the animals. "
            "They are courageous defenders of those they love and relentless advocates for fairness. "
            "The Dog's straightforward nature and deep empathy make them beloved friends and trusted allies."
        ),
        "famous_years": [1922, 1934, 1946, 1958, 1970, 1982, 1994, 2006, 2018, 2030],
        "strengths": "Loyal, honest, kind, cautious, smart, responsible",
        "weaknesses": "Anxious, stubborn, judgmental, cynical",
    },
    {
        "animal": "Pig",
        "element_affinity": "Water",
        "yin_yang": "Yin",
        "trine_group": "Fourth Trine",
        "compatible_with": ["Tiger", "Rabbit", "Goat"],
        "incompatible_with": ["Snake", "Monkey"],
        "lucky_numbers": [2, 5, 8],
        "lucky_colors": ["yellow", "grey", "brown"],
        "description": (
            "The Pig is the generous soul of the Chinese zodiac — compassionate, diligent, and pure of heart. "
            "Born in the Year of the Pig, these individuals are known for their sincerity, warmth, and remarkable "
            "generosity. They work hard and play hard, finding joy in life's pleasures. "
            "The Pig's innocence and good nature attract abundance and love."
        ),
        "famous_years": [1923, 1935, 1947, 1959, 1971, 1983, 1995, 2007, 2019, 2031],
        "strengths": "Compassionate, generous, diligent, faithful, funny, sincere",
        "weaknesses": "Naive, over-reliant, self-indulgent, gullible",
    },
]

ANIMAL_INDEX: dict[str, dict] = {a["animal"]: a for a in ANIMALS}

# Five Element Cycle
GENERATING_CYCLE = ["Wood", "Fire", "Earth", "Metal", "Water"]  # Wood feeds Fire, etc.
CONTROLLING_CYCLE = ["Wood", "Earth", "Water", "Fire", "Metal"]  # Wood controls Earth, etc.


def get_element_cycle() -> dict[str, dict[str, str]]:
    """Return the five-element generating and controlling relationships."""
    result = {}
    for i, el in enumerate(GENERATING_CYCLE):
        generates = GENERATING_CYCLE[(i + 1) % 5]
        controls = CONTROLLING_CYCLE[(i + 1) % 5]
        result[el] = {"generates": generates, "controls": controls}
    return result


# ---------------------------------------------------------------------------
# Calculation functions
# ---------------------------------------------------------------------------

def get_animal(year: int) -> dict:
    """Return the Chinese zodiac animal for a given birth year."""
    # The 12-year cycle starts from 1900 (Rat year)
    idx = (year - 1900) % 12
    return ANIMALS[idx]


def get_element(year: int) -> str:
    """Return the five-element for a given year."""
    last_digit = year % 10
    return ELEMENT_BY_DIGIT[last_digit]


def get_yin_yang(year: int) -> str:
    """Return yin or yang based on year (even=Yang, odd=Yin in traditional system)."""
    return "Yang" if year % 2 == 0 else "Yin"


def get_compatibility(animal1: str, animal2: str) -> dict:
    """Return compatibility information between two animals."""
    a1 = ANIMAL_INDEX.get(animal1)
    a2 = ANIMAL_INDEX.get(animal2)
    if not a1 or not a2:
        return {"score": "unknown", "description": "Animal not found"}

    # Check trine (best)
    for trine_name, members in TRINE_GROUPS.items():
        if animal1 in members and animal2 in members:
            return {
                "score": "excellent",
                "trine": trine_name,
                "description": f"{animal1} and {animal2} share the {trine_name} — a natural harmony and deep understanding.",
            }

    # Check if in compatible list
    if animal2 in a1.get("compatible_with", []):
        return {
            "score": "good",
            "description": f"{animal1} and {animal2} have good compatibility — complementary strengths.",
        }

    # Check opposites
    if OPPOSITE_PAIRS.get(animal1) == animal2:
        return {
            "score": "challenging",
            "description": f"{animal1} and {animal2} are opposites — significant tension, but transformative potential.",
        }

    # Check incompatible
    if animal2 in a1.get("incompatible_with", []):
        return {
            "score": "difficult",
            "description": f"{animal1} and {animal2} have notable friction — patience and effort required.",
        }

    return {
        "score": "neutral",
        "description": f"{animal1} and {animal2} have a neutral relationship — context determines the outcome.",
    }


def build_chinese_zodiac_reading(birth_year: int, user_id: str = "anonymous") -> dict:
    """Build a complete Chinese zodiac reading."""
    animal_data = get_animal(birth_year)
    element = get_element(birth_year)
    yin_yang = get_yin_yang(birth_year)
    element_cycle = get_element_cycle()

    return {
        "user_id": user_id,
        "birth_year": birth_year,
        "animal": animal_data["animal"],
        "element": element,
        "yin_yang": yin_yang,
        "trine_group": animal_data["trine_group"],
        "compatible_with": animal_data["compatible_with"],
        "incompatible_with": animal_data["incompatible_with"],
        "description": animal_data["description"],
        "strengths": animal_data["strengths"],
        "weaknesses": animal_data["weaknesses"],
        "lucky_numbers": animal_data["lucky_numbers"],
        "lucky_colors": animal_data["lucky_colors"],
        "element_cycle": element_cycle,
        "summary": (
            f"{birth_year} is the Year of the {animal_data['animal']} "
            f"({yin_yang} {element} {animal_data['animal']}). "
            f"Trine: {animal_data['trine_group']}. "
            f"Most compatible with: {', '.join(animal_data['compatible_with'])}."
        ),
    }


def get_animal_by_name(name: str) -> Optional[dict]:
    return ANIMAL_INDEX.get(name)


def list_all_animals() -> list[dict]:
    return ANIMALS


# Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
# Code architecture, test suites, and synthesis: GitHub Copilot (AI).
