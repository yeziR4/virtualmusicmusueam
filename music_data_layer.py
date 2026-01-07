# ============================================
# MUSIC DATA LAYER - Deezer API Integration
# ============================================

import requests
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class MusicItem:
    """Standardized music object"""
    id: str
    title: str
    artist: str
    album: str
    cover_url: str
    cover_blur_url: str
    preview_url: str
    duration: int
    release_date: str
    genre: str
    link: str
    rank: Optional[int] = None
    
    def to_dict(self):
        return asdict(self)


class MusicDataFetcher:
    """Handles all Deezer API calls"""
    
    def __init__(self):
        self.base_url = 'https://api.deezer.com'
        self.session = requests.Session()
    
    def _parse_track(self, track_data: Dict) -> MusicItem:
        """Parse raw Deezer track data into MusicItem"""
        return MusicItem(
            id=str(track_data.get('id', '')),
            title=track_data.get('title', 'Unknown Title'),
            artist=track_data.get('artist', {}).get('name', 'Unknown Artist'),
            album=track_data.get('album', {}).get('title', 'Unknown Album'),
            cover_url=track_data.get('album', {}).get('cover_xl', ''),
            cover_blur_url=track_data.get('album', {}).get('cover_big', ''),
            preview_url=track_data.get('preview', ''),
            duration=track_data.get('duration', 0),
            release_date=track_data.get('release_date', ''),
            genre='Unknown',
            link=track_data.get('link', ''),
            rank=track_data.get('rank', None)
        )
    
    def get_trending_tracks(self, limit: int = 50) -> List[MusicItem]:
        """Get trending/chart tracks"""
        try:
            response = self.session.get(f'{self.base_url}/chart')
            response.raise_for_status()
            data = response.json()
            
            tracks = data.get('tracks', {}).get('data', [])[:limit]
            return [self._parse_track(track) for track in tracks]
        
        except Exception as e:
            print(f"Error fetching trending tracks: {e}")
            return []
    
    def search_tracks(self, query: str, limit: int = 50) -> List[MusicItem]:
        """Search tracks by query"""
        try:
            params = {'q': query, 'limit': limit}
            response = self.session.get(f'{self.base_url}/search', params=params)
            response.raise_for_status()
            data = response.json()
            
            tracks = data.get('data', [])
            return [self._parse_track(track) for track in tracks]
        
        except Exception as e:
            print(f"Error searching tracks: {e}")
            return []
    
    def get_genre_tracks(self, genre_id: int, limit: int = 50) -> List[MusicItem]:
        """Get tracks by genre"""
        try:
            response = self.session.get(f'{self.base_url}/genre/{genre_id}/artists')
            response.raise_for_status()
            data = response.json()
            
            artists = data.get('data', [])[:10]
            all_tracks = []
            
            for artist in artists:
                artist_tracks = self.get_artist_top_tracks(artist['id'], limit=5)
                all_tracks.extend(artist_tracks)
                
                if len(all_tracks) >= limit:
                    break
            
            return all_tracks[:limit]
        
        except Exception as e:
            print(f"Error fetching genre tracks: {e}")
            return []
    
    def get_artist_top_tracks(self, artist_id: int, limit: int = 10) -> List[MusicItem]:
        """Get top tracks from an artist"""
        try:
            response = self.session.get(f'{self.base_url}/artist/{artist_id}/top')
            response.raise_for_status()
            data = response.json()
            
            tracks = data.get('data', [])[:limit]
            return [self._parse_track(track) for track in tracks]
        
        except Exception as e:
            print(f"Error fetching artist tracks: {e}")
            return []
    
    def get_playlist_tracks(self, playlist_id: int, limit: int = 50) -> List[MusicItem]:
        """Get tracks from a playlist"""
        try:
            response = self.session.get(f'{self.base_url}/playlist/{playlist_id}')
            response.raise_for_status()
            data = response.json()
            
            tracks = data.get('tracks', {}).get('data', [])[:limit]
            return [self._parse_track(track) for track in tracks]
        
        except Exception as e:
            print(f"Error fetching playlist tracks: {e}")
            return []
    
    def get_random_discovery(self, count: int = 50) -> List[MusicItem]:
        """Get random tracks for discovery"""
        all_tracks = []
        
        # Mix of trending
        all_tracks.extend(self.get_trending_tracks(limit=20))
        
        # Random genres
        genre_ids = [116, 152, 113, 165, 85]
        random_genre = random.choice(genre_ids)
        all_tracks.extend(self.get_genre_tracks(random_genre, limit=20))
        
        # Random search
        search_terms = ['love', 'night', 'summer', 'dream', 'fire', 'soul', 'dance']
        random_search = random.choice(search_terms)
        all_tracks.extend(self.search_tracks(random_search, limit=10))
        
        random.shuffle(all_tracks)
        return all_tracks[:count]
    
    def get_curated_feed(self, genres: List[int] = None, limit: int = 50) -> List[MusicItem]:
        """Get a curated feed based on genres"""
        if genres is None:
            genres = [116, 152, 85]
        
        all_tracks = []
        tracks_per_genre = limit // len(genres)
        
        for genre_id in genres:
            tracks = self.get_genre_tracks(genre_id, limit=tracks_per_genre)
            all_tracks.extend(tracks)
        
        random.shuffle(all_tracks)
        return all_tracks[:limit]


class MusicMuseumAPI:
    """Main API interface"""
    
    def __init__(self):
        self.fetcher = MusicDataFetcher()
    
    def load_initial_feed(self, mode: str = 'discovery', count: int = 50, **kwargs) -> List[Dict]:
        """Load initial feed"""
        if mode == 'trending':
            tracks = self.fetcher.get_trending_tracks(limit=count)
        elif mode == 'search':
            query = kwargs.get('query', 'music')
            tracks = self.fetcher.search_tracks(query, limit=count)
        elif mode == 'genre':
            genre_id = kwargs.get('genre_id', 116)
            tracks = self.fetcher.get_genre_tracks(genre_id, limit=count)
        elif mode == 'discovery':
            tracks = self.fetcher.get_random_discovery(count=count)
        elif mode == 'curated':
            genres = kwargs.get('genres', [116, 152, 85])
            tracks = self.fetcher.get_curated_feed(genres=genres, limit=count)
        else:
            tracks = self.fetcher.get_random_discovery(count=count)
        
        return [track.to_dict() for track in tracks]
    
    def search(self, query: str, limit: int = 50) -> List[Dict]:
        """Search for tracks"""
        tracks = self.fetcher.search_tracks(query, limit=limit)
        return [track.to_dict() for track in tracks]
    
    def get_by_genre(self, genre: str, limit: int = 50) -> List[Dict]:
        """Get tracks by genre name"""
        genre_map = {
            'pop': 116,
            'rock': 152,
            'dance': 113,
            'rnb': 165,
            'hiphop': 85,
            'rap': 85,
            'jazz': 132,
            'classical': 98,
            'electro': 106,
            'folk': 466,
            'metal': 464,
            'reggae': 144,
            'blues': 153,
            'country': 129,
            'latin': 197,
        }
        
        genre_id = genre_map.get(genre.lower(), 116)
        tracks = self.fetcher.get_genre_tracks(genre_id, limit=limit)
        return [track.to_dict() for track in tracks]
