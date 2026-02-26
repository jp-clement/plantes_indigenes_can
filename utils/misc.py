#!/usr/bin/python


"""
The module contains a few utility functions that are practical to have

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
import ast
import inspect
import logging
import os
import pandas as pd
import random 
import sys  
import time

################################################################################
# List of useful functions examples
################################################################################

## ── General Helpers ─────────────────────────────────────────────────────────────
# df = cols_to_front(df, ['cols_to_move'])                    # Move selected columns to the front of a DataFrame
# setup_working_dir('/content/drive/MyDrive/Peptide_scraping') # Set working directory (auto-mount Google Drive in Colab)


################################################################################
# Code
################################################################################

def cols_to_front(df, cols_to_move):
  """
  Moves a list of specified columns to the front of a DataFrame.

  Args:
    df: The input pandas DataFrame.
    cols_to_move: A list of column names to move to the front.

  Returns:
    A new DataFrame with the specified columns at the beginning.
  """
  # Ensure all columns to move are in the DataFrame
  for col in cols_to_move:
    if col not in df.columns:
      print(f"Warning: Column '{col}' not found in DataFrame.")
      cols_to_move.remove(col)

  # Create a list of the remaining columns
  remaining_cols = [col for col in df.columns if col not in cols_to_move]

  # Combine the lists to get the new column order
  new_order = cols_to_move + remaining_cols

  # Return the DataFrame with the new column order
  return df[new_order]


def setup_working_dir(path: str) -> None:
    """
    Sets the working directory depending on whether the script is running in Google Colab or not.

    Parameters
    ----------
    path : str
        The path to set as working directory when running in Google Colab.
    """
    if 'google.colab' in sys.modules:
        from google.colab import drive
        drive.mount('/content/drive')
        os.chdir(path)
        print(f"Working directory set to: {os.getcwd()}")
    else:
        print("Not running inside Google Colab. No directory change performed.")

