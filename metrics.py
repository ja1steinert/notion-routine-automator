import re
from typing import List, Optional, Tuple

# Funções de Cálculo

def calculate_average(values: List[str]) -> Optional[float]:
    # Retorna uma media como float ou None
    cleaned_values = [v.strip() for v in values if v.strip()]
    normalized_values = [re.sub(r'[^\d,]', '', v) for v in cleaned_values]
    numbers = [
        float(v.replace(',', '.'))
        for v in normalized_values
        if re.match(r'^\d+,\d+$|^\d+$', v)
    ]
    return sum(numbers) / len(numbers) if numbers else None

def count_emojis(values: List[str], expected_total=6) -> Tuple[int, int]:
    # Retorna uma tupla
    cleaned_values = [v.strip() for v in values if v.strip()]
    checkmarks = sum(v.count('✅') for v in cleaned_values)
    dashes = sum(v.count('➖') for v in cleaned_values)
    return checkmarks, expected_total - dashes

def calculate_time_average(times: List[str]) -> Optional[int]:
    # Retorna minutos totais como int ou None
    total_minutes = []
    for time in [v.strip() for v in times if v.strip()]:
        match = re.match(r'(\d{1,2}):(\d{1,2})', time)
        if match:
            hours, minutes = int(match.group(1)), int(match.group(2))
            total_min = hours * 60 + minutes
            if hours < 12: total_min += 1440
            total_minutes.append(total_min)
    if not total_minutes: return None
    avg_minutes = sum(total_minutes) // len(total_minutes)
    return avg_minutes % 1440

def calculate_hour_average(values: List[str]) -> Optional[int]:
    # Retorna minutos totais como int ou None
    total_minutes = []
    for value in [v.strip() for v in values if v.strip()]:
        match = re.match(r'(\d{1,2})h(\d{1,2})?$', value)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2)) if match.group(2) else 0
            total_minutes.append(hours * 60 + minutes)
    if not total_minutes: return None
    return sum(total_minutes) // len(total_minutes)


# Funções de Formatação

def format_average(avg: Optional[float]) -> str:
    return f"{round(avg, 2):.2f}L" if avg is not None else "N/A"

def format_emojis(counts: Tuple[int, int]) -> str:
    return f"{counts[0]}/{counts[1]}" if counts else "N/A"

def format_time_average(total_minutes: Optional[int]) -> str:
    if total_minutes is None: return "N/A"
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours:02d}:{minutes:02d}"

def format_hour_average(total_minutes: Optional[int]) -> str:
    if total_minutes is None: return "N/A"
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h{minutes:02d}"