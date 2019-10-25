import re
from abc import ABC, abstractmethod
from typing import Dict, Any, List

import requests
from bs4 import BeautifulSoup
from django.http import Http404

from dictionary.models import Dictionary


class ScrapingDelegator:

    def __init__(self, dictionary: Dictionary):
        self.dictionary = dictionary

    def get_url(self, word: str) -> str:
        return self.dictionary.word_url_pattern % word

    def get_html(self, word: str) -> str:
        url = self.get_url(word)
        response = requests.get(url)
        if response.status_code != 200:
            raise Http404(f'Not found: {word} at {url}')
        return response.content

    def get_root_element(self, word: str) -> BeautifulSoup:
        html = self.get_html(word)
        return BeautifulSoup(html, 'html.parser')

    def delegate(self, word: str) -> Dict[str, Any]:
        results = {}
        if not self.dictionary.allows_scraping:
            return results

        root = self.get_root_element(word)
        if self.dictionary.identifier == 'wiktionary-tr-en':
            results = WiktionaryTrEnScraper(root).scrape()
        return results


class Scraper(ABC):
    def __init__(self, root: BeautifulSoup):
        self.root = root
        self.processed_headers = []

    @abstractmethod
    def scrape(self) -> Dict[str, Any]:
        pass


class WiktionaryTrEnScraper(Scraper):

    def scrape(self) -> Dict[str, Any]:
        label = self.root.find(id='Turkish')
        response = {'meanings': []}
        if label is not None:
            print('Label: %s' % label)
            print('Page title: %s' % self.root.head.title.string)
            siblings: List[BeautifulSoup] = label.parent.find_next_siblings(['h3', 'hr'])
            for sibling in siblings:
                print('>>>>>', sibling.get_text())
                if sibling.name == 'hr':
                    break
                else:
                    sibling_text = str(sibling)
                    if sibling_text not in self.processed_headers:
                        response = self.process_header(sibling, response)
                    self.processed_headers.append(sibling_text)
        return response

    def process_header(self, header: BeautifulSoup, response: Dict[str, Any]) -> Dict[str, Any]:
        if WiktionaryTrEnScraper.is_pronunciation_header(header):
            response['pronunciation'] = WiktionaryTrEnScraper.get_pronunciation(header)
        elif WiktionaryTrEnScraper.is_etymology_header(header):
            response['meanings'].append(self.get_meaning_with_etymology(header))
        elif WiktionaryTrEnScraper.is_part_of_speech_header(header):
            response['meanings'].append(WiktionaryTrEnScraper.get_meaning_without_etymology(header))

        return response

    @staticmethod
    def is_meaning_switcher(header: BeautifulSoup):
        return WiktionaryTrEnScraper.is_pronunciation_header(header) \
               or WiktionaryTrEnScraper.is_etymology_header(header) \
               or WiktionaryTrEnScraper.is_part_of_speech_header(header)

    @staticmethod
    def is_pronunciation_header(header: BeautifulSoup) -> bool:
        if header.find_all('span', text='Pronunciation'):
            return True
        return False

    @staticmethod
    def get_pronunciation(header: BeautifulSoup) -> [Dict[str, Any]]:
        results = []
        if header.find_next_sibling().name == 'ul':
            ul: BeautifulSoup = header.find_next_sibling()
            values = ul.find_all('span', class_='IPA')
            if values:
                results.append({
                    'type': 'IPA',
                    'values': [span.text for span in values]
                })

        return results

    @staticmethod
    def is_etymology_header(header: BeautifulSoup) -> bool:
        if header.find_all('span', text=re.compile('Etymology.*')):
            return True
        return False

    def get_meaning_with_etymology(self, header: BeautifulSoup) -> [Dict[str, Any]]:
        result = {'etymology': None, 'values': []}
        next_sibling: BeautifulSoup = header.find_next_sibling()
        # p is etymology details, capture it
        while next_sibling.name == 'p':
            p: BeautifulSoup = header.find_next_sibling()
            etymology = result.get('etymology')
            result['etymology'] = p.get_text().strip() if etymology is None \
                else etymology + '\n' + p.get_text().strip()
            next_sibling = next_sibling.find_next_sibling()
        # Skip pronunciation headers
        while WiktionaryTrEnScraper.is_pronunciation_header(next_sibling) or next_sibling.name == 'ul':
            next_sibling = next_sibling.find_next_sibling()
        # h4 is the header for parts of speech
        if WiktionaryTrEnScraper.is_part_of_speech_header(next_sibling):
            span: BeautifulSoup = next_sibling.find('span')
            if span:
                result['part_of_speech'] = span.get_text().strip().lower()
            if next_sibling.name == 'h3':
                self.processed_headers.append(str(next_sibling))
            next_sibling = next_sibling.find_next_sibling()
            WiktionaryTrEnScraper.process_meaning_values(next_sibling, result)
        return result

    @staticmethod
    def process_meaning_values(word_p: BeautifulSoup, meaning: Dict[str, Any]):
        next_sibling: BeautifulSoup = word_p
        while next_sibling.name == 'p':
            next_sibling = next_sibling.find_next_sibling()
        if next_sibling.name == 'ol':
            lis = next_sibling.find_all('li')
            for li in lis:
                dl: BeautifulSoup = li.find('dl')
                examples = []
                if dl:
                    dl.extract()
                    example_divs = dl.find_all(class_='h-usage-example')
                    for example_div in example_divs:
                        example_span: BeautifulSoup = example_div.find(class_='e-example')
                        if example_span:
                            example = {
                                'example': example_span.get_text(),
                                'translation': None,
                            }
                            translation: BeautifulSoup = example_div.find(class_='e-translation')
                            if translation:
                                example['translation'] = translation.get_text()
                            examples.append(example)
                value = {
                    'text': li.get_text().strip(),
                    'examples': examples
                }
                meaning['values'].append(value)
            WiktionaryTrEnScraper.process_additional_data(next_sibling, meaning)

    @staticmethod
    def is_part_of_speech_header(header: BeautifulSoup) -> bool:
        next_sibling: BeautifulSoup = header.find_next_sibling()
        while next_sibling and next_sibling.name == 'table':
            next_sibling = next_sibling.find_next_sibling()
        if next_sibling and next_sibling.name == 'p':
            next_sibling = next_sibling.find_next_sibling()
            if next_sibling.name == 'ol':
                return True
        return False

    @staticmethod
    def get_meaning_without_etymology(header: BeautifulSoup) -> [Dict[str, Any]]:
        result = {'etymology': None, 'values': []}
        span: BeautifulSoup = header.find('span')
        if span:
            result['part_of_speech'] = span.get_text().strip().lower()
            next_sibling: BeautifulSoup = header.find_next_sibling()
            while next_sibling.name == 'table':
                next_sibling = next_sibling.find_next_sibling()
            WiktionaryTrEnScraper.process_meaning_values(next_sibling, result)
        return result

    @staticmethod
    def process_additional_data(after_meaning_values: BeautifulSoup, meaning: Dict[str, Any]) -> None:
        if after_meaning_values is not None and meaning['values']:
            next_sibling = after_meaning_values
            while next_sibling is not None and not WiktionaryTrEnScraper.is_meaning_switcher(next_sibling):
                WiktionaryTrEnScraper.process_see_also(next_sibling, meaning)
                WiktionaryTrEnScraper.process_derived_terms(next_sibling, meaning)
                WiktionaryTrEnScraper.process_related_terms(next_sibling, meaning)
                WiktionaryTrEnScraper.process_synonyms(next_sibling, meaning)
                WiktionaryTrEnScraper.process_antonyms(next_sibling, meaning)
                next_sibling = next_sibling.find_next_sibling()

    @staticmethod
    def process_see_also(after_meaning_values: BeautifulSoup, meaning: Dict[str, Any]) -> None:
        WiktionaryTrEnScraper.process_by_id(after_meaning_values, meaning, 'See_also')

    @staticmethod
    def process_derived_terms(after_meaning_values: BeautifulSoup, meaning: Dict[str, Any]) -> None:
        WiktionaryTrEnScraper.process_by_id(after_meaning_values, meaning, 'Derived_terms')

    @staticmethod
    def process_related_terms(after_meaning_values: BeautifulSoup, meaning: Dict[str, Any]) -> None:
        WiktionaryTrEnScraper.process_by_id(after_meaning_values, meaning, 'Related_terms')

    @staticmethod
    def process_synonyms(after_meaning_values: BeautifulSoup, meaning: Dict[str, Any]) -> None:
        WiktionaryTrEnScraper.process_by_id(after_meaning_values, meaning, 'Synonyms')

    @staticmethod
    def process_antonyms(after_meaning_values: BeautifulSoup, meaning: Dict[str, Any]) -> None:
        WiktionaryTrEnScraper.process_by_id(after_meaning_values, meaning, 'Antonyms')

    @staticmethod
    def process_by_id(after_meaning_values: BeautifulSoup, meaning: Dict[str, Any], tag_id: str):
        result = []
        if after_meaning_values.name in ['h3', 'h4', 'h5']:
            h4: BeautifulSoup = after_meaning_values
            span: BeautifulSoup = after_meaning_values.find(id=lambda x: x and x.startswith(tag_id))
            if span:
                ul: BeautifulSoup = h4.find_next_sibling()
                if ul.name == 'ul':
                    lis = ul.find_all('li')
                    for li in lis:
                        result.append(li.get_text())
        if result:
            meaning[tag_id.lower()] = result
