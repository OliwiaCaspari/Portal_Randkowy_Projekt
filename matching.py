from __future__ import annotations
from typing import Optional
from user import User
from preferences import MatchPreference


def compute_match_score(
    candidate: User,
    viewer_prefs: MatchPreference,
    candidate_prefs: Optional[MatchPreference] = None,
) -> float:
    """
    Oblicza wynik dopasowania kandydata (candidate) względem preferencji przeglądającego (viewer).

    Zwraca wartość z zakresu 0.0 – 1.0.
    Wynik 0.0 oznacza dyskwalifikację (twarde kryterium nie spełnione).

    Schemat ważenia:
        - Twarde kryteria (dyskwalifikacja):  płeć, wiek
        - Miękkie kryteria (punktowane):      zainteresowania, cel związku, wzajemność prefs
    """
    score = 0.0
    max_score = 0.0

    # ── 1. Twarde kryterium: płeć ──────────────────────────────────────────
    if viewer_prefs.preferred_genders:
        if candidate.gender not in viewer_prefs.preferred_genders:
            return 0.0

    # ── 2. Twarde kryterium: wiek ───────────────────────────────────────────
    age = candidate.age
    if not (viewer_prefs.age_range.min_age <= age <= viewer_prefs.age_range.max_age):
        return 0.0

    # ── 3. Miękkie: zainteresowania ─────────────────────────────────────────
    weight_interests = 40.0
    max_score += weight_interests
    if viewer_prefs.preferred_interests and candidate.profile.interests:
        common = set(viewer_prefs.preferred_interests) & set(candidate.profile.interests)
        ratio = len(common) / len(viewer_prefs.preferred_interests)
        score += ratio * weight_interests
    else:
        # Brak preferencji = pełny wynik za tę kategorię
        score += weight_interests

    # ── 4. Miękkie: cel związku ─────────────────────────────────────────────
    weight_goal = 30.0
    max_score += weight_goal
    if viewer_prefs.relationship_goals and candidate.profile.relationship_goals:
        # candidate może mieć wiele celów - sprawdzamy czy choć jeden się zgadza
        common_goals = set(viewer_prefs.relationship_goals) & set(candidate.profile.relationship_goals)
        if common_goals:
            score += weight_goal
    else:
        score += weight_goal

    # ── 5. Miękkie: wzajemność preferencji (czy kandydat też by chciał mnie?) ─
    weight_mutual = 30.0
    max_score += weight_mutual
    if candidate_prefs is not None:
        # sprawdzamy czy viewer spełnia kryteria kandydata (wymaga przekazania profilu viewera)
        # uproszczone – tutaj tylko sprawdzamy orientację kandydata
        if (
            not candidate_prefs.preferred_genders
            or candidate.gender in candidate_prefs.preferred_genders
        ):
            score += weight_mutual
    else:
        score += weight_mutual  # brak danych = zakładamy wzajemność

    return round(score / max_score, 4) if max_score > 0 else 0.0


def filter_candidates(
    all_users: list[User],
    viewer: User,
    viewer_prefs: MatchPreference,
    already_seen_ids: Optional[set[str]] = None,
) -> list[tuple[User, float]]:
    """
    Filtruje listę użytkowników i zwraca posortowane wyniki dopasowania.

    Returns:
        Lista krotek (User, score) posortowana malejąco według wyniku.
    """
    already_seen_ids = already_seen_ids or set()
    results = []

    for user in all_users:
        # Wyklucz siebie i już ocenionych
        if user.id == viewer.id or user.id in already_seen_ids:
            continue
        # Wyklucz nieaktywnych
        if not user.is_active:
            continue

        score = compute_match_score(user, viewer_prefs)
        if score > 0.0:
            results.append((user, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results