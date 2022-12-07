from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    """
    Тестируется, что view-классы используют ожидаемые HTML-шаблоны.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.user_not_author = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs=(
                {'slug': f'{self.post.group.slug}'})): 'posts/group_list.html',
            reverse('posts:profile', kwargs=(
                {'username': f'{self.user}'})): 'posts/profile.html',
            reverse('posts:post_detail', kwargs=(
                {'post_id': f'{self.post.id}'})): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs=(
                {'post_id': f'{self.post.id}'})): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_author_0, 'author')
        self.assertEqual(post_group_0, 'Тестовая группа')

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs=({'slug': f'{self.post.group.slug}'})))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_author_0, 'author')
        self.assertEqual(post_group_0, 'Тестовая группа')

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs=({'username': f'{self.user}'})))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_author_0, 'author')
        self.assertEqual(post_group_0, 'Тестовая группа')

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        first_object = response.context['post']
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_author_0, 'author')
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_group_0, 'Тестовая группа')

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    """Тестируется paginator."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_slug',
            description='test description',
        )
        cls.post_list = []
        for i in range(0, 13):
            cls.post_list.append(
                Post.objects.create(
                    text=f'#{i} Текст тестового поста #{i}',
                    author=cls.user,
                    group=cls.group,
                )
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        TEN_POSTS = 10
        THREE_POSTS = 3
        first_page = {
            reverse('posts:index'): TEN_POSTS,
            (reverse('posts:group_list',
                     kwargs={'slug': self.group.slug})): TEN_POSTS,
            (reverse('posts:profile',
                     kwargs={'username': self.user})): TEN_POSTS,
            (reverse('posts:index') + '?page=2'): THREE_POSTS,
            (reverse('posts:group_list',
                     kwargs={'slug': self.group.slug}) + '?page=2'
             ): THREE_POSTS,
            (reverse('posts:profile',
                     kwargs={'username': self.user}) + '?page=2'
             ): THREE_POSTS,
        }
        for value, expected in first_page.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEqual(
                    len(response.context['page_obj']), expected)
