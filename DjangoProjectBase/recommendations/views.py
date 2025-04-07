from django.shortcuts import render
from movie.models import Movie
from .models import Recommendation
import re
from collections import defaultdict

def calculate_relevance(prompt, movie):
    # Palabras clave importantes para diferentes géneros
    genre_keywords = {
        'acción': ['acción', 'pelea', 'lucha', 'batalla', 'guerra', 'explosión', 'arma'],
        'comedia': ['comedia', 'risa', 'divertido', 'gracioso', 'humor'],
        'terror': ['terror', 'miedo', 'suspenso', 'horror', 'escalofriante'],
        'drama': ['drama', 'emocional', 'sentimental', 'historia', 'vida'],
        'romance': ['romance', 'amor', 'pareja', 'relación', 'romántico'],
        'ciencia ficción': ['ciencia ficción', 'futuro', 'espacio', 'tecnología', 'robot', 'alien'],
        'aventura': ['aventura', 'exploración', 'viaje', 'descubrimiento', 'expedición'],
        'fantasía': ['fantasía', 'mágico', 'hechizo', 'dragón', 'mundo mágico'],
    }

    # Convertir todo a minúsculas para la comparación
    prompt = prompt.lower()
    movie_title = movie.title.lower()
    movie_description = movie.description.lower()
    movie_genre = movie.genre.lower()

    # Calcular puntaje base
    score = 0

    # 1. Coincidencia exacta en el título (máxima prioridad)
    if any(word in movie_title for word in prompt.split()):
        score += 5

    # 2. Coincidencia en el género
    for genre, keywords in genre_keywords.items():
        if genre in movie_genre:
            # Si el prompt contiene palabras clave del género
            if any(keyword in prompt for keyword in keywords):
                score += 4

    # 3. Coincidencia en la descripción
    description_words = set(re.findall(r'\w+', movie_description))
    prompt_words = set(re.findall(r'\w+', prompt))
    common_words = description_words.intersection(prompt_words)
    score += len(common_words) * 0.5

    # 4. Palabras clave específicas en la descripción
    for word in prompt.split():
        if word in movie_description:
            score += 1

    return score

def recommend_movie(request):
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '').strip()
        
        if not prompt:
            return render(request, 'recommendations/recommend.html', {
                'error': 'Por favor, ingresa una descripción para buscar películas.'
            })

        # Obtener todas las películas
        movies = Movie.objects.all()
        
        if not movies.exists():
            return render(request, 'recommendations/recommend.html', {
                'error': 'No hay películas disponibles en la base de datos.'
            })

        # Calcular relevancia para cada película
        movie_scores = []
        for movie in movies:
            score = calculate_relevance(prompt, movie)
            if score > 0:  # Solo incluir películas con algún nivel de relevancia
                movie_scores.append((movie, score))

        # Ordenar por puntaje de relevancia
        movie_scores.sort(key=lambda x: x[1], reverse=True)

        if movie_scores:
            recommended_movie = movie_scores[0][0]
            Recommendation.objects.create(
                prompt=prompt,
                recommended_movie=recommended_movie
            )
            return render(request, 'recommendations/result.html', {
                'movie': recommended_movie,
                'prompt': prompt
            })
        else:
            return render(request, 'recommendations/recommend.html', {
                'error': 'No se encontraron películas que coincidan con tu búsqueda. Intenta con otros términos o más específicos.'
            })

    return render(request, 'recommendations/recommend.html')