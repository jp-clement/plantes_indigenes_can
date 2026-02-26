#!/usr/bin/python
from __future__ import annotations

"""
The module contains a few utility functions to process the data

"""

########################################################################################
# Authorship
########################################################################################

__author__ = "Jean-Pierre Clement"
__credits__ = ["Jean-Pierre Clement"]
__license__ = "MIT"
__version__ = "1.0"
__email__ = "jean-pierre.clement@iid.ulaval.ca"
__status__ = "Production"

################################################################################
# Imports
################################################################################

import pandas as pd
from pathlib import Path
import re
import pandas as pd
from typing import Iterable, Optional



################################################################################
# List of useful functions examples
################################################################################

## ── General Helpers ─────────────────────────────────────────────────────────────
# df = cols_to_front(df, ['cols_to_move'])                    # Move selected columns to the front of a DataFrame
# setup_working_dir('/content/drive/MyDrive/Peptide_scraping') # Set working directory (auto-mount Google Drive in Colab)


################################################################################
# Text Cleaning Functions
################################################################################



def load_lexicon(filepath: str | Path = "data/lexicon.xlsx") -> pd.DataFrame:
    """
    Load and preprocess the flavor lexicon.

    """
    lex = pd.read_excel(filepath)
    if "desc" not in lex.columns or "adj" not in lex.columns:
        raise ValueError(f"Lexicon file must contain 'desc' and 'adj' columns. Found: {lex.columns.tolist()}")

    lex["desc"] = lex["desc"].astype(str).str.lower()
    lex["adj"] = lex["adj"].astype(str).str.lower()
    lex = lex.drop_duplicates(subset=["desc"])
    lex = lex.set_index("desc")

    return lex

# lex = load_lexicon("data/lexicon.xlsx")
# utils/text_cleaning.py

def remove_parentheses_text(text):
  """Removes text enclosed in parentheses from a string."""
  if isinstance(text, str):
    return re.sub(r'\(.*?\)', '', text)
  else:
    return "None"

DEFAULT_ADJECTIVES = [
    'slightly','like','like-','mild','subtle','subtly','faintly','mildly','likely',
    'strong','strongly','sometimes','ly ','notes','flavored','lightly','light',
    'low','rich','aroma','undertone','undertones', 'very', 'faint'
]

def _compile_adj_regex(adjectives: Iterable[str]) -> re.Pattern:
    """Make a case-insensitive regex to strip adjective tokens."""
    toks = sorted({a.strip() for a in adjectives if a.strip()}, key=len, reverse=True)
    parts = []
    for t in toks:
        esc = re.escape(t)
        # word-boundary for alnum-ish tokens, literal otherwise
        if re.fullmatch(r"[A-Za-z0-9\-']+", t):
            parts.append(rf"\b{esc}\b")
        else:
            parts.append(esc)
    return re.compile("|".join(parts), flags=re.IGNORECASE)

def clean_descriptor_string(
    text: str,
    lex: Optional[pd.DataFrame] = None,
    adjectives: Iterable[str] = DEFAULT_ADJECTIVES,
    max_len: int = 30,
    lex_output_col: str = "adj",
) -> list[str]:
    """
    Clean one descriptor string:
      - remove adjective-like words,
      - lowercase & strip punctuation (- ' "),
      - split by commas and trim,
      - drop tokens longer than max_len,
      - map through lex (index=raw desc, column=lex_output_col) if provided.
    Returns a list of cleaned tokens.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    adj_re = _compile_adj_regex(adjectives)
    s = adj_re.sub("", text)

    s = s.lower()
    s = s.replace("-", "").replace("'", "").replace('"', "")

    tokens = [t.strip() for t in s.split(",")]
    tokens = [t for t in tokens if t and len(t) < max_len]

    if isinstance(lex, pd.DataFrame) and lex.index.nlevels == 1 and lex_output_col in lex.columns:
        mapped = []
        for t in tokens:
            if t in lex.index:
                val = lex.loc[t, lex_output_col]
                if isinstance(val, str) and val.strip():
                    mapped.append(val.strip())
            else:
                mapped.append(t)
        tokens = mapped

    # # de-duplicate while preserving order
    # seen = set()
    # out = []
    # for t in tokens:
    #     if t not in seen:
    #         seen.add(t)
    #         out.append(t)
    ## Keep duplicates
        out = tokens
    return out

def add_clean_descriptors_column(
    df: pd.DataFrame,
    desc_col: str = "ai_descriptors",
    name_col: str = "Nom scientifique",
    lex: Optional[pd.DataFrame] = None,
    adjectives: Iterable[str] = DEFAULT_ADJECTIVES,
    max_len: int = 30,
    out_col: str = "descriptor",
) -> pd.DataFrame:
    """
    Apply cleaning to a DataFrame and create a comma-joined `out_col` per row.
    Returns a copy of df with the new column.
    """
    df_out = df.copy()
    cleaned = df_out[desc_col].apply(
        lambda s: clean_descriptor_string(s, lex=lex, adjectives=adjectives, max_len=max_len)
    )
    df_out[out_col] = cleaned.apply(lambda toks: ",".join(toks))
    return df_out


################################################################################
# Other data processing functions
################################################################################

def drop_rare_dummy_columns(
    df: pd.DataFrame,
    exclude: list[str] = None,
    threshold_ratio: float = 0.01
) -> pd.DataFrame:
    """
    Drop columns with sum of values lower than `threshold_ratio` of total rows.
    Works only for columns with integer/boolean dummies.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame.
    exclude : list[str], optional
        Column names to exclude from dropping (e.g. identifiers).
    threshold_ratio : float, default 0.01
        Minimum fraction of rows with a positive value to keep a column.

    Returns
    -------
    pd.DataFrame
        New DataFrame with rare columns dropped.
    """
    if exclude is None:
        exclude = []

    # Select only int/bool columns except excluded
    dummy_cols = [
        col for col in df.columns
        if col not in exclude and pd.api.types.is_integer_dtype(df[col])
    ]
    if not dummy_cols:
        print("⚠️ No integer columns found to filter.")
        return df

    # Calculate threshold
    threshold = len(df) * threshold_ratio

    # Sum each column and find those below threshold
    dummy_sums = df[dummy_cols].sum()
    columns_to_drop = dummy_sums[dummy_sums < threshold].index.tolist()

    # Drop them
    df = df.drop(columns=columns_to_drop)
    print(f"Dropped {len(columns_to_drop)} columns with less than {threshold_ratio*100:.1f}% True values.")
    print(f"Remaining columns: {df.shape[1]}")
    return df

# drop_rare_dummy_columns(flav, threshold_ratio = 0.01, exclude=['Nom scientifique'])

################################################################################
# Category mapping
################################################################################

def get_category_mapping() -> dict:
    """
    Return a dictionary mapping broad food category groups to their
    corresponding detailed category labels.
    """
    category_mapping = {
        "Plant": [
            "cat_Plant", "cat_plant", "cat_plantd", "cat_plantderivative"
        ],

        "Vegetable": [
            "cat_Vegetable", "cat_vegetable", "cat_vegetable-cabbage",
            "cat_vegetable-fruit", "cat_vegetable-gourd", "cat_vegetable-root",
            "cat_vegetable-stem", "cat_vegetable-tuber"
        ],

        "Fruit": [
            "cat_fruit", "cat_fruit-berry", "cat_fruit-citrus", "cat_fruit-essence"
        ],

        "Cereal_Grains": [
            "cat_cereal", "cat_cerealcrop-cereal", "cat_cerealcrop-maize"
        ],

        "Nuts_Legumes": [
            "cat_nutseed-legume", "cat_nutseed-nut", "cat_nutseed-seed", "cat_seed"
        ],

        "Herbs_Spices": [
            "cat_herb", "cat_spice", "cat_flower", "cat_essentialoil"
        ],

        "Fungus": [
            "cat_fungus"
        ],

        "Animal_Product": [
            "cat_animalproduct", "cat_meat", "cat_fishseafood-fish",
            "cat_fishseafood-seafood", "cat_dairy"
        ],

        "Prepared Foods_Dishes": [
            "cat_dish", "cat_bakery"
        ],

        "Additives": [
            "cat_additive"
        ],

        "Beverages": [
            "cat_beverage", "cat_beverage-alcoholic", "cat_beverage-caffeinated"
        ]
    }

    return category_mapping


def combine_one_hot_categories(df: pd.DataFrame,
                               mapping: dict,
                               drop_original: bool = True) -> pd.DataFrame:
    """
    Combine one-hot encoded columns based on a category mapping dictionary.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing one-hot encoded category columns.
    mapping : dict
        Dictionary mapping broad groups to a list of detailed category columns.
    drop_original : bool, default=True
        If True, drop the original detailed one-hot columns after merging.

    Returns
    -------
    pd.DataFrame
        Updated DataFrame with new combined one-hot columns.
    """
    
    df_out = df.copy()

    for broad_cat, detailed_cols in mapping.items():
        # keep only columns that exist in df
        existing_cols = [c for c in detailed_cols if c in df_out.columns]

        if not existing_cols:
            continue  # skip if none of the detailed columns exist
        
        # Combine using OR (max works for 0/1 one-hot values)
        df_out[f"cat_{broad_cat}"] = df_out[existing_cols].max(axis=1)

        if drop_original:
            df_out.drop(columns=existing_cols, inplace=True)

    return df_out
