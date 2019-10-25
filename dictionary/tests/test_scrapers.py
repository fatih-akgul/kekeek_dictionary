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
            print(results)
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

    def test_response_el(self):
        expected_response = {
            'meanings': [
                {
                    'etymology': 'From Old Turkic élig (“hand”), from Proto-Turkic *alı-, *ạl- (“to take”) or *el;-ig ("hand"). Cognates with Uzbek ilik, Turkmen el, Gagauz el and Sary-Yughur ɨlɨɣ.',
                    'values': [
                        {
                            'text': 'hand',
                            'examples': []
                        }
                    ],
                    'part_of_speech': 'noun'
                },
                {
                    'etymology': None,
                    'values': [
                        {
                            'text': 'a foreign person',
                            'examples': []
                        }
                    ],
                    'part_of_speech': 'noun'
                },
                {
                    'etymology': 'From Old Turkic él, from Proto-Turkic.',
                    'values': [
                        {
                            'text': 'country, homeland, province',
                            'examples': []
                        }
                    ],
                    'part_of_speech': 'noun'
                }
            ],
            'pronunciation': [
                {
                    'type': 'IPA', 'values': ['/el/', '/əl/']
                }
            ]
        }
        self.assertDictEqual(self.get_response('el'), expected_response)

    def test_response_araba(self):
        expected_response = {
            'meanings': [
                {
                    'etymology': 'Ultimate origin uncertain. Originally intended to mean "a two-wheeled cart" now being used generically for all kinds of vehicles and bicycles (Schwarz 1992: 393). According to Ramstedt (1905: 23), the Turkic form was borrowed into Iranian (Afgh. arabá, Shg. arōbā), Arabic عَرَبَة\u200e (ʿaraba), Uralic, European and Caucasian languages. A Turkic loan relation with Burushaski arabá is also discussed by Rybatzki. Considering Doerfer (1963/1965/1967/1975), the etymology of the word seems unclear, being either of Turkic or Arabic origin. Uzbek arava was loaned into Tajik aråba \'cart, carriage\' (Doerfer 1967: 12) and Ormuri arâba \'wheel\' (M29: 387). Other Turkic congnates include Uyghur araba, Kyrgyz арба (arba), Taranchi hariba, as well as Chuvash урапа (urapa), Bashkir арба (arba) and Tatar арба (arba, “covered wagon”)[1]. Rybatzki notes that all Turkic forms are too similar with Burushaski, concluding the exact donor language can not be determined.[2]',
                    'values': [
                        {
                            'text': 'car',
                            'examples': []
                        },
                        {
                            'text': 'cart',
                            'examples': []
                        },
                        {
                            'text': 'carriage',
                            'examples': []
                        }
                    ],
                    'part_of_speech': 'noun'
                }
            ],
            'pronunciation': [
                {
                    'type': 'IPA',
                    'values': ['/aɾaˈba/']
                },
                {
                    'type': 'Hyphenation',
                    'values': ['a‧ra‧ba']
                }
            ]
        }
        self.assertDictEqual(self.get_response('araba'), expected_response)
