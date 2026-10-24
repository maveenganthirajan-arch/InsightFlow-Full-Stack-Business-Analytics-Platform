import pandas as pd
import numpy as np
import re

def inspect_dataset(df):
    """
    Analyzes DataFrame to provide data quality metrics:
    - Missing values per column
    - Data types
    - Total duplicate rows
    - Memory usage
    """
    total_rows = len(df)
    missing_info = {}
    dtypes_info = {}
    sample_values = {}

    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        null_pct = round((null_count / total_rows * 100), 2) if total_rows > 0 else 0
        missing_info[str(col)] = {
            'count': null_count,
            'percent': null_pct
        }
        dtypes_info[str(col)] = str(df[col].dtype)
        # 3 non-null sample values
        non_nulls = df[col].dropna().head(3).tolist()
        sample_values[str(col)] = [str(x) for x in non_nulls]

    duplicate_rows = int(df.duplicated().sum())

    return {
        'total_rows': total_rows,
        'total_columns': len(df.columns),
        'columns': [str(c) for c in df.columns],
        'missing_info': missing_info,
        'dtypes': dtypes_info,
        'sample_values': sample_values,
        'duplicate_rows': duplicate_rows
    }

def clean_dataset(df, options=None):
    """
    Executes configurable data cleaning operations on DataFrame.
    options = {
        'remove_duplicates': bool,
        'standardize_column_names': bool,
        'missing_action': 'drop' | 'fill_mean_mode' | 'fill_zero' | 'ffill' | 'none',
        'convert_dates': bool,
        'drop_empty_cols': bool
    }
    """
    if options is None:
        options = {
            'remove_duplicates': True,
            'standardize_column_names': True,
            'missing_action': 'fill_mean_mode',
            'convert_dates': True,
            'drop_empty_cols': False
        }

    cleaned_df = df.copy()
    initial_rows = len(cleaned_df)
    log = []

    # 1. Standardize column names if requested
    if options.get('standardize_column_names', False):
        orig_cols = list(cleaned_df.columns)
        cleaned_df.columns = [
            re.sub(r'[^\w\s]', '', str(c)).strip().replace(' ', '_').lower()
            for c in cleaned_df.columns
        ]
        log.append(f"Standardized {len(orig_cols)} column names to snake_case format.")

    # 2. Remove duplicates
    duplicates_removed = 0
    if options.get('remove_duplicates', False):
        dup_count = int(cleaned_df.duplicated().sum())
        if dup_count > 0:
            cleaned_df = cleaned_df.drop_duplicates()
            duplicates_removed = dup_count
            log.append(f"Removed {dup_count} duplicate rows.")

    # 3. Drop completely empty columns
    if options.get('drop_empty_cols', False):
        empty_cols = cleaned_df.columns[cleaned_df.isnull().all()].tolist()
        if empty_cols:
            cleaned_df = cleaned_df.dropna(axis=1, how='all')
            log.append(f"Dropped {len(empty_cols)} completely empty columns: {', '.join(empty_cols)}.")

    # 4. Handle Missing Values
    missing_action = options.get('missing_action', 'none')
    if missing_action == 'drop':
        before = len(cleaned_df)
        cleaned_df = cleaned_df.dropna()
        dropped = before - len(cleaned_df)
        log.append(f"Dropped {dropped} rows containing null values.")
    elif missing_action == 'fill_mean_mode':
        filled_count = 0
        for col in cleaned_df.columns:
            if cleaned_df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                    median_val = cleaned_df[col].median()
                    if not pd.isna(median_val):
                        cleaned_df[col] = cleaned_df[col].fillna(round(median_val, 2))
                        filled_count += 1
                else:
                    mode_series = cleaned_df[col].mode()
                    fill_val = mode_series[0] if not mode_series.empty else 'Unknown'
                    cleaned_df[col] = cleaned_df[col].fillna(fill_val)
                    filled_count += 1
        log.append(f"Imputed missing values across {filled_count} columns using numeric median & categorical mode.")
    elif missing_action == 'fill_zero':
        cleaned_df = cleaned_df.fillna(0)
        log.append("Replaced all missing values with 0 / blank.")
    elif missing_action == 'ffill':
        cleaned_df = cleaned_df.ffill().bfill()
        log.append("Applied forward-fill / backward-fill for sequence data.")

    # 5. Automatically detect and parse date columns
    if options.get('convert_dates', True):
        date_candidates = [
            c for c in cleaned_df.columns 
            if any(term in str(c).lower() for term in ['date', 'time', 'year', 'month', 'timestamp', 'created'])
        ]
        for col in date_candidates:
            try:
                converted = pd.to_datetime(cleaned_df[col], errors='coerce')
                # If at least 70% converted successfully, keep datetime
                if converted.notnull().sum() / max(len(cleaned_df), 1) > 0.7:
                    cleaned_df[col] = converted
                    log.append(f"Converted column '{col}' to datetime format.")
            except Exception:
                pass

    final_rows = len(cleaned_df)
    rows_removed = initial_rows - final_rows

    stats = {
        'initial_rows': initial_rows,
        'final_rows': final_rows,
        'rows_removed': rows_removed,
        'duplicates_removed': duplicates_removed,
        'operations_log': log
    }

    return cleaned_df, stats
