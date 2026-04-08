from __future__ import annotations

from ..constants import SNARK_SCENARIOS
from .choice import ChoiceActivity


class ComebackBattleActivity(ChoiceActivity):
    """Pick the snarkiest comeback!"""

    stat_name = "snark"
    title = "Comeback Battle"
    header = "COMEBACK BATTLE"
    scenarios = SNARK_SCENARIOS
    tiers = [
        (4, "DEVASTATING! +{gain} SNARK", "success"),
        (3, "Pretty snarky! +{gain} SNARK", "warning"),
        (0, "Too polite! +{gain} SNARK", "dim"),
    ]
