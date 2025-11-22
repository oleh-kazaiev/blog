from django.core.cache import cache
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Category model for organizing posts."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        """Meta configuration."""

        ordering = ['name']

    def __str__(self):
        """Return string representation."""
        return self.name

    def save(self, *args, **kwargs):
        """Save category and invalidate cache."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        cache.delete('all_categories_response')

    def delete(self, *args, **kwargs):
        """Delete category and invalidate cache."""
        super().delete(*args, **kwargs)
        cache.delete('all_categories_response')
