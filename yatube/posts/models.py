from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
POST_STR_LENGTH: int = 15


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts',

    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        related_name='posts',
        help_text='Группа, к которой будет относиться пост',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.text[:POST_STR_LENGTH]
