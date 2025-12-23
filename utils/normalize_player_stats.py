import re


def normalize_column_name(col_name: str) -> str:
    """Normalize column names to snake_case format."""

    col_name = col_name.replace(" ", "_")

    col_name = re.sub(r'(?<!^)(?=[A-Z])', "_", col_name)

    col_name = col_name.lower()

    return col_name


__all__ = ["normalize_column_name"]
