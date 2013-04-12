from django.core.management.base import BaseCommand
from django_medusa.renderers import StaticSiteRenderer
from django_medusa.utils import get_static_renderers

from optparse import make_option
from django.contrib.sites.models import Site

class Command(BaseCommand):
    args = '<WSGI environ values eg:[SERVER_NAME=www.edmstudio.com wsgi.url_scheme=https] >'
    can_import_settings = True
    option_list = BaseCommand.option_list + (
    make_option('--site-id',
        action='store',
        dest='site-id',
        default=None,
        help='Site id to use while generating.'),
    )

#SERVER_NAME
    help = 'Looks for \'renderers.py\' in each INSTALLED_APP, which defines '\
           'a class for processing one or more URL paths into static files.'
    

    def handle(self, *args, **options):

        if options['site-id']:
            from django.conf import settings
            settings.SITE_ID = int(options['site-id'])
        print "Using", Site.objects.get_current()

        defaults = {}
        defaults['SERVER_NAME'] = Site.objects.get_current().domain
        for arg in args:
            key, value = [s.strip() for s in arg.split("=")]
            defaults[key] = value
        StaticSiteRenderer.initialize_output()

        for Renderer in get_static_renderers():
            r = Renderer()
            r.generate(defaults=defaults)

        StaticSiteRenderer.finalize_output()
