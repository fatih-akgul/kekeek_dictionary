from django.db import models
from django.contrib.postgres.fields import JSONField


class Dictionary(models.Model):
    identifier = models.CharField(max_length=256, db_index=True)
    name = models.CharField(max_length=256)
    short_description = models.CharField(max_length=1024)
    long_description = models.CharField(max_length=2048)
    url = models.CharField(max_length=512, blank=True)
    language_from = models.CharField(max_length=64, db_index=True)
    language_to = models.CharField(max_length=64, db_index=True)
    # Date fields:
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name_plural = 'dictionaries'

    def __str__(self):
        return self.name


class Word(models.Model):
    dictionary = models.ForeignKey(Dictionary, on_delete=models.CASCADE)
    word = models.CharField(max_length=256, db_index=True)
    word_simplified = models.CharField(max_length=256, db_index=True)
    details = JSONField()
    # Date fields:
    date_created = models.DateTimeField(auto_now_add=True, db_index=True)
    date_modified = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return self.word
