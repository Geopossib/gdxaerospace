"""S-N (Basquin power-law) fatigue life and Miner's-rule cumulative damage.

Reference
---------
- Basquin, O.H., "The Exponential Law of Endurance Tests", ASTM
  Proceedings, 1910 (the original power-law S-N relation).
- Dowling, N.E., *Mechanical Behavior of Materials*, 4th ed., Ch. 9,
  for the standard ``sigma_a = A * N^b`` fitted S-N curve form used
  here and the Palmgren-Miner cumulative damage rule.
- Shigley's *Mechanical Engineering Design*, 10th ed., Ch. 6, for the
  same relations as commonly applied in machine-design practice.

Assumptions
-----------
- Constant-amplitude, fully-reversed (or otherwise consistent
  mean-stress) loading for the S-N curve itself; this module does not
  apply a mean-stress correction (e.g. Goodman, Gerber) -- the fatigue
  strength coefficient/exponent passed in must already correspond to
  the loading's actual mean stress condition.
- Miner's rule (linear cumulative damage) is a widely used engineering
  approximation, not an exact physical law -- it ignores load-sequence
  effects (the order in which different stress levels are applied can
  measurably change the true fatigue life).
"""

from __future__ import annotations

from fatiguepy.exceptions import InvalidFatigueInputError


def basquin_life(
    stress_amplitude: float,
    fatigue_strength_coefficient: float,
    fatigue_strength_exponent: float,
) -> float:
    """Compute cycles to failure from the Basquin power-law S-N relation.

    ``sigma_a = A * N^b``, so ``N = (sigma_a / A)^(1/b)``.

    Parameters
    ----------
    stress_amplitude:
        Applied stress amplitude, Pa, > 0.
    fatigue_strength_coefficient:
        ``A``, the fatigue strength coefficient (stress-intercept at
        N=1 cycle), Pa, > 0.
    fatigue_strength_exponent:
        ``b``, the fatigue strength exponent, dimensionless, < 0
        (fatigue strength decreases with increasing cycle count).

    Returns
    -------
    float
        Predicted cycles to failure, N.

    Example
    -------
    >>> round(
    ...     basquin_life(
    ...         stress_amplitude=300e6,
    ...         fatigue_strength_coefficient=1000e6,
    ...         fatigue_strength_exponent=-0.1,
    ...     ),
    ...     0,
    ... )
    169351.0

    """
    if stress_amplitude <= 0:
        raise InvalidFatigueInputError(
            f"stress_amplitude must be positive, got {stress_amplitude!r}"
        )
    if fatigue_strength_coefficient <= 0:
        raise InvalidFatigueInputError(
            f"fatigue_strength_coefficient must be positive, got {fatigue_strength_coefficient!r}"
        )
    if fatigue_strength_exponent >= 0:
        raise InvalidFatigueInputError(
            f"fatigue_strength_exponent must be negative, got {fatigue_strength_exponent!r}"
        )
    ratio = stress_amplitude / fatigue_strength_coefficient
    return ratio ** (1 / fatigue_strength_exponent)


def basquin_stress_amplitude(
    cycles: float, fatigue_strength_coefficient: float, fatigue_strength_exponent: float
) -> float:
    """Invert :func:`basquin_life`: the stress amplitude for a target life ``N``.

    ``sigma_a = A * N^b``.

    Parameters
    ----------
    cycles:
        Target cycles to failure, N, > 0.
    fatigue_strength_coefficient:
        ``A``, Pa, > 0.
    fatigue_strength_exponent:
        ``b``, dimensionless, < 0.

    Returns
    -------
    float
        Stress amplitude, Pa.

    Example
    -------
    >>> round(
    ...     basquin_stress_amplitude(
    ...         cycles=169350.0,
    ...         fatigue_strength_coefficient=1000e6,
    ...         fatigue_strength_exponent=-0.1,
    ...     )
    ...     / 1e6,
    ...     1,
    ... )
    300.0

    """
    if cycles <= 0:
        raise InvalidFatigueInputError(f"cycles must be positive, got {cycles!r}")
    if fatigue_strength_coefficient <= 0:
        raise InvalidFatigueInputError(
            f"fatigue_strength_coefficient must be positive, got {fatigue_strength_coefficient!r}"
        )
    if fatigue_strength_exponent >= 0:
        raise InvalidFatigueInputError(
            f"fatigue_strength_exponent must be negative, got {fatigue_strength_exponent!r}"
        )
    return fatigue_strength_coefficient * cycles**fatigue_strength_exponent


def miners_rule_damage(cycles_applied: list[float], cycles_to_failure: list[float]) -> float:
    """Compute cumulative fatigue damage via the Palmgren-Miner linear damage rule.

    ``D = sum(n_i / N_i)`` over each stress level ``i``: ``n_i`` cycles
    applied out of ``N_i`` cycles to failure at that level. Failure is
    predicted when ``D >= 1``.

    Parameters
    ----------
    cycles_applied:
        Number of cycles actually applied at each stress level, >= 0.
    cycles_to_failure:
        Number of cycles to failure at each corresponding stress level
        (e.g. from :func:`basquin_life`), > 0. Must be the same length
        as ``cycles_applied``.

    Returns
    -------
    float
        Cumulative damage fraction ``D``. ``D < 1``: predicted safe;
        ``D >= 1``: predicted failure.

    Example
    -------
    >>> round(
    ...     miners_rule_damage(
    ...         cycles_applied=[1000.0, 2000.0], cycles_to_failure=[10000.0, 8000.0]
    ...     ),
    ...     3,
    ... )
    0.35

    """
    if len(cycles_applied) != len(cycles_to_failure):
        raise InvalidFatigueInputError(
            f"cycles_applied (len {len(cycles_applied)}) and cycles_to_failure "
            f"(len {len(cycles_to_failure)}) must have the same length"
        )
    if len(cycles_applied) == 0:
        raise InvalidFatigueInputError("cycles_applied must not be empty")
    damage = 0.0
    for n, big_n in zip(cycles_applied, cycles_to_failure, strict=True):
        if n < 0:
            raise InvalidFatigueInputError(
                f"cycles_applied values must be non-negative, got {n!r}"
            )
        if big_n <= 0:
            raise InvalidFatigueInputError(
                f"cycles_to_failure values must be positive, got {big_n!r}"
            )
        damage += n / big_n
    return damage
