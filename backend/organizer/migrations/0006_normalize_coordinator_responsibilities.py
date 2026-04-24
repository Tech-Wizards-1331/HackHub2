"""
Data migration: normalize pre-existing coordinator responsibilities
to match the new strict TextChoices enum (uppercase values).

Maps old lowercase values → new enum values:
  'problem_statements' → 'PROBLEM_STATEMENTS'
  'analytics'          → 'ANALYTICS'
  'teams'              → 'TEAM_MANAGEMENT'
  'team_management'    → 'TEAM_MANAGEMENT'
"""

from django.db import migrations


# Old value → new enum value
LEGACY_MAP = {
    'problem_statements': 'PROBLEM_STATEMENTS',
    'analytics': 'ANALYTICS',
    'teams': 'TEAM_MANAGEMENT',
    'team_management': 'TEAM_MANAGEMENT',
}


def normalize_responsibilities(apps, schema_editor):
    HackathonCoordinator = apps.get_model('organizer', 'HackathonCoordinator')
    for coord in HackathonCoordinator.objects.all():
        if not coord.responsibilities:
            continue
        updated = []
        changed = False
        for r in coord.responsibilities:
            mapped = LEGACY_MAP.get(r, r)  # keep unknown values as-is
            if mapped != r:
                changed = True
            updated.append(mapped)
        if changed:
            coord.responsibilities = updated
            coord.save(update_fields=['responsibilities'])


def reverse_normalize(apps, schema_editor):
    # Reverse map (best-effort — 'teams' and 'team_management' both mapped
    # to TEAM_MANAGEMENT, so we pick 'teams' as the canonical reverse)
    REVERSE_MAP = {
        'PROBLEM_STATEMENTS': 'problem_statements',
        'ANALYTICS': 'analytics',
        'TEAM_MANAGEMENT': 'teams',
    }
    HackathonCoordinator = apps.get_model('organizer', 'HackathonCoordinator')
    for coord in HackathonCoordinator.objects.all():
        if not coord.responsibilities:
            continue
        updated = []
        changed = False
        for r in coord.responsibilities:
            mapped = REVERSE_MAP.get(r, r)
            if mapped != r:
                changed = True
            updated.append(mapped)
        if changed:
            coord.responsibilities = updated
            coord.save(update_fields=['responsibilities'])


class Migration(migrations.Migration):

    dependencies = [
        ('organizer', '0005_hackathoncoordinator_responsibilities'),
    ]

    operations = [
        migrations.RunPython(
            normalize_responsibilities,
            reverse_normalize,
        ),
    ]
