from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

# Create your models here.

# class travelUser(models.Model):
#     me =
#     friends = models.ManyToManyField(travelUser)

class Category(models.Model):
    name = models.CharField(max_length=200)
    icon = models.URLField(max_length=200, blank=True, null=True)


class Location(models.Model):
    longitude = models.FloatField(blank=False, null=False, default=0)
    latitude = models.FloatField(blank=False, null=False, default=0)


    def __unicode__(self):
        return u"%i - %i" % (self.longitude, self.latitude)

class PersonalManager(models.Manager):
    def query_set(self):
        return super(PersonalManager, self).get_queryset().filter(privacy = 100)

class FriendsManager(models.Manager):
    def query_set(self):
        return super(PersonalManager, self).get_queryset().filter(privacy = 50)

class AllManager(models.Manager):
    def query_set(self):
        return super(PersonalManager, self).get_queryset().filter(privacy = 0)


class Review(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=100, blank=True)
    location = models.ForeignKey('Location')
    categories = models.ManyToManyField('Category')
    privacy = models.IntegerField(default=50)
    # image = models.ImageField(upload_to = "images")


    #the who fields
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='first_reviewer')
    creation_date = models.DateField(auto_now_add=True)

    objects = models.Manager()
    personal_review = PersonalManager()
    friends_review = FriendsManager()
    all_review = AllManager()

    def __unicode__(self):
            return self.title


# nimporte quoi ^^

#different manager in each case

#different class of review
class PersonalReview(Review):
    objects = PersonalManager()
    class Meta:
        proxy = True

class FriendsReview(Review):
    objects = FriendsManager()
    class Meta:
        proxy = True

class AllReview(Review):
    objects = AllManager()
    class Meta:
        proxy = True
