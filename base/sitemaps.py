from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from django.contrib.sites.models import Site
from django.conf import settings

class StaticViewSitemap(Sitemap):
    def items(self):
        return ['aboutPage', 'login', 'dashboard']
    
    def location(self, item):
        return reverse(item)
    
#doesnt work, gets an extra http://http://127.0.0.1:800