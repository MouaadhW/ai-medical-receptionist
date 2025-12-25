"""
Load MIMIC-IV data into database
Run this after initializing the database
"""

import sys
sys.path.insert(0, '.')

from mimic.mimicloader import MIMICLoader
from loguru import logger

if name == "main":
    logger.info("Starting MIMIC-IV data load...")
    loader = MIMICLoader()
    loader.loadall()
    logger.info("MIMIC-IV data load complete!")