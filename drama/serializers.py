from drama import models
from rest_framework import serializers
from rest_framework.reverse import reverse

from django.contrib.auth import get_user_model

User = get_user_model()

class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Role
        lookup_field = 'slug'
        fields = ('id', 'url', 'name', 'desc', 'cat')


class RoleInstanceSerializer(serializers.HyperlinkedModelSerializer):
    show_name = serializers.RelatedField(source='show', queryset=User.objects.all())
    role_name = serializers.RelatedField(source='role', queryset=User.objects.all())
    class Meta:
        model = models.RoleInstance
        lookup_field = 'id'
        fields = ('role', 'role_name', 'show', 'show_name')
        
        
class PersonSerializer(serializers.HyperlinkedModelSerializer):
    roles = RoleInstanceSerializer(source='roleinstance_set')
    
    class Meta:
        model = models.Person
        lookup_field = 'slug'
        fields = ('id', 'url', 'name', 'desc', 'roles')

        
class CompanySerializer(serializers.HyperlinkedModelSerializer):
    cat = serializers.CharField(max_length=4, source='role.cat')
    person_name = serializers.RelatedField(source='person', queryset=User.objects.all())
    role_name = serializers.CharField(source='name')
    
    class Meta:
        model = models.RoleInstance
        lookup_field = 'id'
        fields = ('role', 'role_name', 'person', 'person_name',  'cat')


class PerformanceSerializer(serializers.HyperlinkedModelSerializer):
    venue_name = serializers.RelatedField(source='venue', queryset=User.objects.all())
    class Meta:
        model = models.Performance
        lookup_field='id'
        fields = ('start_date', 'end_date', 'time', 'venue', 'venue_name')
        

class ShowSerializer(serializers.HyperlinkedModelSerializer):
    performances = PerformanceSerializer(source='performance_set', many=True)
    cast = CompanySerializer(source = 'cast')
    band = CompanySerializer(source = 'band')
    prod = CompanySerializer(source = 'prod')
    
    class Meta:
        model = models.Show
        lookup_field = 'slug'
        fields = ('id', 'url', 'name', 'author', 'societies', 'desc', 'performances', 'cast', 'band', 'prod', 'image')


class EmailListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.EmailList
        lookup_field = 'slug'
        fields = ('name',)


class VenueSerializer(serializers.HyperlinkedModelSerializer):
    shows = serializers.SerializerMethodField(method_name='get_shows')

    def get_shows(self, obj):
        return [reverse('show-detail', kwargs={'slug': x.slug}, request=self.context.get('request', None),
                        format=self.context.get('format', None)) for x in obj.get_shows()]

    class Meta:
        model = models.Venue
        lookup_field = 'slug'
        fields = ('id', 'url', 'name', 'desc', 'shows')


class SocietySerializer(serializers.HyperlinkedModelSerializer):
    shows = serializers.SerializerMethodField(method_name='get_shows')

    def get_shows(self, obj):
        return [reverse('show-detail', kwargs={'slug': x.slug}, request=self.context.get('request', None),
                        format=self.context.get('format', None)) for x in obj.get_shows()]
    
    class Meta:
        model = models.Society
        lookup_field = 'slug'
        fields = ('id', 'url', 'name', 'shortname', 'desc', 'image', 'shows')
