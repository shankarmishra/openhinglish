"""
Script to append new lexicon entries to roman_hindi.tsv, english_freq.tsv, and english_tts.tsv.
Only adds entries not already present.
"""

import os

# ── paths ────────────────────────────────────────────────────────────────────
BASE = r"C:\Users\shankar mishra\openhinglish\src\openhinglish\data\lexicons"
ROMAN_HINDI = os.path.join(BASE, "roman_hindi.tsv")
ENG_FREQ    = os.path.join(BASE, "english_freq.tsv")
ENG_TTS     = os.path.join(BASE, "english_tts.tsv")


def existing_keys(path, key_col=0):
    keys = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) > key_col and parts[key_col].strip():
                keys.add(parts[key_col].strip())
    return keys


def append_rows(path, rows):
    """Append tab-separated rows (tuples) to file, one per line."""
    with open(path, "a", encoding="utf-8", newline="") as f:
        for row in rows:
            f.write("\t".join(str(c) for c in row) + "\n")


# ── B. roman_hindi.tsv entries ───────────────────────────────────────────────
# Format: roman \t devanagari \t freq
ROMAN_HINDI_NEW = [
    # Pronouns / possessives
    ("aapka",    "आपका",    6000),
    ("mujhe",    "मुझे",    8000),
    ("tujhe",    "तुझे",    6000),
    ("use",      "उसे",     7000),
    ("hume",     "हमें",    6000),
    ("humein",   "हमें",    6000),
    ("unhein",   "उन्हें",  5000),
    ("mere",     "मेरे",    7500),
    ("tera",     "तेरा",    6000),
    ("teri",     "तेरी",    5500),
    ("tere",     "तेरे",    5500),
    ("tumhari",  "तुम्हारी", 4500),
    ("iska",     "इसका",    5000),
    ("iski",     "इसकी",    4500),
    ("khud",     "ख़ुद",    5500),

    # Verbs – kar family
    ("karta",    "करता",    7000),
    ("karni",    "करनी",    5500),
    ("karne",    "करने",    6500),
    ("karega",   "करेगा",   6500),
    ("karegi",   "करेगी",   6000),
    ("karenge",  "करेंगे",  6000),
    ("karunga",  "करूँगा",  5000),
    ("karungi",  "करूँगी",  4500),
    ("karke",    "करके",    6500),
    ("kiye",     "किये",    6000),

    # Verb – khana/khao family
    ("khana",    "खाना",    7000),
    ("khaya",    "खाया",    6000),
    ("kharab",   "ख़राब",   6000),

    # Verb – lena family
    ("lene",     "लेने",    6000),
    ("liya",     "लिया",    6500),
    ("liye",     "लिये",    6000),
    ("leta",     "लेता",    5500),

    # Verb – milna family
    ("milkar",   "मिलकर",   4500),
    ("mile",     "मिले",    5500),
    ("milega",   "मिलेगा",  5000),

    # Verb – bhejna family
    ("bhejo",    "भेजो",    4500),
    ("bhejna",   "भेजना",   4500),
    ("bheja",    "भेजा",    4500),

    # Verb – bolna family
    ("bola",     "बोला",    6000),
    ("boli",     "बोली",    5500),
    ("bole",     "बोले",    5500),
    ("bolna",    "बोलना",   5500),

    # Verb – dekhna family
    ("dekhe",    "देखे",    5500),
    ("dekha",    "देखा",    6000),
    ("dekhna",   "देखना",   5500),
    ("dekhne",   "देखने",   5500),

    # Verb – jaana future tense
    ("jaunga",   "जाऊँगा",  4500),
    ("jaungi",   "जाऊँगी",  4000),
    ("jayega",   "जाएगा",   6000),
    ("jayegi",   "जाएगी",   5500),
    ("jayenge",  "जाएँगे",  5500),
    ("jana",     "जाना",    6500),

    # Verb – aana family (missing forms)
    ("aaye",     "आये",     5500),
    ("aata",     "आता",     6000),
    ("aati",     "आती",     5500),
    ("aate",     "आते",     5500),

    # Verb – dena family
    ("diya",     "दिया",    7000),
    ("diye",     "दिये",    6000),
    ("do",       "दो",      6500),
    ("deta",     "देता",    5500),
    ("dete",     "देते",    5500),

    # Verb – hona family
    ("hona",     "होना",    6500),
    ("hota",     "होता",    6500),
    ("hoti",     "होती",    6000),
    ("hote",     "होते",    6000),
    ("honge",    "होंगे",   5500),

    # Verb – rahna future
    ("rahega",   "रहेगा",   5500),

    # Verb – sunna family
    ("suna",     "सुना",    5500),
    ("sunna",    "सुनना",   5000),

    # Misc verbs
    ("ho",       "हो",      8000),
    ("ja",       "जा",      6000),
    ("jaa",      "जा",      5500),
    ("kaha",     "कहा",     6500),
    ("baje",     "बजे",     5000),

    # Nouns / adjectives
    ("tabiyat",  "तबियत",   4500),

    # Modal verbs
    ("lagta",    "लगता",    6000),
    ("lagti",    "लगती",    5500),
    ("lagi",     "लगी",     5500),
    ("laga",     "लगा",     6000),

    # Particles / function words
    ("mat",      "मत",      7000),
    ("sath",     "साथ",     6500),
    ("paas",     "पास",     6000),
    ("door",     "दूर",     5500),
    ("jaldi",    "जल्दी",   6500),
    ("der",      "देर",     5500),
    ("waapas",   "वापस",    5500),
    ("fir",      "फिर",     6000),
    ("taki",     "ताकि",    5000),
    ("tab",      "तब",      6500),
    ("agar",     "अगर",     6500),
]

# ── C. english_freq.tsv & english_tts.tsv entries ───────────────────────────
# Format freq: word \t freq
# Format tts:  word \t devanagari_pron
ENGLISH_NEW = [
    # word, freq, devanagari_pron
    ("attend",    5500, "अटेंड"),
    ("please",    7000, "प्लीज़"),
    ("receive",   4500, "रिसीव"),
    ("customer",  6000, "कस्टमर"),
    ("care",      5500, "केयर"),
    ("request",   5500, "रिक्वेस्ट"),
    ("complete",  5000, "कम्प्लीट"),
    ("submit",    5000, "सबमिट"),
    ("register",  4500, "रजिस्टर"),
    ("schedule",  4500, "शेड्यूल"),
    ("available", 6000, "अवेलेबल"),
    ("important", 6500, "इम्पॉर्टेंट"),
    ("urgent",    5500, "अर्जेंट"),
    ("ready",     6500, "रेडी"),
    ("busy",      6000, "बिज़ी"),
    ("free",      6000, "फ्री"),
    ("sure",      6500, "श्योर"),
    ("detail",    5000, "डिटेल"),
    ("screenshot",4500, "स्क्रीनशॉट"),
    ("status",    6000, "स्टेटस"),
    ("approve",   4500, "अप्रूव"),
    ("reject",    4500, "रिजेक्ट"),
]


def main():
    # ── B: roman_hindi.tsv ──────────────────────────────────────────────────
    rh_existing = existing_keys(ROMAN_HINDI, key_col=0)
    rh_to_add = [row for row in ROMAN_HINDI_NEW if row[0] not in rh_existing]
    append_rows(ROMAN_HINDI, rh_to_add)
    print(f"roman_hindi.tsv: added {len(rh_to_add)} rows (skipped {len(ROMAN_HINDI_NEW) - len(rh_to_add)} already-present)")

    # ── C: english_freq.tsv ─────────────────────────────────────────────────
    ef_existing = existing_keys(ENG_FREQ, key_col=0)
    ef_to_add = [(w, f) for w, f, _ in ENGLISH_NEW if w not in ef_existing]
    append_rows(ENG_FREQ, ef_to_add)
    print(f"english_freq.tsv: added {len(ef_to_add)} rows")

    # ── C: english_tts.tsv ──────────────────────────────────────────────────
    et_existing = existing_keys(ENG_TTS, key_col=0)
    et_to_add = [(w, p) for w, _, p in ENGLISH_NEW if w not in et_existing]
    append_rows(ENG_TTS, et_to_add)
    print(f"english_tts.tsv: added {len(et_to_add)} rows")


if __name__ == "__main__":
    main()
