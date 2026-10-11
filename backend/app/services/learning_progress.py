def update_completed_sections(existing_ids, section_id, completed):
    """Return a sorted, de-duplicated section ID list after a completion toggle."""
    ids = {int(value) for value in (existing_ids or [])}
    if completed:
        ids.add(int(section_id))
    else:
        ids.discard(int(section_id))
    return sorted(ids)


def calculate_section_progress(section_ids, total_sections):
    """Calculate integer completion percentage from valid completed sections."""
    if total_sections <= 0:
        return 0
    valid = {int(value) for value in (section_ids or []) if int(value) > 0}
    return min(100, round(len(valid) * 100 / total_sections))
