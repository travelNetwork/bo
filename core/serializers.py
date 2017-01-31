from django.conf.urls import url, include
from django.contrib.auth import get_user_model
from rest_framework import serializers, viewsets
from core.models import Review, Location, Category

User = get_user_model()

# Serializers define the API representation.
# class UserSerializer(serializers.Serializer):
#     first_name = serializers.CharField()
#     last_name = serializers.CharField()
#     email = serializers.EmailField()
#
#     def create(self, *args, **kwargs):
#         return  User().save(*args, **kwargs)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'icon')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('longitude', 'latitude')

class ReviewSerializer(serializers.ModelSerializer):
    location = LocationSerializer(many=False,)
    categories = CategorySerializer(many=True)

    class Meta:
        model = Review
        fields = ('id', 'title', 'description', 'privacy', 'location', 'categories')

    def create(self, validated_data):
        #validated_data contains all data from the serializer

        category_list=[]


        #set up created_by attribute with logged user or None
        user = None
        request = self.context['request']
        if request and hasattr(request, "user"):
            user = request.user
            validated_data['created_by'] = user

        # create location manually (DRF doesn't handle nested creation or update)
        location_data = validated_data.pop('location')
        location, _ = Location.objects.get_or_create(**location_data)
        validated_data['location'] = location

        #we remove the category properties
        if 'categories' in validated_data:
            category_list = validated_data.pop('categories')

        #we create the review object
        review = Review.objects.create(**validated_data)

        #we add the category, one by one
        for category in category_list:
            print category['name']
            newCategory, created = Category.objects.get_or_create(name=category['name'])

            if 'icon' in category and category['icon'] is not None:
                newCategory.icon = category['icon']
                newCategory.save()

            review.categories.add(newCategory)


        return review

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.privacy = validated_data.get('privacy', instance.privacy)

        # handle manually location
        location_data = validated_data.pop('location')
        location, _ = Location.objects.get_or_create(**location_data)
        instance.location = location

        instance.save()
        return instance
