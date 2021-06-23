from django.contrib.auth.models import User, Group
from rest_framework import serializers
from . import models
from .models import LANGUAGE_CHOICES, STYLE_CHOICES


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = ['number', 'street', 'zip_code', 'city', 'region', 'country']


class SiteSerializer(serializers.ModelSerializer):
    address = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = models.Site
        fields = ['name', 'address']


class ClientSerializer(serializers.ModelSerializer):
    sites = SiteSerializer(many=True, read_only=True)

    class Meta:
        model = models.Client
        fields = ['url', 'name', 'phone', 'maintenance', 'sites']


class ScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Script
        fields = ['id', 'title', 'code', 'linenos', 'language', 'style']
