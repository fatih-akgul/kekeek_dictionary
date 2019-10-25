import json

from django.http import HttpResponse

from dictionary.scrapers import ScrapingDelegator
from dictionary.models import Word, Dictionary


def lookup(request, word):
    results = Word.objects.filter(word_simplified=word)
    response = {'error': 'Not found: ' + word}
    found = False
    for result in results:
        response = result.details
        found = True

    if not found:
        dictionaries = Dictionary.objects.filter(allows_scraping=True)
        for dictionary in dictionaries:
            scraper = ScrapingDelegator(dictionary)
            response = scraper.delegate(word)

    return HttpResponse('%s' % json.dumps(response), content_type='application/json')
