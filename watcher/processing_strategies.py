import json
from bs4 import BeautifulSoup

class ProcessingStrategy:
    """ Base class for different processing strategies. """
    def process(self, response_text, *args):
        raise NotImplementedError("Each strategy must implement a process method.")

class ClassSelectorStrategy(ProcessingStrategy):
    """ Extracts elements with a specific CSS class. """
    def process(self, response_text, css_class):
        soup = BeautifulSoup(response_text, 'html.parser')
        elements = soup.find_all(class_=css_class)
        return [str(element) for element in elements]

class JSONScriptStrategy(ProcessingStrategy):
    """ Parses JSON from a <script> tag and extracts a specific path. """
    def process(self, response_text):
        soup = BeautifulSoup(response_text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
        data = json.loads(script.text)
        return data['props']['pageProps']['data']['recommendedOffers']['groupedOffers']
