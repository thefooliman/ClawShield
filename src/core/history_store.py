import json
import os
import hashlib
from typing import Optional

class HistoryStore:
    """
    Simple history store for tracking trusted actions
    Stores actions in a JSON file with hash-based keys
    """

    def __init__(self, history_file: str = "clawshield_trust.json"):
        self.history_file = history_file
        self.history = self._load_history()

    def _load_history(self) -> dict:
        """Load history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load history: {e}")
        return {}

    def _save_history(self):
        """Save history to JSON file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save history: {e}")

    def _create_key(self, text: str, x: int, y: int) -> str:
        """
        Create a unique key for an action
        Uses hash of text + coordinates for consistency
        """
        # Use a short hash to keep keys manageable
        text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        return f"{text_hash}_{x}_{y}"

    def is_trusted(self, text: str, x: int, y: int, threshold: int = 3) -> bool:
        """
        Check if an action should be trusted
        Returns True if allowed at least `threshold` times
        """
        key = self._create_key(text, x, y)

        if key in self.history:
            allowed_count = self.history[key].get("allowed", 0)
            blocked_count = self.history[key].get("blocked", 0)

            # Only trust if allowed more than blocked and meets threshold
            if allowed_count >= threshold and allowed_count > blocked_count:
                return True

        return False

    def record_action(self, text: str, x: int, y: int, allowed: bool):
        """
        Record the outcome of an action
        """
        key = self._create_key(text, x, y)

        if key not in self.history:
            self.history[key] = {"allowed": 0, "blocked": 0}

        if allowed:
            self.history[key]["allowed"] += 1
        else:
            self.history[key]["blocked"] += 1

        self._save_history()

    def get_stats(self, text: str, x: int, y: int) -> Optional[dict]:
        """
        Get statistics for a specific action
        """
        key = self._create_key(text, x, y)
        return self.history.get(key)

    def clear_history(self):
        """Clear all history"""
        self.history = {}
        self._save_history()
        print("🗑️ History cleared")

    def get_total_actions(self) -> int:
        """Get total number of recorded actions"""
        return len(self.history)

    def get_trusted_actions(self, threshold: int = 3) -> list:
        """
        Get list of all trusted actions (keys)
        """
        trusted = []
        for key, stats in self.history.items():
            allowed = stats.get("allowed", 0)
            blocked = stats.get("blocked", 0)
            if allowed >= threshold and allowed > blocked:
                trusted.append(key)
        return trusted