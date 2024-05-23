import json
import enum

from bs4 import BeautifulSoup


class ProcessingStrategy:
    """Base class for different processing strategies."""

    def process(self, response_text, *args):
        raise NotImplementedError("Each strategy must implement a process method.")


class ClassSelectorStrategy(ProcessingStrategy):
    """Extracts elements with a specific CSS class."""

    def process(self, response_text, css_class):
        soup = BeautifulSoup(response_text, "html.parser")
        elements = soup.find_all(class_=css_class)
        return [str(element) for element in elements]


class JSONScriptStrategy(ProcessingStrategy):
    """Parses JSON from a <script> tag and extracts a specific path."""

    def process(self, response_text):
        soup = BeautifulSoup(response_text, "html.parser")
        script = soup.find(
            "script", {"id": "__NEXT_DATA__", "type": "application/json"}
        )
        data = json.loads(script.text)
        return data["props"]["pageProps"]["data"]["recommendedOffers"]["groupedOffers"]


class ProcessingStrategyChoices(enum.Enum):
    CLASS_SELECTOR = (
        "class_selector",
        "Extracts elements with a specific CSS class using BeautifulSoup.",
        ClassSelectorStrategy,
    )
    JSON_SCRIPT = (
        "json_script",
        "Parses JSON from a <script> tag and extracts specific data.",
        JSONScriptStrategy,
    )

    def __new__(cls, value, description, strategy_class):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.strategy_class = strategy_class
        return obj

    @classmethod
    def choices(cls):
        return [(key.value, key.description) for key in cls]

    @classmethod
    def get_strategy_class(cls, value):
        for item in cls:
            if item.value == value:
                return item.strategy_class
        raise ValueError(f"No strategy class found for value: {value}")
