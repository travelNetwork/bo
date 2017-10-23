from django.conf.urls import url, include
from django.contrib.auth import get_user_model

from itertools import chain
from rest_framework import serializers, viewsets

from core.models import Review, Place, Category, Picture, Status
from friends.models import Friend
from authentication.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ('id', 'name')

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('id', 'name', 'longitude', 'latitude', 'address')

class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ('source', 'caption')

class ReviewSerializer(serializers.ModelSerializer):
    place = PlaceSerializer(many=False, write_only=True)
    status = StatusSerializer(many=False)
    categories = CategorySerializer(many=True)
    pictures = PictureSerializer(many=True)
    created_by = UserSerializer(default=serializers.CurrentUserDefault(), read_only=True)
    user_type = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'short_description', 'information', 'place', 'categories', 'pictures', 'status', 'created_by', 'user_type', 'creation_date')

    def create(self, validated_data):
        category_list=[]

        # create place manually (DRF doesn't handle nested creation or update)
        place_data = validated_data.pop('place')
        place, _ = Place.objects.get_or_create(**place_data)
        validated_data['place'] = place

        # remove the categories properties
        if 'categories' in validated_data:
            category_list = validated_data.pop('categories')

        # remove the pictures properties
        if 'pictures' in validated_data:
            pictures_list = validated_data.pop('pictures')

        # remove the status properties
        if 'status' in validated_data:
            status = validated_data.pop('status')

        #we create the review object
        review = Review.objects.create(**validated_data)

        #we add the category, one by one
        for category in category_list:
            getCategory = Category.objects.get(name=category['name'])
            review.categories.add(getCategory)

        for picture in pictures_list:
            newPicture = Picture.objects.create(**picture)
            review.pictures.add(newPicture)

        getStatus = Status.objects.get(**status)
        review.status = getStatus

        return review

    def update(self, instance, validated_data):
        instance.short_description = validated_data.get('short_description', instance.short_description)
        instance.information = validated_data.get('information', instance.information)

        instance.save()
        return instance

    def get_user_type(self, obj):
        currentUser = self.context['request'].user
        friends = Friend.objects.friends(currentUser)
        friends_friends = list()

        for friend in friends:
            friend_friends = Friend.objects.friends(friend, [currentUser])
            friends_friends = list(chain(friends_friends, friend_friends))

        if (obj.created_by == currentUser):
            return 'me'

        if (obj.created_by in friends):
            return 'friend'

        if (obj.created_by in friends_friends):
            return 'friends_friend'

        return ''


class PlacesSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Place
        fields = ('id', 'name', 'longitude', 'latitude', 'address', 'reviews')
