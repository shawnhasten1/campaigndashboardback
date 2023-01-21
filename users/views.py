from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Organization, User, Campaign, Contact, Journey
from .serializers import OrganizationSerializer, UserSerializer, CampaignSerializer, ContactSerializer, JourneySerializer, UserValidatorSerializer

import bcrypt
import jwt
import datetime
from decouple import config

@api_view(['GET', 'POST', 'DELETE'])
def organizations(request):
    if request.method == 'GET':
        authorization = jwt.decode(request.headers['Authorization'], config('SECRET_KEY'), algorithms=["HS256"])
        organizations = Organization.objects.get(pk=authorization['organization_id'])
        serializer = OrganizationSerializer(organizations, many=False)
        return JsonResponse(serializer.data, json_dumps_params={'indent': 2}, safe=False)
    elif request.method == 'POST':
        return Response(create_organization(request.data))
    elif request.method == 'DELETE':
        try:
            authorization = jwt.decode(request.headers['Authorization'], config('SECRET_KEY'), algorithms=["HS256"])
            organization = Organization.objects.get(pk=authorization['organization_id'])
        except:
            return JsonResponse({'Message':'Failure'}, json_dumps_params={'indent': 2}, safe=False)
        organization.delete()
        return JsonResponse({'Message':'Organization Deleted'}, json_dumps_params={'indent': 2}, safe=False)

@api_view(['GET', 'POST', 'DELETE'])
def users(request, slug=None):
    try:
        authorization = jwt.decode(request.headers['Authorization'], config('SECRET_KEY'), algorithms=["HS256"])
        authorization['organization_id']
    except:
        return JsonResponse({'Message':'Not Authorized'}, json_dumps_params={'indent': 2}, safe=False, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        serializer = None
        if slug:
            user = User.objects.get(pk=slug)
            if user:
                serializer = UserSerializer(user)
        else:
            users = User.objects.all()
            if users:
                serializer = UserSerializer(users, many=True)
        return JsonResponse(serializer.data, json_dumps_params={'indent': 2}, safe=False)
    elif request.method == 'POST':
        create_user(request.data)
        return JsonResponse({'Message':'User Added'}, json_dumps_params={'indent': 2}, safe=False)
    elif request.method == 'DELETE':
        if slug:
            try:
                user = User.objects.get(pk=slug)
            except:
                return JsonResponse({'Message':'Failure'}, json_dumps_params={'indent': 2}, safe=False)
            user.delete()
            return JsonResponse({'Message':'Campaign Deleted'}, json_dumps_params={'indent': 2}, safe=False)
        return JsonResponse({'Message':'Failure'}, json_dumps_params={'indent': 2}, safe=False)

@api_view(['POST'])
def register(request):
    org_data = request.data['organization']
    organization = create_organization(org_data)
    user_data = request.data['user']
    user_data['organization_id'] = organization['id']
    create_user(user_data)
    return JsonResponse({'Message':'User Added'}, json_dumps_params={'indent': 2}, safe=False)

@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        user = User.objects.get(username=request.data['username'])
        if user:
            serializer = UserValidatorSerializer(user, many=False)
            password = bytes(request.data['password'], 'utf-8')
            if bcrypt.checkpw(password,bytes(serializer.data['password'], 'utf-8')):
                now = datetime.datetime.utcnow()
                expires = now + datetime.timedelta(days=14)
                encoded_jwt = jwt.encode({
                    "created_at":str(now), 
                    "expires":str(expires),
                    "user_id":serializer.data['id'],
                    "organization_id":serializer.data['organization_id'],
                }, config('SECRET_KEY'), algorithm="HS256")
                return JsonResponse({'Message':'Success', 'token':encoded_jwt})
        return JsonResponse({'Message':'Not Authorized'}, json_dumps_params={'indent': 2}, safe=False, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'POST', 'DELETE'])
def campaigns(request, slug=None):
    authorization = jwt.decode(request.headers['Authorization'], config('SECRET_KEY'), algorithms=["HS256"])
    if request.method == 'GET':
        campaigns = Campaign.objects.all().filter(organization_id=authorization['organization_id'])
        serializer = CampaignSerializer(campaigns, many=True)
        if slug:
            campaign = Campaign.objects.get(pk=slug)
            serializer = CampaignSerializer(campaign)
        return JsonResponse(serializer.data, json_dumps_params={'indent': 2}, safe=False)
    elif request.method == 'POST':
        req_data = request.data
        req_data['owner_id'] = authorization['user_id']
        req_data['organization_id'] = authorization['organization_id']
        serializer = CampaignSerializer(data=req_data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if slug:
            try:
                campaign = Campaign.objects.get(pk=slug)
            except:
                return JsonResponse({'Message':'Failure'}, json_dumps_params={'indent': 2}, safe=False)
            campaign.delete()
            return JsonResponse({'Message':'Campaign Deleted'}, json_dumps_params={'indent': 2}, safe=False)
        return JsonResponse({'Message':'Failure'}, json_dumps_params={'indent': 2}, safe=False)

@api_view(['GET', 'POST', 'DELETE'])
def contacts(request, slug=None):
    if request.method == 'GET':
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        if slug:
            contact = Contact.objects.get(pk=slug)
            serializer = ContactSerializer(contact)
        return JsonResponse(serializer.data, json_dumps_params={'indent': 2}, safe=False)
    elif request.method == 'POST':
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if slug:
            try:
                contact = Contact.objects.get(pk=slug)
            except:
                return JsonResponse({'Message':'Failure'}, json_dumps_params={'indent': 2}, safe=False)
            contact.delete()
            return JsonResponse({'Message':'Contact Deleted'}, json_dumps_params={'indent': 2}, safe=False)
        return JsonResponse({'Message':'Failure'}, json_dumps_params={'indent': 2}, safe=False)

@api_view(['GET', 'POST', 'DELETE'])
def journeys(request, slug=None, campaign_id=None):
    if request.method == 'GET':
        return_data = []
        if slug:
            journey = Journey.objects.get(pk=slug)
            serializer = JourneySerializer(journey)
            return_data = serializer.data
        elif campaign_id:
            print(campaign_id)
            journeys = Journey.objects.all().filter(campaign_id=campaign_id)
            serializer = JourneySerializer(journeys, many=True)
            for journey in serializer.data:
                contact = Contact.objects.get(pk=journey['contact_id'])
                contact_serializer = ContactSerializer(contact)
                return_data.append(contact_serializer.data)
        else:
            journeys = Journey.objects.all()
            serializer = JourneySerializer(journeys, many=True)
            return_data = serializer.data
        return JsonResponse(return_data, json_dumps_params={'indent': 2}, safe=False)
    elif request.method == 'POST':
        serializer = JourneySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if slug:
            try:
                journey = Journey.objects.get(pk=slug)
            except:
                return JsonResponse({'Message':'Failure'}, json_dumps_params={'indent': 2}, safe=False)
            journey.delete()
            return JsonResponse({'Message':'Journey Deleted'}, json_dumps_params={'indent': 2}, safe=False)
        return JsonResponse({'Message':'Failure'}, json_dumps_params={'indent': 2}, safe=False)

@api_view(['POST'])
def batches(request):
    try:
        authorization = jwt.decode(request.headers['Authorization'], config('SECRET_KEY'), algorithms=["HS256"])
        authorization['organization_id']
        organization = Organization.objects.get(pk=authorization['organization_id']),
    except:
        return JsonResponse({'Message':'Not Authorized'}, json_dumps_params={'indent': 2}, safe=False, status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'POST':
        req_data = request.data
        created_contacts = []
        updated_contacts = []
        for contact in req_data:
            try:
                contact_obj = Contact.objects.get(unique_id=contact['unique_id'])

                contact_obj.name_first = contact['name_first']
                contact_obj.name_last = contact['name_last']
                contact_obj.email = contact['email']
                contact_obj.phone_number = contact['phone_number']

                updated_contacts.append(contact_obj)
            except:

                contact['organization_id'] = authorization['organization_id']
                created_contacts.append(Contact(
                    name_first = contact['name_first'],
                    name_last = contact['name_last'],
                    email = contact['email'],
                    phone_number = contact['phone_number'],
                    organization_id = Organization.objects.get(pk=contact['organization_id']),
                    unique_id = contact['unique_id']
                ))
        number_of_created_contacts = 0
        if len(created_contacts) > 0:
            number_of_created_contacts = Contact.objects.bulk_create(created_contacts)
        number_of_updated_contacts = 0
        if len(updated_contacts) > 0:
            number_of_updated_contacts = Contact.objects.bulk_update(updated_contacts, ["name_first","name_last","email","phone_number"])
        return JsonResponse({'Message':'Success', 'Created Contacts':len(number_of_created_contacts), 'Updated Contacts':number_of_updated_contacts}, json_dumps_params={'indent': 2}, safe=False)


        #serializer = ContactSerializer(data=req_data, many=True)
        #print(serializer.is_valid())
        return JsonResponse({'Message':'Success'}, json_dumps_params={'indent': 2}, safe=False)

def create_organization(request_data):
    serializer = OrganizationSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save() 
    return serializer.data

def create_user(request_data):
    password = bytes(request_data['password'], 'utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    password = str(hashed)[2:]
    password = str(password)[:-1]

    request_data['password'] = password

    serializer = UserValidatorSerializer(data=request_data)
    if serializer.is_valid():
        serializer.save()
    return serializer.data