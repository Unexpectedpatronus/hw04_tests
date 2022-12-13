from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.user_not_author = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='test description'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            pub_date='Тестовая дата',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': f'{self.user.username}'}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                pub_date=self.post.pub_date,
                author=self.user,
                group=self.group,
            ).exists()
        )

    def test_title_label(self):
        text_label = PostFormTests.form.fields['text'].label
        self.assertEqual(text_label, 'Текст поста')

    def test_title_help_text(self):
        text_help_text = PostFormTests.form.fields['text'].help_text
        self.assertEqual(text_help_text, 'Введите текст поста')

    def test_edit_post_unauthorized(self):
        """Неавторизованный пользователь хочет отредактировать пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk
        }
        response = self.guest_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.pk}/edit/')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                pub_date=self.post.pub_date,
                author=self.user,
                group=self.group,
            ).exists()
        )

    def test_create_post_unauthorized(self):
        """Неавторизованный пользователь хочет создать пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post_not_author(self):
        """Юзер хочет отредактировать чужой пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk
        }
        response = self.authorized_client_not_author.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, f'/posts/{self.post.pk}/')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=self.post.text,
                pub_date=self.post.pub_date,
                author=self.user,
                group=self.group,
            ).exists()
        )

    def test_edit_post_author(self):
        """Автор хочет отредактировать свой пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, f'/posts/{self.post.pk}/'
        )
        self.assertEqual(Post.objects.count(), posts_count)
