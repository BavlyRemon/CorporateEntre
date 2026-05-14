"""Pure-Python Porter (1980) stemmer.

Implements the classic five-step suffix-stripping algorithm described in
M.F. Porter (1980), "An algorithm for suffix stripping". Used by the
keyword counters so that, e.g., "innovate", "innovation", "innovating",
and "innovative" all reduce to the same stem.

No third-party deps; stdlib only.
"""

from __future__ import annotations


_VOWELS = "aeiou"


def _is_consonant(word: str, i: int) -> bool:
    ch = word[i]
    if ch in _VOWELS:
        return False
    if ch == "y":
        return True if i == 0 else not _is_consonant(word, i - 1)
    return True


def _measure(stem: str) -> int:
    """Porter's m: number of VC sequences in the stem."""
    n = len(stem)
    if n == 0:
        return 0
    seq = "".join("c" if _is_consonant(stem, i) else "v" for i in range(n))
    return seq.count("vc")


def _contains_vowel(stem: str) -> bool:
    return any(not _is_consonant(stem, i) for i in range(len(stem)))


def _ends_double_consonant(word: str) -> bool:
    if len(word) < 2:
        return False
    if word[-1] != word[-2]:
        return False
    return _is_consonant(word, len(word) - 1)


def _cvc(word: str) -> bool:
    """True if word ends with consonant-vowel-consonant where final isn't w/x/y."""
    if len(word) < 3:
        return False
    if not _is_consonant(word, len(word) - 1):
        return False
    if _is_consonant(word, len(word) - 2):
        return False
    if not _is_consonant(word, len(word) - 3):
        return False
    if word[-1] in "wxy":
        return False
    return True


def _replace_if(word: str, suffix: str, replacement: str, min_m: int) -> str | None:
    if word.endswith(suffix):
        stem = word[: len(word) - len(suffix)]
        if _measure(stem) > min_m:
            return stem + replacement
    return None


def _step1a(w: str) -> str:
    for suf, rep in (("sses", "ss"), ("ies", "i"), ("ss", "ss"), ("s", "")):
        if w.endswith(suf):
            return w[: len(w) - len(suf)] + rep
    return w


def _step1b(w: str) -> str:
    if w.endswith("eed"):
        stem = w[:-3]
        if _measure(stem) > 0:
            return stem + "ee"
        return w
    stripped = None
    if w.endswith("ed"):
        stem = w[:-2]
        if _contains_vowel(stem):
            stripped = stem
    elif w.endswith("ing"):
        stem = w[:-3]
        if _contains_vowel(stem):
            stripped = stem
    if stripped is None:
        return w
    w = stripped
    if w.endswith(("at", "bl", "iz")):
        return w + "e"
    if _ends_double_consonant(w) and not w.endswith(("l", "s", "z")):
        return w[:-1]
    if _measure(w) == 1 and _cvc(w):
        return w + "e"
    return w


def _step1c(w: str) -> str:
    if w.endswith("y") and len(w) > 1 and _contains_vowel(w[:-1]):
        return w[:-1] + "i"
    return w


_STEP2_PAIRS = [
    ("ational", "ate"), ("tional", "tion"), ("enci", "ence"), ("anci", "ance"),
    ("izer", "ize"), ("abli", "able"), ("alli", "al"), ("entli", "ent"),
    ("eli", "e"), ("ousli", "ous"), ("ization", "ize"), ("ation", "ate"),
    ("ator", "ate"), ("alism", "al"), ("iveness", "ive"), ("fulness", "ful"),
    ("ousness", "ous"), ("aliti", "al"), ("iviti", "ive"), ("biliti", "ble"),
]


def _step2(w: str) -> str:
    for suf, rep in _STEP2_PAIRS:
        out = _replace_if(w, suf, rep, 0)
        if out is not None:
            return out
    return w


_STEP3_PAIRS = [
    ("icate", "ic"), ("ative", ""), ("alize", "al"), ("iciti", "ic"),
    ("ical", "ic"), ("ful", ""), ("ness", ""),
]


def _step3(w: str) -> str:
    for suf, rep in _STEP3_PAIRS:
        out = _replace_if(w, suf, rep, 0)
        if out is not None:
            return out
    return w


_STEP4_SUFFIXES = [
    "al", "ance", "ence", "er", "ic", "able", "ible", "ant", "ement",
    "ment", "ent", "ou", "ism", "ate", "iti", "ous", "ive", "ize",
]


def _step4(w: str) -> str:
    if w.endswith("ion"):
        stem = w[:-3]
        if _measure(stem) > 1 and stem.endswith(("s", "t")):
            return stem
    for suf in _STEP4_SUFFIXES:
        if w.endswith(suf):
            stem = w[: len(w) - len(suf)]
            if _measure(stem) > 1:
                return stem
    return w


def _step5a(w: str) -> str:
    if w.endswith("e"):
        stem = w[:-1]
        m = _measure(stem)
        if m > 1:
            return stem
        if m == 1 and not _cvc(stem):
            return stem
    return w


def _step5b(w: str) -> str:
    if _measure(w) > 1 and _ends_double_consonant(w) and w.endswith("l"):
        return w[:-1]
    return w


def stem(word: str) -> str:
    """Return the Porter stem of `word` (lowercased, alphabetic input)."""
    if not word:
        return word
    w = word.lower()
    if len(w) <= 2:
        return w
    w = _step1a(w)
    w = _step1b(w)
    w = _step1c(w)
    w = _step2(w)
    w = _step3(w)
    w = _step4(w)
    w = _step5a(w)
    w = _step5b(w)
    return w


__all__ = ["stem"]
