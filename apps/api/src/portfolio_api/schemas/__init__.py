"""Wire-format models.

Deliberately separate from the persistence documents in `models/`: the database shape must
be free to change without leaking new fields into the public API (ARCHITECTURE § 6.2).
"""
