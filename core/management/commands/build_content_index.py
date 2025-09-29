from django.core.management.base import BaseCommand
from core.recommender.content import build_index

class Command(BaseCommand):
    help = 'Build TF-IDF content index (artifacts in core/recommender/artifacts)'

    def handle(self, *args, **kwargs):
        build_index()
        self.stdout.write(self.style.SUCCESS('Built TF-IDF index.'))