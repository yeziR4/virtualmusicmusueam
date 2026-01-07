from flask import Flask, jsonify, request
from flask_cors import CORS
from music_data_layer import MusicMuseumAPI
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the music API
music_api = MusicMuseumAPI()


@app.route('/')
def home():
    """API documentation"""
    return jsonify({
        'message': 'Music Museum API',
        'version': '1.0.0',
        'endpoints': {
            '/api/feed': 'GET - Get initial music feed',
            '/api/search': 'GET - Search tracks (param: q, limit)',
            '/api/genre/<genre>': 'GET - Get tracks by genre (param: limit)',
            '/api/trending': 'GET - Get trending tracks (param: limit)',
            '/api/genres': 'GET - List available genres'
        },
        'docs': 'https://github.com/yourusername/music-museum-api'
    })


@app.route('/api/feed', methods=['GET'])
def get_feed():
    """
    Get initial music feed
    Query params:
        - mode: discovery (default), trending, curated
        - count: number of tracks (default: 50, max: 100)
    """
    try:
        mode = request.args.get('mode', 'discovery')
        count = int(request.args.get('count', 50))
        count = min(count, 100)  # Max 100 tracks
        
        tracks = music_api.load_initial_feed(mode=mode, count=count)
        
        return jsonify({
            'success': True,
            'count': len(tracks),
            'mode': mode,
            'data': tracks
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/search', methods=['GET'])
def search():
    """
    Search for tracks
    Query params:
        - q: search query (required)
        - limit: number of results (default: 50, max: 100)
    """
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter "q" is required'
            }), 400
        
        limit = int(request.args.get('limit', 50))
        limit = min(limit, 100)
        
        tracks = music_api.search(query, limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(tracks),
            'query': query,
            'data': tracks
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/genre/<genre>', methods=['GET'])
def get_genre(genre):
    """
    Get tracks by genre
    Path param: genre (pop, rock, hiphop, jazz, etc.)
    Query param: limit (default: 50, max: 100)
    """
    try:
        limit = int(request.args.get('limit', 50))
        limit = min(limit, 100)
        
        tracks = music_api.get_by_genre(genre, limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(tracks),
            'genre': genre,
            'data': tracks
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/trending', methods=['GET'])
def get_trending():
    """
    Get trending tracks
    Query param: limit (default: 50, max: 100)
    """
    try:
        limit = int(request.args.get('limit', 50))
        limit = min(limit, 100)
        
        tracks = music_api.load_initial_feed(mode='trending', count=limit)
        
        return jsonify({
            'success': True,
            'count': len(tracks),
            'data': tracks
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/genres', methods=['GET'])
def list_genres():
    """List all available genres"""
    genres = {
        'pop': 'Pop music',
        'rock': 'Rock music',
        'hiphop': 'Hip Hop / Rap',
        'jazz': 'Jazz',
        'classical': 'Classical',
        'rnb': 'R&B / Soul',
        'dance': 'Dance / Electronic',
        'electro': 'Electro',
        'folk': 'Folk',
        'metal': 'Metal',
        'reggae': 'Reggae',
        'blues': 'Blues',
        'country': 'Country',
        'latin': 'Latin'
    }
    
    return jsonify({
        'success': True,
        'count': len(genres),
        'data': genres
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'music-museum-api'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
