"""Markdown rendering and sanitisation.

Rendering happens once, at seed time, rather than on every request: it is the same output
every time, and doing it on the way in means the dangerous step — turning text into HTML —
lives in exactly one place.
"""

import nh3
from markdown_it import MarkdownIt

# Everything a case study needs, and nothing that can execute or embed. No `script`, no
# `iframe`, no `style`, no event handlers: the author is trusted, but a sanitiser that only
# works against untrusted input is a sanitiser nobody tests.
ALLOWED_TAGS = {
    "p",
    "br",
    "hr",
    "h2",
    "h3",
    "h4",
    "strong",
    "em",
    "del",
    "code",
    "pre",
    "blockquote",
    "ul",
    "ol",
    "li",
    "a",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "img",
    "figure",
    "figcaption",
}

ALLOWED_ATTRIBUTES = {
    # `rel` is deliberately absent: nh3 refuses to allow it as an attribute while it is
    # also managing it through `link_rel`, and having it managed is the safer half.
    "a": {"href", "title"},
    "img": {"src", "alt", "title", "width", "height", "loading"},
    "code": {"class"},
    "th": {"scope"},
}

_markdown = MarkdownIt("commonmark", {"typographer": True}).enable(["table", "strikethrough"])


def render_markdown(source: str) -> str:
    """Render Markdown to sanitised HTML.

    `nh3` (Rust ammonia) rather than a regex or an HTML parser of our own: sanitisation is
    the one place where "mostly right" is indistinguishable from broken.
    """
    html = _markdown.render(source)

    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        # External links open in a new tab, and `rel` stops the target page from reaching
        # back through `window.opener`.
        link_rel="noopener noreferrer",
    ).strip()
