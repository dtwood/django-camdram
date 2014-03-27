import datetime
from haystack import indexes
from drama.models import Show, Person, Venue, Society


class ShowIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    date = indexes.DateField(model_attr='opening_night')
    auto = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return Show


class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    auto = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return Person


class VenueIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    auto = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return Venue


class SocietyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    auto = indexes.EdgeNgramField(use_template=True)

    def get_model(self):
        return Society
