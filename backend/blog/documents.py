from django.conf import settings
from django.contrib.auth import get_user_model

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models.category import Category
from .models.post import Post

User = get_user_model()


@registry.register_document
class PostDocument(Document):
    """Elasticsearch document for Post model with auto-indexing."""

    # Define searchable fields
    title = fields.TextField(
        attr='title',
        fields={
            'raw': fields.KeywordField(),
        }
    )
    excerpt = fields.TextField(attr='excerpt')
    content = fields.TextField(attr='content')
    slug = fields.KeywordField(attr='slug')

    # Additional fields for filtering
    is_published = fields.BooleanField(attr='is_published')
    is_paid = fields.BooleanField(attr='is_paid')
    price_cents = fields.IntegerField(attr='price_cents')
    published_at = fields.DateField(attr='published_at')
    created_at = fields.DateField(attr='created_at')

    # Author information
    author_id = fields.KeywordField(attr='author_id')
    author_email = fields.KeywordField(attr='author.email')

    # Category information (if exists)
    category_id = fields.IntegerField(attr='category_id')
    category_name = fields.TextField(
        fields={
            'raw': fields.KeywordField(),
        }
    )

    class Index:
        """Elasticsearch index configuration."""

        name = settings.ES_INDEX_POSTS
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'analysis': {
                'analyzer': {
                    'default': {
                        'type': 'standard',
                    },
                }
            },
        }

    class Django:
        """Django model configuration."""

        model = Post
        fields = [
            'id',
        ]
        # Related models that trigger reindexing
        related_models = [Category, User]

    def get_instances_from_related(self, related_instance):
        """If related models are updated, return the instances of this document that need to be updated."""
        if isinstance(related_instance, Category):
            return related_instance.posts.all()
        if isinstance(related_instance, User):
            return related_instance.posts.all()
        return None

    def prepare_category_name(self, instance):
        """Prepare category name safely."""
        return instance.category.name if instance.category else None

    def should_index_object(self, obj):
        """Determine if object should be indexed.

        Only index published posts to keep the search index clean.
        """
        return obj.is_published
