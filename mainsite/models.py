from time import time

from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import reverse
from utils import slugify


def gen_post_slug(slug):
    new_slug = slugify(slug)
    return new_slug + '.' + str(int(time()))

class Account(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    age = models.IntegerField(blank=True, null=True)
    groups = models.ManyToManyField('Group', related_name='owners', blank=True)
    views = models.CharField(max_length=40, blank=True)
    photo = models.ImageField(verbose_name=u'Аватарка', default='profile_logo.png', upload_to='users/%Y/%m/%d/', blank=True)

    def get_absolute_url(self):
        return reverse('profile', kwargs={'pk': self.pk})

    def __str__(self):
        return self.user.username

class Group(models.Model):
    name = models.CharField(max_length=150, db_index=True, verbose_name=u'Название')
    slug = models.SlugField(max_length=160, unique=True, null=True, verbose_name=u'URL')
    description = models.TextField(verbose_name='Описание', blank=True, db_index=True)
    photo = models.ImageField(verbose_name=u'Фото группы', default='group_logo.jpg', upload_to='groups/%Y/%m/%d/', blank=True)
    date_create = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Профсоюз"
        ordering = ["-date_create"]
    
    def get_absolute_url(self):
        return reverse('group_info', kwargs={'slug': self.slug})
    def get_update_url(self): # don't django func, only i use this func!
        return reverse('group_update', kwargs={'slug': self.slug})
    def get_delete_url(self):
        return reverse('group_delete', kwargs={'slug': self.slug})
    def save(self, *args, **kwarg):
        super().save(*args, **kwarg)
        if not self.slug: # self.id
            self.slug = 'g' + str(self.pk)
            super().save(*args, **kwarg)
    def __str__(self):
        return self.name

class Tag(models.Model):
    title = models.CharField(max_length=40)
    slug = models.SlugField(max_length=50, unique=True)
    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwarg):
        print(self.title)
        print(slugify(self.title))
        self.slug = slugify(self.title)
        super().save(*args, **kwarg)

    def __str__(self):
        return self.title

class Post(models.Model):
    title = models.CharField(max_length=150, db_index=True, verbose_name=u'Заголовок')
    author = models.ForeignKey('Account', on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=160, unique=True)
    body = models.TextField(blank=True, db_index=True, verbose_name=u'Содержание')
    tags = models.ManyToManyField('Tag', related_name='posts', blank=True, verbose_name=u'Тэги')
    date_pub = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.group.slug, 'postslug': self.slug})

    def save(self, *args, **kwarg):
        if not self.pk: # self.id
            self.slug = gen_post_slug(self.title)
        super().save(*args, **kwarg)

    def __str__(self):
        return self.title
    class Meta:
        ordering = ["-date_pub"]
