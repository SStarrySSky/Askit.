"""LaTeX formula renderer for PAskit chat panel."""

import re
import io
import base64
from typing import Tuple, Optional

# Try to import matplotlib for LaTeX rendering
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib import mathtext
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class LaTeXRenderer:
    """Render LaTeX formulas to images for display in Qt widgets."""

    # Regex patterns for LaTeX
    DISPLAY_PATTERN = re.compile(r'\$\$(.*?)\$\$', re.DOTALL)
    INLINE_PATTERN = re.compile(r'\$([^\$]+?)\$')

    def __init__(self):
        self.cache = {}  # Cache rendered formulas

    def render_to_base64(self, latex: str, fontsize: int = 14,
                         dpi: int = 150, color: str = 'white') -> Optional[str]:
        """Render LaTeX formula to base64 PNG image."""
        if not HAS_MATPLOTLIB:
            return None

        cache_key = (latex, fontsize, dpi, color)
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            fig, ax = plt.subplots(figsize=(0.1, 0.1))
            ax.axis('off')

            # Render the formula
            text = ax.text(0, 0, f'${latex}$', fontsize=fontsize,
                          color=color, ha='left', va='bottom')

            # Get bounding box and resize figure
            fig.canvas.draw()
            bbox = text.get_window_extent(fig.canvas.get_renderer())

            # Convert to inches and add padding
            width = bbox.width / dpi + 0.1
            height = bbox.height / dpi + 0.1
            fig.set_size_inches(width, height)

            # Save to buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png', dpi=dpi,
                       transparent=True, bbox_inches='tight', pad_inches=0.02)
            plt.close(fig)

            # Convert to base64
            buf.seek(0)
            b64 = base64.b64encode(buf.read()).decode('utf-8')

            self.cache[cache_key] = b64
            return b64

        except Exception as e:
            print(f"LaTeX render error: {e}")
            return None

    def process_text(self, text: str) -> str:
        """Process text and replace LaTeX with rendered images."""
        if not HAS_MATPLOTLIB:
            return text

        # Process display math ($$...$$)
        def replace_display(match):
            latex = match.group(1).strip()
            b64 = self.render_to_base64(latex, fontsize=16)
            if b64:
                return f'<br><img src="data:image/png;base64,{b64}"/><br>'
            return f'$${latex}$$'

        text = self.DISPLAY_PATTERN.sub(replace_display, text)

        # Process inline math ($...$)
        def replace_inline(match):
            latex = match.group(1).strip()
            b64 = self.render_to_base64(latex, fontsize=12)
            if b64:
                return f'<img src="data:image/png;base64,{b64}" style="vertical-align:middle;"/>'
            return f'${latex}$'

        text = self.INLINE_PATTERN.sub(replace_inline, text)

        return text


# Global renderer instance
_renderer = None

def get_latex_renderer() -> LaTeXRenderer:
    """Get the global LaTeX renderer instance."""
    global _renderer
    if _renderer is None:
        _renderer = LaTeXRenderer()
    return _renderer
