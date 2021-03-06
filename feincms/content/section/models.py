from django import forms
from django.conf import settings as django_settings
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from feincms import settings
from feincms.admin.item_editor import FeinCMSInline
from feincms.contrib.richtext import RichTextField
from feincms.module.medialibrary.fields import MediaFileForeignKey
from feincms.module.medialibrary.models import MediaFile


class SectionContentInline(FeinCMSInline):
    raw_id_fields = ('mediafile',)
    radio_fields = {'type': admin.VERTICAL}


class SectionContent(models.Model):
    """
    Title, media file and rich text fields in one content block.
    """

    feincms_item_editor_inline = SectionContentInline
    feincms_item_editor_context_processors = (
        lambda x: settings.FEINCMS_RICHTEXT_INIT_CONTEXT,
    )
    feincms_item_editor_includes = {
        'head': [settings.FEINCMS_RICHTEXT_INIT_TEMPLATE],
    }

    title = models.CharField(_('title'), max_length=200, blank=True)
    richtext = RichTextField(_('text'), blank=True)
    mediafile = MediaFileForeignKey(MediaFile, verbose_name=_('media file'),
        related_name='+', blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = _('section')
        verbose_name_plural = _('sections')

    @classmethod
    def initialize_type(cls, TYPE_CHOICES=None, cleanse=False):
        if 'feincms.module.medialibrary' not in django_settings.INSTALLED_APPS:
            raise ImproperlyConfigured, 'You have to add \'feincms.module.medialibrary\' to your INSTALLED_APPS before creating a %s' % cls.__name__

        if TYPE_CHOICES is None:
            raise ImproperlyConfigured, 'You need to set TYPE_CHOICES when creating a %s' % cls.__name__

        cls.add_to_class('type', models.CharField(_('type'),
            max_length=10, choices=TYPE_CHOICES,
            default=TYPE_CHOICES[0][0]))

        if cleanse:
            # If cleanse is True use default cleanse method
            if cleanse == True:
                import warnings
                warnings.warn("Please pass a callable instead. cleanse=True is"
                    " being deprecated in favor of explicitly specifying the"
                    " cleansing function. To continue using the same"
                    " functionality, pip install feincms-cleanse and pass"
                    " cleanse=feincms_cleanse.cleanse_html to the"
                    " create_content_type call."
                    " Support for cleanse=True will be removed in FeinCMS v1.8.",
                    DeprecationWarning, stacklevel=2)

                from feincms.utils.html.cleanse import cleanse_html
                cls.cleanse = cleanse_html
            # Otherwise use passed callable
            else:
                cls.cleanse = cleanse

    @classmethod
    def get_queryset(cls, filter_args):
        # Explicitly add nullable FK mediafile to minimize the DB query count
        return cls.objects.select_related('parent', 'mediafile').filter(filter_args)

    def render(self, **kwargs):
        if self.mediafile:
            mediafile_type = self.mediafile.type
        else:
            mediafile_type = 'nomedia'

        return render_to_string([
            'content/section/%s_%s.html' % (self.type, mediafile_type),
            'content/section/%s.html' % self.type,
            'content/section/%s.html' % mediafile_type,
            'content/section/default.html',
            ], {'content': self})

    def save(self, *args, **kwargs):
        if getattr(self, 'cleanse', False):
            try:
                # Passes the rich text content as first argument because
                # the passed callable has been converted into a bound method
                self.richtext = self.cleanse(self.text)
            except TypeError:
                # Call the original callable, does not pass the rich richtext
                # content instance along
                self.richtext = self.cleanse.im_func(self.text)

        super(SectionContent, self).save(*args, **kwargs)
    save.alters_data = True
