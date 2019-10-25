import os

from bs4 import BeautifulSoup
from django.test import TestCase

from dictionary.scrapers import WiktionaryTrEnScraper


class WiktionaryTrEnScraperTests(TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        this_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(this_dir, 'data/wiktionary')

    def get_response(self, word):
        file_dir = os.path.join(self.data_dir, word + '.html')
        with open(file_dir, 'r') as html_file:
            html = html_file.read()
            root = BeautifulSoup(html, 'html.parser')
            results = WiktionaryTrEnScraper(root).scrape()
            return results

    def test_response_gibi(self):
        expected_response = {
            'meanings': [
                {
                    'etymology': 'From Proto-Turkic *käpä (compare Hungarian kép (“picture”), a Turkic borrowing).',
                    'values': [
                        {
                            'text': 'like (similar to)',
                            'examples': [
                                {
                                    'example': 'Tupac bir kahraman gibi öldü.',
                                    'translation': 'Tupac died like a hero.'
                                }
                            ]
                        }
                    ],
                    'part_of_speech': 'postposition'
                }
            ],
            'pronunciation': [
                {
                    'type': 'IPA',
                    'values': ['/ɡibi/']
                }
            ]
        }
        self.assertDictEqual(self.get_response('gibi'), expected_response)
