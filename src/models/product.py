"""
Module contenant les modèles liés aux produits musicaux.

Ce module définit les classes pour les artistes, albums, genres, types de média et pistes.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from .base import BaseModel

class MediaType(BaseModel):
    """
    Modèle représentant un type de média (MP3, AAC, etc.).
    
    Attributs:
        media_type_id: Identifiant unique du type de média
        name: Nom du type de média (ex: "MPEG audio file")
    """
    
    _table_name = 'MediaType'
    _primary_key = 'MediaTypeId'
    _fields = {
        'media_type_id': int,  # MediaTypeId
        'name': str           # Name
    }
    
    def __init__(self, **kwargs):
        # Renommage des clés pour correspondre aux noms d'attributs Python
        mapping = {
            'MediaTypeId': 'media_type_id',
            'Name': 'name'
        }
        
        # Transformation des clés
        transformed_kwargs = {}
        for key, value in kwargs.items():
            if key in mapping:
                transformed_kwargs[mapping[key]] = value
            else:
                transformed_kwargs[key] = value
        
        super().__init__(**transformed_kwargs)
    
    def __str__(self) -> str:
        """Représentation en chaîne du type de média."""
        return self.name or f"MediaType {self.media_type_id}"


class Genre(BaseModel):
    """
    Modèle représentant un genre musical.
    
    Attributs:
        genre_id: Identifiant unique du genre
        name: Nom du genre (ex: "Rock", "Jazz")
    """
    
    _table_name = 'Genre'
    _primary_key = 'GenreId'
    _fields = {
        'genre_id': int,  # GenreId
        'name': str      # Name
    }
    
    def __init__(self, **kwargs):
        # Renommage des clés pour correspondre aux noms d'attributs Python
        mapping = {
            'GenreId': 'genre_id',
            'Name': 'name'
        }
        
        # Transformation des clés
        transformed_kwargs = {}
        for key, value in kwargs.items():
            if key in mapping:
                transformed_kwargs[mapping[key]] = value
            else:
                transformed_kwargs[key] = value
        
        super().__init__(**transformed_kwargs)
    
    def get_tracks(self) -> List['Track']:
        """
        Récupère toutes les pistes de ce genre.
        
        Returns:
            Liste des pistes de ce genre
        """
        # À implémenter avec un service ou un repository
        return []
    
    def get_album_count(self) -> int:
        """
        Compte le nombre d'albums différents dans ce genre.
        
        Returns:
            Nombre d'albums
        """
        # À implémenter avec une requête SQL ou un service
        return 0
    
    def __str__(self) -> str:
        """Représentation en chaîne du genre."""
        return self.name or f"Genre {self.genre_id}"


class Artist(BaseModel):
    """
    Modèle représentant un artiste.
    
    Attributs:
        artist_id: Identifiant unique de l'artiste
        name: Nom de l'artiste
    """
    
    _table_name = 'Artist'
    _primary_key = 'ArtistId'
    _fields = {
        'artist_id': int,  # ArtistId
        'name': str       # Name
    }
    
    def __init__(self, **kwargs):
        # Renommage des clés pour correspondre aux noms d'attributs Python
        mapping = {
            'ArtistId': 'artist_id',
            'Name': 'name'
        }
        
        # Transformation des clés
        transformed_kwargs = {}
        for key, value in kwargs.items():
            if key in mapping:
                transformed_kwargs[mapping[key]] = value
            else:
                transformed_kwargs[key] = value
        
        super().__init__(**transformed_kwargs)
        self._albums = None
    
    def get_albums(self, force_refresh: bool = False) -> List['Album']:
        """
        Récupère les albums de cet artiste.
        
        Args:
            force_refresh: Si True, force le rechargement depuis la base de données
            
        Returns:
            Liste des albums de l'artiste
        """
        if self._albums is None or force_refresh:
            # À implémenter avec un service ou un repository
            # Exemple: self._albums = artist_service.get_artist_albums(self.artist_id)
            self._albums = []
        
        return self._albums
    
    def get_tracks(self) -> List['Track']:
        """
        Récupère toutes les pistes de cet artiste.
        
        Returns:
            Liste des pistes de l'artiste
        """
        # À implémenter avec un service ou un repository
        return []
    
    def get_genres(self) -> List[Genre]:
        """
        Récupère les genres musicaux associés à cet artiste.
        
        Returns:
            Liste des genres de l'artiste
        """
        # À implémenter avec une requête SQL ou un service
        return []
    
    def get_top_tracks(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les pistes les plus populaires de l'artiste.
        
        Args:
            limit: Nombre maximum de pistes à retourner
            
        Returns:
            Liste des pistes avec leurs statistiques de vente
        """
        # À implémenter avec une requête SQL ou un service
        return []
    
    def __str__(self) -> str:
        """Représentation en chaîne de l'artiste."""
        return self.name or f"Artist {self.artist_id}"


class Album(BaseModel):
    """
    Modèle représentant un album musical.
    
    Attributs:
        album_id: Identifiant unique de l'album
        title: Titre de l'album
        artist_id: Identifiant de l'artiste
    """
    
    _table_name = 'Album'
    _primary_key = 'AlbumId'
    _fields = {
        'album_id': int,   # AlbumId
        'title': str,      # Title
        'artist_id': int   # ArtistId
    }
    
    def __init__(self, **kwargs):
        # Renommage des clés pour correspondre aux noms d'attributs Python
        mapping = {
            'AlbumId': 'album_id',
            'Title': 'title',
            'ArtistId': 'artist_id'
        }
        
        # Transformation des clés
        transformed_kwargs = {}
        for key, value in kwargs.items():
            if key in mapping:
                transformed_kwargs[mapping[key]] = value
            else:
                transformed_kwargs[key] = value
        
        super().__init__(**transformed_kwargs)
        self._artist = None
        self._tracks = None
    
    def get_artist(self) -> Optional[Artist]:
        """
        Récupère l'artiste de l'album.
        
        Returns:
            L'artiste de l'album ou None si non trouvé
        """
        if self._artist is None and hasattr(self, 'artist_id'):
            # À implémenter avec un service ou un repository
            # Exemple: self._artist = artist_service.get_artist(self.artist_id)
            pass
        
        return self._artist
    
    def get_tracks(self, force_refresh: bool = False) -> List['Track']:
        """
        Récupère les pistes de l'album.
        
        Args:
            force_refresh: Si True, force le rechargement depuis la base de données
            
        Returns:
            Liste des pistes de l'album
        """
        if self._tracks is None or force_refresh:
            # À implémenter avec un service ou un repository
            # Exemple: self._tracks = album_service.get_album_tracks(self.album_id)
            self._tracks = []
        
        return self._tracks
    
    def get_genres(self) -> List[Genre]:
        """
        Récupère les genres musicaux de l'album.
        
        Returns:
            Liste des genres de l'album
        """
        # À implémenter avec une requête SQL ou un service
        return []
    
    def get_duration(self) -> int:
        """
        Calcule la durée totale de l'album en millisecondes.
        
        Returns:
            Durée totale en millisecondes
        """
        tracks = self.get_tracks()
        return sum(track.milliseconds for track in tracks if hasattr(track, 'milliseconds'))
    
    def get_duration_formatted(self) -> str:
        """
        Retourne la durée totale de l'album au format MM:SS.
        
        Returns:
            Chaîne formatée de la durée
        """
        total_seconds = self.get_duration() // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def __str__(self) -> str:
        """Représentation en chaîne de l'album."""
        artist = self.get_artist()
        artist_name = artist.name if artist else "Artiste inconnu"
        return f"{self.title} - {artist_name}"


class Track(BaseModel):
    """
    Modèle représentant une piste musicale.
    
    Attributs:
        track_id: Identifiant unique de la piste
        name: Nom de la piste
        album_id: Identifiant de l'album
        media_type_id: Identifiant du type de média
        genre_id: Identifiant du genre (optionnel)
        composer: Compositeur (optionnel)
        milliseconds: Durée en millisecondes
        bytes: Taille en octets (optionnel)
        unit_price: Prix unitaire
    """
    
    _table_name = 'Track'
    _primary_key = 'TrackId'
    _fields = {
        'track_id': int,       # TrackId
        'name': str,          # Name
        'album_id': int,      # AlbumId
        'media_type_id': int, # MediaTypeId
        'genre_id': int,      # GenreId (optionnel)
        'composer': str,      # Composer (optionnel)
        'milliseconds': int,  # Milliseconds
        'bytes': int,         # Bytes (optionnel)
        'unit_price': float   # UnitPrice
    }
    
    def __init__(self, **kwargs):
        # Renommage des clés pour correspondre aux noms d'attributs Python
        mapping = {
            'TrackId': 'track_id',
            'Name': 'name',
            'AlbumId': 'album_id',
            'MediaTypeId': 'media_type_id',
            'GenreId': 'genre_id',
            'Composer': 'composer',
            'Milliseconds': 'milliseconds',
            'Bytes': 'bytes',
            'UnitPrice': 'unit_price'
        }
        
        # Transformation des clés
        transformed_kwargs = {}
        for key, value in kwargs.items():
            if key in mapping:
                transformed_kwargs[mapping[key]] = value
            else:
                transformed_kwargs[key] = value
        
        super().__init__(**transformed_kwargs)
        self._album = None
        self._genre = None
        self._media_type = None
    
    def get_album(self) -> Optional[Album]:
        """
        Récupère l'album de la piste.
        
        Returns:
            L'album de la piste ou None si non trouvé
        """
        if self._album is None and hasattr(self, 'album_id'):
            # À implémenter avec un service ou un repository
            # Exemple: self._album = album_service.get_album(self.album_id)
            pass
        
        return self._album
    
    def get_genre(self) -> Optional[Genre]:
        """
        Récupère le genre de la piste.
        
        Returns:
            Le genre de la piste ou None si non trouvé
        """
        if self._genre is None and hasattr(self, 'genre_id') and self.genre_id:
            # À implémenter avec un service ou un repository
            # Exemple: self._genre = genre_service.get_genre(self.genre_id)
            pass
        
        return self._genre
    
    def get_media_type(self) -> Optional[MediaType]:
        """
        Récupère le type de média de la piste.
        
        Returns:
            Le type de média de la piste ou None si non trouvé
        """
        if self._media_type is None and hasattr(self, 'media_type_id'):
            # À implémenter avec un service ou un repository
            # Exemple: self._media_type = media_type_service.get_media_type(self.media_type_id)
            pass
        
        return self._media_type
    
    def get_duration_formatted(self) -> str:
        """
        Retourne la durée de la piste au format MM:SS.
        
        Returns:
            Chaîne formatée de la durée
        """
        if not hasattr(self, 'milliseconds'):
            return "00:00"
            
        total_seconds = self.milliseconds // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_formatted_size(self) -> str:
        """
        Retourne la taille du fichier dans un format lisible.
        
        Returns:
            Chaîne formatée de la taille (ex: "3.5 MB")
        """
        if not hasattr(self, 'bytes') or not self.bytes:
            return "0 B"
            
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.bytes < 1024.0:
                if unit == 'B':
                    return f"{int(self.bytes)} {unit}"
                return f"{self.bytes:.1f} {unit}"
            self.bytes /= 1024.0
        
        return f"{self.bytes:.1f} TB"
    
    def get_artist(self) -> Optional[Artist]:
        """
        Récupère l'artiste de la piste via l'album.
        
        Returns:
            L'artiste de la piste ou None si non trouvé
        """
        album = self.get_album()
        if album:
            return album.get_artist()
        return None
    
    def __str__(self) -> str:
        """Représentation en chaîne de la piste."""
        artist = self.get_artist()
        artist_name = artist.name if artist else "Artiste inconnu"
        return f"{self.name} - {artist_name}"
