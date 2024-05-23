from .content_extraction_strategies import ContentProcessingStrategies


def dashify(text):
    """Converts spaces and underscores in a string to dashes."""
    return text.replace("_", "-").replace(" ", "-").lower()


def deslugify(slug):
    """Converts a dash-separated slug back to the original enum value."""
    for choice in ContentProcessingStrategies:
        if slug == dashify(choice.name):
            return choice.value
    return slug
