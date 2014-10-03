import datetime
from haystack import indexes
from drama.models import Show, Person, Venue, Society, Role


class ShowIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    date = indexes.DateField(model_attr='opening_night')
    auto = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return Show

    def index_queryset(self, using=None):
        return self.get_model().objects.approved()


class PersonIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    auto = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return Person

    def index_queryset(self, using=None):
        return self.get_model().objects.approved()

class VenueIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    auto = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return Venue

    def index_queryset(self, using=None):
        return self.get_model().objects.approved()


class SocietyIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    auto = indexes.EdgeNgramField(use_template=True)

    def get_model(self):
        return Society

    def index_queryset(self, using=None):
        return self.get_model().objects.approved()

class RoleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    auto = indexes.EdgeNgramField(model_attr='name')

    def get_model(self):
        return Role

    def index_queryset(self, using=None):
        return self.get_model().objects.approved()
