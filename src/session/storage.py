"""Session storage for saving and loading sessions."""

import json
from pathlib import Path
from typing import Optional, List
from loguru import logger

from .session import Session


class SessionStorage:
    """Storage manager for sessions."""

    def __init__(self, storage_dir: str = "sessions"):
        """
        Initialize session storage.

        Args:
            storage_dir: Directory to store sessions
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        logger.info(f"Session storage initialized at {self.storage_dir}")

    def save(self, session: Session) -> bool:
        """
        Save a session to disk.

        Args:
            session: Session to save

        Returns:
            True if successful
        """
        try:
            file_path = self.storage_dir / f"{session.id}.json"
            data = session.model_dump(mode='json')

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Saved session: {session.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    def load(self, session_id: str) -> Optional[Session]:
        """
        Load a session from disk.

        Args:
            session_id: Session ID to load

        Returns:
            Session object or None if not found
        """
        try:
            file_path = self.storage_dir / f"{session_id}.json"

            if not file_path.exists():
                logger.warning(f"Session not found: {session_id}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            session = Session(**data)
            logger.info(f"Loaded session: {session_id}")
            return session

        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return None

    def list_sessions(self) -> List[str]:
        """
        List all available session IDs.

        Returns:
            List of session IDs
        """
        try:
            sessions = [f.stem for f in self.storage_dir.glob("*.json")]
            return sorted(sessions)
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []

    def delete(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if successful
        """
        try:
            file_path = self.storage_dir / f"{session_id}.json"

            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted session: {session_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False
