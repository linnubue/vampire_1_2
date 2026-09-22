"""
Initializes vampire package.
"""

import os
from dotenv import load_dotenv

load_dotenv()

assert os.path.exists(os.getenv('VAMPIRE_DATA')), 'VAMPIRE_DATA not found'
