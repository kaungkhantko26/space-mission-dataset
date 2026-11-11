#!/usr/bin/env python3
"""Render USER_GUIDE.md -> docs/guide.html using the shared site shell (tools/make_site.py)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_site
make_site.page_guide()
