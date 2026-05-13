import re

SUSPICIOUS_KEYWORDS = [
    b"/JavaScript",
    b"/JS",
    b"/OpenAction",
    b"/EmbeddedFile",
]

URL_RE = re.compile(rb"https?://[^\s<>()'\"\\]+")
IP_RE = re.compile(rb"\b(?:\d{1,3}\.){3}\d{1,3}\b")
