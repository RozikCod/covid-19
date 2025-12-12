"""
COVID-19 Dashboard Pages Module

This package contains all the page modules for the COVID-19 dashboard application.
Each module represents a separate page or functionality of the application.
"""

# Import all page modules
from . import auth
from . import dashboard
from . import compare
from . import add_case
from . import users

# Define what should be available when using "from pages import *"
__all__ = ['auth', 'dashboard', 'compare', 'add_case', 'users']

# Package metadata
__version__ = '1.0.0'
__author__ = 'COVID Dashboard Team'