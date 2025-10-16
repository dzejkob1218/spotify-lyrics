from config import *
# TODO: undo functions for all these functions

def fav(sp, track_uri):
    """Add track to Favorites, Star, and Legacy playlists, then remove from Processing"""
    if not track_uri:
        print("ERROR: No track loaded")
        return

    print(f"FAV - Up Arrow - {track_uri}")
    try:
        # Add to Favorites, Star, and Legacy playlists
        if FAV_ID:
            sp.playlist_add_items(FAV_ID, [track_uri])
            print(f"  Added to Favorites")
        if STAR_ID:
            sp.playlist_add_items(STAR_ID, [track_uri])
            print(f"  Added to Star")
        if LEGACY_ID:
            sp.playlist_add_items(LEGACY_ID, [track_uri])
            print(f"  Added to Legacy")

        # Remove from Processing playlist
        if PROCESSING_ID:
            sp.playlist_remove_all_occurrences_of_items(PROCESSING_ID, [track_uri])
            print(f"  Removed from Processing")

        print("FAV complete!")
    except Exception as e:
        print(f"ERROR in fav(): {e}")


def keep(sp, track_uri):
    """Add track to Star and Legacy playlists, then remove from Processing"""
    if not track_uri:
        print("ERROR: No track loaded")
        return

    print(f"KEEP - Right Arrow - {track_uri}")
    try:
        # Add to Star and Legacy playlists
        if STAR_ID:
            sp.playlist_add_items(STAR_ID, [track_uri])
            print(f"  Added to Star")
        if LEGACY_ID:
            sp.playlist_add_items(LEGACY_ID, [track_uri])
            print(f"  Added to Legacy")

        # Remove from Processing playlist
        if PROCESSING_ID:
            sp.playlist_remove_all_occurrences_of_items(PROCESSING_ID, [track_uri])
            print(f"  Removed from Processing")

        print("KEEP complete!")
    except Exception as e:
        print(f"ERROR in keep(): {e}")


def delete(sp, track_uri):
    """Remove track from Processing playlist"""
    if not track_uri:
        print("ERROR: No track loaded")
        return

    print(f"DELETE - Down Arrow - {track_uri}")
    try:
        # Remove from Processing playlist
        if PROCESSING_ID:
            sp.playlist_remove_all_occurrences_of_items(PROCESSING_ID, [track_uri])
            print(f"  Removed from Processing")

        print("DELETE complete!")
    except Exception as e:
        print(f"ERROR in delete(): {e}")


def skip(sp, track_uri):
    """Skip the current track - don't perform any Spotify actions"""
    print(f"SKIP - Left Arrow - {track_uri if track_uri else 'No track loaded'}")
    print("SKIP complete (no Spotify actions performed)")
