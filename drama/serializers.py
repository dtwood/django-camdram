from drama import models
from rest_framework import serializers

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Role
        lookup_field = 'slug'
        fields = ('id','name','desc', 'slug')

        
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Person
        lookup_field = 'slug'
        fields = ('id', 'name', 'desc', 'slug')

class SocietySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Society
        lookup_field = 'slug'
        fields = ('id','name','desc', 'slug')

        
class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Venue
        lookup_field = 'slug'
        fields = ('id','name','desc', 'slug')

        
class ShowSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Show
        lookup_field = 'slug'
        fields = ('id','name','desc', 'slug')
