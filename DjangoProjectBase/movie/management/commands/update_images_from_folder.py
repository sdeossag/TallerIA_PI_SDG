import os
from django.core.management.base import BaseCommand
from django.conf import settings
from movie.models import Movie

class Command(BaseCommand):
    help = 'Actualiza las imágenes de las películas desde la carpeta media/movie/images/'

    def handle(self, *args, **kwargs):
        images_folder = os.path.join(settings.MEDIA_ROOT, 'movie', 'images')

        if not os.path.exists(images_folder):
            self.stdout.write(self.style.ERROR(f'La carpeta {images_folder} no existe.'))
            return

        updated_count = 0

        for movie in Movie.objects.all():
            sanitized_title = movie.title.replace(" ", "_")  # Reemplaza espacios con guiones bajos si es necesario
            possible_filenames = [
                f"m_{movie.title}.png",  # Intenta con el título original
                f"m_{sanitized_title}.png",  # Intenta con espacios reemplazados
            ]

            image_path = None
            for filename in possible_filenames:
                potential_path = os.path.join(images_folder, filename)
                if os.path.exists(potential_path):
                    image_path = potential_path
                    break

            if image_path:
                movie.image = os.path.relpath(image_path, settings.MEDIA_ROOT).replace("\\", "/")
                movie.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Imagen actualizada para: {movie.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'No se encontró imagen para: {movie.title}'))

        self.stdout.write(self.style.SUCCESS(f'Total de imágenes actualizadas: {updated_count}'))

