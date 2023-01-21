from rest_framework import serializers
from .models import Organization, User, Campaign, Contact, Journey

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','name_first','name_last','username','email','profile_picture','organization_id','created_date','modified_date')

class UserValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = '__all__'