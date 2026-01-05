"""Code parser for extracting Python code from AI responses."""

import re
from typing import List, Optional


class CodeParser:
    """Parser for extracting Python code from AI responses."""

    @staticmethod
    def extract_code_blocks(text: str) -> List[str]:
        """
        Extract Python code blocks from text.

        Args:
            text: Text containing code blocks

        Returns:
            List of code blocks
        """
        # Pattern for ```python ... ``` blocks
        pattern = r"```python\s*(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        if matches:
            return [match.strip() for match in matches]

        # Fallback: try generic ``` blocks
        pattern = r"```\s*(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        return [match.strip() for match in matches] if matches else []

    @staticmethod
    def validate_syntax(code: str) -> bool:
        """
        Validate Python syntax.

        Args:
            code: Python code to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            compile(code, '<string>', 'exec')
            return True
        except SyntaxError:
            return False

    @staticmethod
    def extract_first_code_block(text: str) -> Optional[str]:
        """
        Extract the first code block from text.

        Args:
            text: Text containing code blocks

        Returns:
            First code block or None
        """
        blocks = CodeParser.extract_code_blocks(text)
        return blocks[0] if blocks else None
