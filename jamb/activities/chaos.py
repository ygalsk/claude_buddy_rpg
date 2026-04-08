from __future__ import annotations

from ..constants import CHAOS_SCENARIOS
from .choice import ChoiceActivity


class ChaosRouletteActivity(ChoiceActivity):
    """Pick the most chaotic response!"""

    stat_name = "chaos"
    title = "Chaos Roulette"
    header = "CHAOS ROULETTE"
    scenarios = CHAOS_SCENARIOS
    tiers = [
        (4, "MAXIMUM CHAOS! +{gain} CHAOS", "error"),
        (3, "Pretty chaotic! +{gain} CHAOS", "warning"),
        (0, "Too sensible! +{gain} CHAOS", "dim"),
    ]
