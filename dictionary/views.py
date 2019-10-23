from django.http import HttpResponse
from django.shortcuts import render


def lookup(request, word):
    return HttpResponse("Meaning of %s is 42" % word)
