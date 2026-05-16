"""Shared keyword dictionaries and stem-aware matcher.

A dictionary entry is one of:

  - a `str`: a literal phrase (whole-word, case-insensitive; hyphens and spaces
    treated as interchangeable). Use this for multi-word phrases or for tokens
    containing non-alphabetic characters (e.g. "R&D", "day 1", "AI").

  - a `dict` with keys:
      base     (str)   canonical surface form; Porter stem(base) is accepted
      aliases  (list)  optional extra surface forms whose stems should also
                        be accepted (handy when Porter under-/over-shoots,
                        e.g. base="discover" + aliases=["discovery"])
      excludes (list)  optional surface forms that must NOT count, even if
                        their stem would otherwise match (e.g. base="execute"
                        + excludes=["executive","executives"])

Counting:
  - Single-word stem entries: count any text token whose Porter stem matches
    the entry's accepted-stem set, minus surface forms in `excludes`.
  - Literal phrase entries: count whole-word/whole-phrase regex hits.
  - All matching is case-insensitive.

Each category counts entries independently; the same token can be counted
in multiple categories (categories are deliberately overlapping lenses).
"""

from __future__ import annotations

import re
from functools import lru_cache

from stemmer import stem


WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']*")


@lru_cache(maxsize=None)
def _stem(word: str) -> str:
    return stem(re.sub(r"[^a-z]", "", word.lower()))


def _literal_pattern(term: str) -> re.Pattern[str]:
    # Split the phrase on spaces/hyphens, escape each token, then rejoin with
    # a "[\s-]+" separator so "AI factory" also matches "AI-factory".
    # NB: do NOT do this with chained str.replace — escaping a space to "\ "
    # and then replacing "\-" corrupts the just-inserted "[\s\-]+" group.
    parts = [p for p in re.split(r"[\s\-]+", term.strip()) if p]
    body = r"[\s\-]+".join(re.escape(p) for p in parts)
    return re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", re.IGNORECASE)


def _is_literal_only(term: str) -> bool:
    """A bare word with no spaces/hyphens/punctuation can be stemmed."""
    s = term.strip()
    return not re.fullmatch(r"[A-Za-z]+", s)


def _entry_to_matcher(entry):
    """Return (kind, payload) where kind is 'literal' or 'stem'."""
    if isinstance(entry, str):
        return ("literal", _literal_pattern(entry))
    base = entry["base"]
    aliases = entry.get("aliases", []) or []
    excludes = entry.get("excludes", []) or []
    # If the base itself contains spaces/hyphens/non-alpha, fall back to literal.
    if _is_literal_only(base):
        return ("literal", _literal_pattern(base))
    # Allow opting out of stem matching for terms whose Porter stem collides
    # with semantically different words (e.g. "values" vs "value").
    if entry.get("stem") is False:
        forms = [base] + [a for a in aliases if not _is_literal_only(a)]
        accepted_surfaces = {a.lower() for a in forms}
        excluded = {a.lower() for a in excludes}
        return ("surface", (accepted_surfaces, excluded))
    accepted = {_stem(base)}
    for a in aliases:
        if _is_literal_only(a):
            continue
        accepted.add(_stem(a))
    excluded = {a.lower() for a in excludes}
    return ("stem", (accepted, excluded))


class Matcher:
    """Pre-compiled matcher for a single named category."""

    def __init__(self, name: str, terms: list):
        self.name = name
        self.literals: list[re.Pattern[str]] = []
        self.stem_entries: list[tuple[set, set]] = []
        self.surface_entries: list[tuple[set, set]] = []
        for term in terms:
            kind, payload = _entry_to_matcher(term)
            if kind == "literal":
                self.literals.append(payload)
            elif kind == "surface":
                self.surface_entries.append(payload)
            else:
                self.stem_entries.append(payload)

    def count(self, text: str, tokens: list[str] | None = None,
              token_stems: list[str] | None = None) -> int:
        total = sum(len(p.findall(text)) for p in self.literals)
        if self.stem_entries or self.surface_entries:
            if tokens is None:
                tokens = [m.group(0).lower() for m in WORD_RE.finditer(text)]
            if token_stems is None and self.stem_entries:
                token_stems = [_stem(t) for t in tokens]
            for accepted, excluded in self.surface_entries:
                for surface in tokens:
                    if surface in accepted and surface not in excluded:
                        total += 1
            for accepted, excluded in self.stem_entries:
                for surface, s in zip(tokens, token_stems):
                    if s in accepted and surface not in excluded:
                        total += 1
        return total


def build_matchers(category_dict: dict[str, list]) -> dict[str, Matcher]:
    return {name: Matcher(name, terms) for name, terms in category_dict.items()}


def tokenize(text: str) -> tuple[list[str], list[str]]:
    """Return (lowercased word tokens, their Porter stems) for `text`."""
    tokens = [m.group(0).lower() for m in WORD_RE.finditer(text)]
    return tokens, [_stem(t) for t in tokens]


# ---------------------------------------------------------------------------
# IPM (Innovation Process Model) categories
# ---------------------------------------------------------------------------

IPM_TERMS: dict[str, list] = {
    "Strategic Leadership": [
        {"base": "founder", "aliases": ["founders", "founding", "founded"], "excludes": ["found"]},
        {"base": "ownership"},
        {"base": "owner", "aliases": ["owners"]},
        {"base": "entrepreneurial", "aliases": ["entrepreneur", "entrepreneurs", "entrepreneurship"]},
        "day 1",
        "day one",
        {"base": "stewardship", "aliases": ["steward", "stewards"]},
        {"base": "ambidextrous", "aliases": ["ambidexterity"]},
        {"base": "paradox", "aliases": ["paradoxes", "paradoxical"]},
        "trade-off",
        "tradeoff",
        "dual mandate",
        {"base": "conviction", "aliases": ["convictions"]},
        {"base": "disciplined", "aliases": ["discipline", "disciplines"]},
        "high standards",
        "capital discipline",
        {"base": "decisive", "aliases": ["decisiveness", "decisively"], "excludes": ["decision", "decisions"]},
        {"base": "accountable", "aliases": ["accountability"], "excludes": ["account", "accounts", "accounting"]},
        {"base": "integrity", "stem": False},
        {"base": "bold", "aliases": ["boldly", "boldness"]},
        "risk-taking",
        "long-term owner",
    ],
    "Horizon Scanning / Sense-making": [
        {"base": "disrupt", "aliases": ["disruption", "disruptive", "disruptions", "disruptor", "disruptors"]},
        {"base": "uncertain", "aliases": ["uncertainty", "uncertainties"]},
        {"base": "volatile", "aliases": ["volatility", "volatilities"]},
        {"base": "turbulent", "aliases": ["turbulence"]},
        {"base": "crisis", "aliases": ["crises"]},
        {"base": "shock", "aliases": ["shocks", "shocked"]},
        "long-term",
        "long term",
        "next wave",
        # General future-orientation / sense-making vocabulary (industry-neutral).
        # Added 2026-05-16: the theme was skewed to energy/hardware terms and
        # under-counted tech firms that talk about the future in plain language.
        {"base": "future", "aliases": ["futures"]},
        {"base": "decade", "aliases": ["decades"]},
        {"base": "tomorrow"},
        {"base": "trend", "aliases": ["trends", "trending"]},
        {"base": "technology", "aliases": ["technologies", "technological", "technologically"]},
        {"base": "digital", "aliases": ["digitally", "digitize", "digitized", "digitization", "digitalization"]},
        {"base": "internet"},
        {"base": "cloud", "aliases": ["clouds"]},
        {"base": "data-driven"},
        {"base": "evolve", "aliases": ["evolves", "evolved", "evolving", "evolution"]},
        {"base": "transform", "aliases": ["transforms", "transformed", "transforming", "transformation", "transformations", "transformative"]},
        {"base": "shift", "aliases": ["shifts", "shifting", "shifted"]},
        {"base": "inflection"},
        {"base": "anticipate", "aliases": ["anticipates", "anticipated", "anticipating", "anticipation"]},
        {"base": "explore", "aliases": ["exploration", "exploring", "explored", "exploratory"]},
        {"base": "discover", "aliases": ["discovery", "discoveries", "discovered", "discovering"]},
        {"base": "experiment", "aliases": ["experimentation", "experimental", "experiments", "experimented", "experimenting"], "excludes": ["experience", "experiences", "experienced", "experiencing"]},
        {"base": "pilot", "aliases": ["pilots", "piloted", "piloting"]},
        "artificial intelligence",
        "AI",
        "generative AI",
        "generative artificial intelligence",
        "gen AI",
        "machine learning",
        "deep learning",
        "neural network",
        "neural networks",
        "large language model",
        "large language models",
        "LLM",
        "LLMs",
        "foundation model",
        "foundation models",
        "artificial general intelligence",
        "AGI",
        "AI factory",
        "AI factories",
        "AI infrastructure",
        "GPU",
        "accelerated computing",
        {"base": "automate", "aliases": ["automation", "automated", "automating", "automatic"]},
        {"base": "electrify", "aliases": ["electrification", "electric", "electrified", "electrifying"]},
        "energy transition",
        {"base": "decarbonize", "aliases": ["decarbonization", "decarbonized", "decarbonizing"]},
        {"base": "regulate", "aliases": ["regulation", "regulatory", "regulator", "regulators", "regulations", "regulated", "regulating"]},
        {"base": "policy", "aliases": ["policies"]},
        {"base": "geopolitical", "aliases": ["geopolitics"]},
        "commodity cycle",
        "energy security",
        "export controls",
    ],
    "Purpose, Vision, and Governance": [
        "customer obsession",
        "customer experience",
        {"base": "customer", "aliases": ["customers"], "excludes": ["custom", "customize", "customized", "customizing", "customizes"]},
        {"base": "client", "aliases": ["clients"]},
        {"base": "user", "aliases": ["users"]},
        {"base": "shareholder", "aliases": ["shareholders"]},
        {"base": "stockholder", "aliases": ["stockholders"]},
        {"base": "dividend", "aliases": ["dividends"]},
        "share repurchase",
        {"base": "buyback", "aliases": ["buybacks"]},
        "total shareholder return",
        "cash return",
        "category leadership",
        "market leadership",
        "competitive advantage",
        {"base": "ecosystem", "aliases": ["ecosystems"]},
        "scale advantage",
        {"base": "mission", "aliases": ["missions"]},
        {"base": "purpose", "aliases": ["purposes", "purposeful"]},
        {"base": "values", "stem": False},
        {"base": "identity", "aliases": ["identities"]},
        "human progress",
        "energy progress",
        "day 1",
        "day one",
        {"base": "govern", "aliases": ["governance", "governing", "governed"], "excludes": ["government", "governments", "governmental"]},
        "board oversight",
        {"base": "ethic", "aliases": ["ethics", "ethical", "ethically"]},
        "lower carbon",
        "climate oversight",
    ],
    "Strategic Options, Experimentation, and Choices": [
        {"base": "invent", "aliases": ["invention", "inventions", "inventing", "invented", "inventive", "inventor", "inventors"], "excludes": ["inventory", "inventories"]},
        "research and development",
        "R&D",
        {"base": "engineer", "aliases": ["engineering", "engineered", "engineers"], "excludes": ["engine", "engines"]},
        "technology development",
        {"base": "innovate", "aliases": ["innovation", "innovative", "innovations", "innovating", "innovator", "innovators", "innovated"]},
        {"base": "partner", "aliases": ["partners", "partnership", "partnerships", "partnered", "partnering"]},
        {"base": "alliance", "aliases": ["alliances"]},
        {"base": "collaborate", "aliases": ["collaboration", "collaborations", "collaborative", "collaborating", "collaborated", "collaborator", "collaborators"]},
        "joint venture",
        {"base": "ecosystem", "aliases": ["ecosystems"]},
        "developer ecosystem",
        "supplier partnership",
        {"base": "acquire", "aliases": ["acquisition", "acquisitions", "acquired", "acquiring", "acquires"]},
        {"base": "merger", "aliases": ["mergers", "merge", "merged", "merging"]},
        {"base": "integrate", "aliases": ["integration", "integrated", "integrating", "integrations"], "excludes": ["integrity", "integral"]},
        {"base": "divest", "aliases": ["divestment", "divestments", "divested", "divesting", "divestiture", "divestitures"]},
        "portfolio optimization",
        {"base": "experiment", "aliases": ["experimentation", "experiments", "experimented", "experimenting", "experimental"]},
        {"base": "pilot", "aliases": ["pilots", "piloted", "piloting"]},
        {"base": "prototype", "aliases": ["prototypes", "prototyping", "prototyped"]},
        "test-and-learn",
        {"base": "iterate", "aliases": ["iteration", "iterations", "iterating", "iterative", "iterated"]},
        "strategic option",
        "investment option",
        "selective bet",
        "capital allocation",
        {"base": "prioritize", "aliases": ["prioritization", "prioritized", "prioritizing", "prioritizes"]},
        {"base": "commercialize", "aliases": ["commercialization", "commercialized", "commercializing"], "excludes": ["commercial", "commercially", "commercials"]},
        {"base": "deploy", "aliases": ["deployment", "deployments", "deployed", "deploying", "deploys"]},
        "phase out",
        {"base": "exit", "aliases": ["exits", "exited", "exiting"]},
    ],
    "Agile Execution and Organization": [
        {"base": "agile", "aliases": ["agility"]},
        "high-velocity",
        "rapid execution",
        {"base": "accelerate", "aliases": ["accelerated", "accelerating", "acceleration", "accelerator", "accelerators", "accelerates"]},
        {"base": "adapt", "aliases": ["adaptable", "adaptation", "adapting", "adapted", "adaptive", "adaptability", "adapts"]},
        {"base": "pivot", "aliases": ["pivots", "pivoted", "pivoting"]},
        {"base": "flexible", "aliases": ["flexibility", "flexibly"]},
        "operational excellence",
        {"base": "efficient", "aliases": ["efficiency", "efficiently", "efficiencies"]},
        {"base": "productive", "aliases": ["productivity", "productively"], "excludes": ["product", "products", "production", "productions"]},
        {"base": "reliable", "aliases": ["reliability", "reliably"]},
        "process safety",
        "execution discipline",
        {"base": "talent", "aliases": ["talents", "talented"]},
        "capability building",
        "workforce capability",
        {"base": "culture", "aliases": ["cultures", "cultural", "culturally"]},
        {"base": "deploy", "aliases": ["deployment", "deployments", "deployed", "deploying"]},
        {"base": "implement", "aliases": ["implementation", "implementations", "implementing", "implemented", "implements"]},
        "infrastructure buildout",
        "capacity expansion",
        "ramp-up",
        {"base": "speed", "aliases": ["speeds", "speeding"]},
        {"base": "fast", "aliases": ["faster", "fastest"]},
        {"base": "rapid", "aliases": ["rapidly"], "excludes": ["rapids"]},
    ],
}


# ---------------------------------------------------------------------------
# Cross-cutting paired categories
# ---------------------------------------------------------------------------

CROSS_TERMS: dict[str, list] = {
    "explore": [
        {"base": "explore", "aliases": ["exploration", "exploring", "explored", "exploratory", "explorer", "explorers", "explores"]},
        {"base": "experiment", "aliases": ["experimentation", "experimental", "experiments", "experimented", "experimenting"], "excludes": ["experience", "experiences", "experienced", "experiencing"]},
        {"base": "discover", "aliases": ["discovery", "discoveries", "discovered", "discovering"]},
        {"base": "pilot", "aliases": ["pilots", "piloted", "piloting"]},
        "new business",
        {"base": "emerge", "aliases": ["emerging", "emerged", "emerges", "emergent"]},
        {"base": "option", "aliases": ["options", "optional", "optionality"]},
        {"base": "invent", "aliases": ["invention", "inventions", "inventing", "invented", "inventive", "inventor", "inventors"], "excludes": ["inventory", "inventories"]},
        {"base": "innovate", "aliases": ["innovation", "innovative", "innovations", "innovating", "innovator", "innovators", "innovated"]},
        "R&D",
        {"base": "research", "aliases": ["researcher", "researchers", "researching", "researched"]},
        {"base": "prototype", "aliases": ["prototypes", "prototyping", "prototyped"]},
        {"base": "iterate", "aliases": ["iteration", "iterations", "iterating", "iterative", "iterated"]},
        {"base": "learn", "aliases": ["learning", "learned", "learner", "learners", "learns"]},
        {"base": "pioneer", "aliases": ["pioneers", "pioneered", "pioneering"]},
        {"base": "reinvent", "aliases": ["reinvention", "reinvented", "reinventing", "reinvents"]},
        {"base": "disrupt", "aliases": ["disruption", "disruptions", "disruptive", "disruptor", "disruptors", "disrupted", "disrupting"]},
        {"base": "revolutionize", "aliases": ["revolution", "revolutionary", "revolutions", "revolutionized", "revolutionizing"]},
    ],
    "exploit": [
        "operational excellence",
        "cash generation",
        "capital discipline",
        {"base": "return", "aliases": ["returns", "returning", "returned"]},
        {"base": "efficient", "aliases": ["efficiency", "efficiencies", "efficiently"]},
        {"base": "productive", "aliases": ["productivity", "productively"], "excludes": ["product", "products", "production", "productions"]},
        {"base": "reliable", "aliases": ["reliability", "reliably"]},
        "cash flow",
        {"base": "dividend", "aliases": ["dividends"]},
        {"base": "buyback", "aliases": ["buybacks"]},
        "record production",
        {"base": "cost", "aliases": ["costs", "costing"], "excludes": ["costume", "costumes"]},
        {"base": "margin", "aliases": ["margins"]},
        {"base": "safety"},
        {"base": "execute", "aliases": ["execution", "executions", "executed", "executing", "executes"], "excludes": ["executive", "executives"]},
        {"base": "scale", "aliases": ["scales", "scaled", "scaling"]},
    ],
    "customer": [
        "customer obsession",
        "customer experience",
        {"base": "customer", "aliases": ["customers"], "excludes": ["custom", "customize", "customized", "customizing", "customizes"]},
        {"base": "client", "aliases": ["clients"]},
        {"base": "user", "aliases": ["users"]},
        {"base": "consumer", "aliases": ["consumers"], "excludes": ["consume", "consumed", "consuming", "consumables", "consumes", "consumption"]},
    ],
    "shareholder": [
        {"base": "shareholder", "aliases": ["shareholders"]},
        {"base": "stockholder", "aliases": ["stockholders"]},
        {"base": "dividend", "aliases": ["dividends"]},
        {"base": "buyback", "aliases": ["buybacks"]},
        "share repurchase",
        "cash return",
        "total shareholder return",
    ],
    "long_term": [
        "long-term",
        "long term",
        {"base": "decade", "aliases": ["decades"]},
        {"base": "future", "aliases": ["futures"]},
        "next generation",
        "multi-year",
        "years ahead",
    ],
    "short_term": [
        "short-term",
        "short term",
        "near-term",
        "near term",
        {"base": "quarter", "aliases": ["quarters", "quarterly"]},
        {"base": "immediate", "aliases": ["immediately"]},
        {"base": "temporary", "aliases": ["temporarily"]},
    ],
    "entrepreneurial": [
        {"base": "entrepreneurial", "aliases": ["entrepreneur", "entrepreneurs", "entrepreneurship"]},
        {"base": "founder", "aliases": ["founders", "founded", "founding"], "excludes": ["found"]},
        "day 1",
        "day one",
        {"base": "invent", "aliases": ["invention", "inventions", "inventing", "invented"], "excludes": ["inventory", "inventories"]},
        {"base": "experiment", "aliases": ["experimentation", "experiments", "experimented", "experimenting"], "excludes": ["experience", "experiences", "experienced", "experiencing"]},
        {"base": "builder", "aliases": ["builders"]},
        "risk-taking",
        {"base": "bold", "aliases": ["boldly", "boldness"]},
        {"base": "startup", "aliases": ["startups"]},
    ],
    "managerial": [
        {"base": "disciplined", "aliases": ["discipline", "disciplines"]},
        {"base": "efficient", "aliases": ["efficiency", "efficiencies", "efficiently"]},
        {"base": "productive", "aliases": ["productivity", "productively"], "excludes": ["product", "products", "production", "productions"]},
        {"base": "process", "aliases": ["processes"], "excludes": ["processor", "processors", "processing", "processed"]},
        {"base": "govern", "aliases": ["governance", "governing", "governed"], "excludes": ["government", "governments", "governmental"]},
        {"base": "cost", "aliases": ["costs", "costing"], "excludes": ["costume", "costumes"]},
        {"base": "control", "aliases": ["controls", "controlling", "controlled"]},
        "capital discipline",
        {"base": "reliable", "aliases": ["reliability", "reliably"]},
        {"base": "safety"},
    ],
    "internal_innovation": [
        {"base": "invent", "aliases": ["invention", "inventions", "inventing", "invented"], "excludes": ["inventory", "inventories"]},
        "R&D",
        {"base": "research", "aliases": ["researcher", "researchers", "researching", "researched"]},
        {"base": "engineer", "aliases": ["engineering", "engineered", "engineers"], "excludes": ["engine", "engines"]},
        {"base": "build", "aliases": ["builds", "built", "building", "builder", "builders"], "excludes": ["buildings"]},
        {"base": "develop", "aliases": ["development", "developments", "developed", "developing", "developer", "developers"]},
        "technology development",
    ],
    "external_innovation": [
        {"base": "acquire", "aliases": ["acquisition", "acquisitions", "acquired", "acquiring", "acquires"]},
        {"base": "merger", "aliases": ["mergers", "merge", "merged", "merging"]},
        {"base": "partner", "aliases": ["partners", "partnership", "partnerships", "partnered", "partnering"]},
        {"base": "alliance", "aliases": ["alliances"]},
        "joint venture",
        {"base": "collaborate", "aliases": ["collaboration", "collaborations", "collaborative", "collaborating", "collaborated"]},
        {"base": "ecosystem", "aliases": ["ecosystems"]},
    ],
    "risk_challenge": [
        {"base": "crisis", "aliases": ["crises"]},
        {"base": "shock", "aliases": ["shocks", "shocked"]},
        {"base": "volatile", "aliases": ["volatility", "volatilities"]},
        {"base": "uncertain", "aliases": ["uncertainty", "uncertainties"]},
        {"base": "disrupt", "aliases": ["disruption", "disruptions", "disruptive"]},
        {"base": "geopolitical", "aliases": ["geopolitics"]},
        {"base": "risk", "aliases": ["risks", "risky"]},
        {"base": "challenge", "aliases": ["challenges", "challenging", "challenged"]},
        {"base": "pandemic", "aliases": ["pandemics"]},
        "supply constraint",
    ],
    "success_performance": [
        "cash flow",
        {"base": "dividend", "aliases": ["dividends"]},
        {"base": "buyback", "aliases": ["buybacks"]},
        {"base": "productive", "aliases": ["productivity", "productively"], "excludes": ["product", "products", "production", "productions"]},
        {"base": "record", "aliases": ["records", "recording", "recorded"]},
        {"base": "margin", "aliases": ["margins"]},
        {"base": "return", "aliases": ["returns", "returning", "returned"]},
        {"base": "profit", "aliases": ["profits", "profitable", "profitably", "profitability"]},
        {"base": "growth", "aliases": ["grow", "grows", "growing", "grown", "grew"]},
        {"base": "performance", "aliases": ["performances"]},
    ],
}


# ---------------------------------------------------------------------------
# Subtheme breakdown used by the report appendix
# ---------------------------------------------------------------------------

THEME_SUBTHEMES: list[dict[str, object]] = [
    {"theme": "Strategic Leadership", "subtheme": "Founder/ownership mentality",
     "terms": [
         {"base": "founder", "aliases": ["founders", "founding", "founded"], "excludes": ["found"]},
         {"base": "ownership"}, {"base": "owner", "aliases": ["owners"]},
         "day 1", "day one",
         {"base": "entrepreneurial", "aliases": ["entrepreneur", "entrepreneurs", "entrepreneurship"]},
         "long-term owner",
         {"base": "builder", "aliases": ["builders"]},
     ]},
    {"theme": "Strategic Leadership", "subtheme": "Ambidexterity/tension",
     "terms": [
         {"base": "ambidextrous", "aliases": ["ambidexterity"]},
         {"base": "paradox", "aliases": ["paradoxes", "paradoxical"]},
         "trade-off", "tradeoff",
         {"base": "tension", "aliases": ["tensions"]},
         "dual mandate", {"base": "dual"}, {"base": "both"},
     ]},
    {"theme": "Strategic Leadership", "subtheme": "Boldness/discipline",
     "terms": [
         {"base": "bold", "aliases": ["boldly", "boldness"]},
         {"base": "disciplined", "aliases": ["discipline", "disciplines"]},
         {"base": "conviction", "aliases": ["convictions"]},
         {"base": "decisive", "aliases": ["decisiveness", "decisively"], "excludes": ["decision", "decisions"]},
         "high standards", "capital discipline",
     ]},
    {"theme": "Strategic Leadership", "subtheme": "Stewardship/accountability",
     "terms": [
         {"base": "stewardship", "aliases": ["steward", "stewards"]},
         {"base": "accountable", "aliases": ["accountability"], "excludes": ["account", "accounts", "accounting"]},
         {"base": "responsible", "aliases": ["responsibility", "responsibly", "responsibilities"]},
         {"base": "safety"}, {"base": "trust", "aliases": ["trusted", "trusting", "trusts"]},
         {"base": "integrity", "stem": False},
     ]},
    {"theme": "Strategic Leadership", "subtheme": "Managerial control",
     "terms": [
         {"base": "efficient", "aliases": ["efficiency", "efficiencies", "efficiently"]},
         {"base": "productive", "aliases": ["productivity", "productively"], "excludes": ["product", "products", "production", "productions"]},
         "cost control",
         {"base": "process", "aliases": ["processes"], "excludes": ["processor", "processors", "processing", "processed"]},
         {"base": "govern", "aliases": ["governance", "governing", "governed"], "excludes": ["government", "governments"]},
     ]},
    {"theme": "Horizon Scanning / Sense-making", "subtheme": "Disruption/uncertainty",
     "terms": [
         {"base": "disrupt", "aliases": ["disruption", "disruptive", "disruptions", "disruptor"]},
         {"base": "uncertain", "aliases": ["uncertainty", "uncertainties"]},
         {"base": "volatile", "aliases": ["volatility", "volatilities"]},
         {"base": "turbulent", "aliases": ["turbulence"]},
         {"base": "crisis", "aliases": ["crises"]},
         {"base": "shock", "aliases": ["shocks", "shocked"]},
     ]},
    {"theme": "Horizon Scanning / Sense-making", "subtheme": "Future orientation",
     "terms": [
         {"base": "future", "aliases": ["futures"]},
         "long-term", "long term",
         {"base": "decade", "aliases": ["decades"]},
         {"base": "emerge", "aliases": ["emerging", "emerged", "emerges", "emergent"]},
         "tomorrow", "next wave", "next decade",
     ]},
    {"theme": "Horizon Scanning / Sense-making", "subtheme": "Discovery/exploration",
     "terms": [
         {"base": "discover", "aliases": ["discovery", "discoveries", "discovered", "discovering"]},
         {"base": "explore", "aliases": ["exploration", "exploring", "explored", "exploratory", "explorer"]},
         {"base": "learn", "aliases": ["learning", "learned", "learner", "learners", "learns"]},
         {"base": "opportunity", "aliases": ["opportunities"]},
         {"base": "option", "aliases": ["options", "optional", "optionality"]},
         {"base": "experiment", "aliases": ["experimentation", "experimental", "experiments", "experimented"], "excludes": ["experience", "experiences", "experienced", "experiencing"]},
     ]},
    {"theme": "Horizon Scanning / Sense-making", "subtheme": "Technology transition",
     "terms": [
         "artificial intelligence", "AI", "generative AI", "gen AI",
         "machine learning", "deep learning", "neural network", "neural networks",
         "large language model", "LLM", "foundation model",
         "artificial general intelligence", "AGI", "AI factory", "AI infrastructure",
         "cloud", "GPU", "energy transition",
         {"base": "digital", "aliases": ["digitally", "digitalization", "digitization", "digitized"]},
         {"base": "automate", "aliases": ["automation", "automated", "automating", "automatic"]},
         {"base": "electrify", "aliases": ["electrification", "electric", "electrified"]},
     ]},
    {"theme": "Horizon Scanning / Sense-making", "subtheme": "External environment",
     "terms": [
         {"base": "regulate", "aliases": ["regulation", "regulatory", "regulator", "regulators", "regulations", "regulated"]},
         {"base": "geopolitical", "aliases": ["geopolitics"]},
         {"base": "macro"}, {"base": "policy", "aliases": ["policies"]},
         {"base": "demand", "aliases": ["demands", "demanded", "demanding"]},
         {"base": "commodity", "aliases": ["commodities"]},
         {"base": "competition", "aliases": ["competitions", "compete", "competes", "competing", "competitive", "competitor", "competitors"]},
     ]},
    {"theme": "Purpose, Vision, and Governance", "subtheme": "Customer orientation",
     "terms": [
         {"base": "customer", "aliases": ["customers"], "excludes": ["custom", "customize", "customized", "customizing", "customizes"]},
         {"base": "consumer", "aliases": ["consumers"], "excludes": ["consume", "consumed", "consuming", "consumables", "consumes", "consumption"]},
         {"base": "client", "aliases": ["clients"]},
         {"base": "user", "aliases": ["users"]},
         {"base": "experience", "aliases": ["experiences", "experienced", "experiencing"]},
         {"base": "convenience", "aliases": ["convenient", "conveniently"]},
     ]},
    {"theme": "Purpose, Vision, and Governance", "subtheme": "Shareholder/value orientation",
     "terms": [
         {"base": "shareholder", "aliases": ["shareholders"]},
         {"base": "stockholder", "aliases": ["stockholders"]},
         {"base": "return", "aliases": ["returns", "returning", "returned"]},
         "cash flow", "value creation",
         {"base": "dividend", "aliases": ["dividends"]},
     ]},
    {"theme": "Purpose, Vision, and Governance", "subtheme": "Market/category leadership",
     "terms": [
         {"base": "leader", "aliases": ["leaders", "leadership"]},
         "market leadership", "category leadership",
         {"base": "scale", "aliases": ["scales", "scaled", "scaling"]},
         {"base": "ecosystem", "aliases": ["ecosystems"]},
     ]},
    {"theme": "Purpose, Vision, and Governance", "subtheme": "Mission/purpose/identity",
     "terms": [
         {"base": "mission", "aliases": ["missions"]},
         {"base": "purpose", "aliases": ["purposes", "purposeful"]},
         {"base": "values", "stem": False}, {"base": "identity", "aliases": ["identities"]},
         "human progress", "day one", "day 1",
     ]},
    {"theme": "Purpose, Vision, and Governance", "subtheme": "Governance/responsibility",
     "terms": [
         {"base": "govern", "aliases": ["governance", "governing", "governed"], "excludes": ["government", "governments"]},
         {"base": "board", "aliases": ["boards"]},
         {"base": "oversight"},
         {"base": "ethic", "aliases": ["ethics", "ethical", "ethically"]},
         {"base": "responsible", "aliases": ["responsibility", "responsibly", "responsibilities"]},
         "lower carbon",
     ]},
    {"theme": "Strategic Options, Experimentation, and Choices", "subtheme": "Internal invention/R&D",
     "terms": [
         {"base": "invent", "aliases": ["invention", "inventions", "inventing", "invented", "inventive"], "excludes": ["inventory", "inventories"]},
         {"base": "research", "aliases": ["researcher", "researchers", "researching", "researched"]},
         "R&D",
         {"base": "develop", "aliases": ["development", "developments", "developed", "developing", "developer", "developers"]},
         {"base": "engineer", "aliases": ["engineering", "engineered", "engineers"], "excludes": ["engine", "engines"]},
         {"base": "technology", "aliases": ["technologies", "technological", "technologically"]},
     ]},
    {"theme": "Strategic Options, Experimentation, and Choices", "subtheme": "Partnerships/ecosystems",
     "terms": [
         {"base": "partner", "aliases": ["partners", "partnership", "partnerships", "partnered", "partnering"]},
         {"base": "alliance", "aliases": ["alliances"]},
         {"base": "collaborate", "aliases": ["collaboration", "collaborations", "collaborative", "collaborating", "collaborated"]},
         {"base": "ecosystem", "aliases": ["ecosystems"]},
         {"base": "developer", "aliases": ["developers"]},
     ]},
    {"theme": "Strategic Options, Experimentation, and Choices", "subtheme": "Acquisition/integration",
     "terms": [
         {"base": "acquire", "aliases": ["acquisition", "acquisitions", "acquired", "acquiring", "acquires"]},
         {"base": "merger", "aliases": ["mergers", "merge", "merged", "merging"]},
         {"base": "integrate", "aliases": ["integration", "integrated", "integrating", "integrations"], "excludes": ["integrity", "integral"]},
         {"base": "divest", "aliases": ["divestment", "divestments", "divested", "divesting", "divestiture", "divestitures"]},
         {"base": "portfolio", "aliases": ["portfolios"]},
     ]},
    {"theme": "Strategic Options, Experimentation, and Choices", "subtheme": "Experiment/pilot/learn",
     "terms": [
         {"base": "experiment", "aliases": ["experimentation", "experimental", "experiments", "experimented", "experimenting"], "excludes": ["experience", "experiences", "experienced", "experiencing"]},
         {"base": "pilot", "aliases": ["pilots", "piloted", "piloting"]},
         {"base": "trial", "aliases": ["trials", "trialed", "trialing"]},
         {"base": "iterate", "aliases": ["iteration", "iterations", "iterating", "iterative", "iterated"]},
         {"base": "test", "aliases": ["tests", "testing", "tested"]},
         {"base": "learn", "aliases": ["learning", "learned", "learner", "learners", "learns"]},
     ]},
    {"theme": "Strategic Options, Experimentation, and Choices", "subtheme": "Prioritize/scale/allocate",
     "terms": [
         {"base": "prioritize", "aliases": ["prioritization", "prioritized", "prioritizing", "prioritizes"]},
         {"base": "allocate", "aliases": ["allocation", "allocations", "allocated", "allocating"]},
         {"base": "scale", "aliases": ["scales", "scaled", "scaling"]},
         {"base": "invest", "aliases": ["invests", "invested", "investing", "investment", "investments", "investor", "investors"]},
         {"base": "capital"},
         {"base": "choose", "aliases": ["chooses", "chose", "choosing", "chosen", "choice", "choices"]},
     ]},
    {"theme": "Agile Execution and Organization", "subtheme": "Speed/agility",
     "terms": [
         {"base": "speed", "aliases": ["speeds", "speeding"]},
         {"base": "fast", "aliases": ["faster", "fastest"]},
         {"base": "agile", "aliases": ["agility"]},
         {"base": "velocity", "aliases": ["velocities"]},
         {"base": "rapid", "aliases": ["rapidly"], "excludes": ["rapids"]},
     ]},
    {"theme": "Agile Execution and Organization", "subtheme": "Resilience/adaptability",
     "terms": [
         {"base": "resilient", "aliases": ["resilience", "resiliency"]},
         {"base": "adapt", "aliases": ["adaptable", "adaptation", "adapting", "adapted", "adaptive", "adaptability", "adapts"]},
         {"base": "flexible", "aliases": ["flexibility", "flexibly"]},
         {"base": "recover", "aliases": ["recovery", "recoveries", "recovered", "recovering", "recoverable"]},
     ]},
    {"theme": "Agile Execution and Organization", "subtheme": "Operational excellence",
     "terms": [
         "operational excellence",
         {"base": "efficient", "aliases": ["efficiency", "efficiencies", "efficiently"]},
         {"base": "reliable", "aliases": ["reliability", "reliably"]},
         {"base": "productive", "aliases": ["productivity", "productively"], "excludes": ["product", "products", "production", "productions"]},
         {"base": "process", "aliases": ["processes"], "excludes": ["processor", "processors", "processing", "processed"]},
     ]},
    {"theme": "Agile Execution and Organization", "subtheme": "Talent/capabilities",
     "terms": [
         {"base": "talent", "aliases": ["talents", "talented"]},
         {"base": "people"},
         {"base": "capability", "aliases": ["capabilities"]},
         {"base": "culture", "aliases": ["cultures", "cultural", "culturally"]},
         {"base": "organization", "aliases": ["organizations", "organizational", "organizationally"]},
         {"base": "skill", "aliases": ["skills", "skilled"]},
     ]},
    {"theme": "Agile Execution and Organization", "subtheme": "Infrastructure/scaling",
     "terms": [
         {"base": "infrastructure", "aliases": ["infrastructures"]},
         {"base": "capacity", "aliases": ["capacities"]},
         "supply chain",
         {"base": "deploy", "aliases": ["deployment", "deployments", "deployed", "deploying"]},
         {"base": "execute", "aliases": ["execution", "executions", "executed", "executing", "executes"], "excludes": ["executive", "executives"]},
     ]},
]


def format_entry_for_csv(term) -> str:
    """Render a dictionary entry as a human-readable label for the CSV files."""
    if isinstance(term, str):
        return term
    base = term["base"]
    aliases = term.get("aliases") or []
    excludes = term.get("excludes") or []
    parts = [base]
    if aliases:
        parts.append("[" + ", ".join(aliases) + "]")
    if excludes:
        parts.append("!" + ", ".join(excludes))
    return " ".join(parts)


__all__ = [
    "Matcher",
    "build_matchers",
    "tokenize",
    "IPM_TERMS",
    "CROSS_TERMS",
    "THEME_SUBTHEMES",
    "format_entry_for_csv",
    "_stem",
]
