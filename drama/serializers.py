from drama import models
from rest_framework import serializers
from rest_framework.reverse import reverse

class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Role
        lookup_field = 'slug'
        fields = ('id', 'url', 'name', 'desc', 'cat', 'slug',)


class RoleInstanceSerializer(serializers.HyperlinkedModelSerializer):
    show_name = serializers.RelatedField(source='show')
    role_name = serializers.RelatedField(source='role')
    class Meta:
        model = models.RoleInstance
        lookup_field = 'id'
        fields = ('role', 'role_name', 'show', 'show_name')
        
class PersonSerializer(serializers.HyperlinkedModelSerializer):
    roles = RoleInstanceSerializer(source='roleinstance_set')
    
    class Meta:
        model = models.Person
        lookup_field = 'slug'
        fields = ('id', 'url', 'name', 'desc', 'roles', 'slug')

class SocietySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Society
        lookup_field = 'slug'
        fields = ('id', 'url', 'name', 'shortname', 'desc', 'slug')

        
class VenueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Venue
        lookup_field = 'slug'
        fields = ('id', 'url', 'name', 'desc', 'slug')

class CompanySerializer(serializers.HyperlinkedModelSerializer):
    cat = serializers.CharField(max_length=4, source='role.cat')
    person_name = serializers.RelatedField(source='person')
    role_name = serializers.CharField(source='name')
    
    class Meta:
        model = models.RoleInstance
        lookup_field = 'id'
        fields = ('role', 'role_name', 'person', 'person_name',  'cat')

class PerformanceSerializer(serializers.HyperlinkedModelSerializer):
    venue_name = serializers.RelatedField(source='venue')
    class Meta:
        model = models.Performance
        lookup_field='id'
        fields = ('start_date', 'end_date', 'time', 'venue', 'venue_name')
        
class ShowSerializer(serializers.HyperlinkedModelSerializer):
    performances = PerformanceSerializer(source='performance_set', many=True)
    society_name = serializers.RelatedField(source='society')
    cast = CompanySerializer(source = 'cast')
    band = CompanySerializer(source = 'band')
    prod = CompanySerializer(source = 'prod')
    
    class Meta:
        model = models.Show
        lookup_field = 'slug'
        fields = ('id', 'url', 'name', 'author', 'society', 'society_name', 'desc', 'performances', 'cast', 'band', 'prod', 'slug')
