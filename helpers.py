def format_composition(attribute, features):
    if attribute == 'key':
        return format_key(features)
    if attribute == 'tempo':
        return format_tempo(features)
    if attribute == 'signature':
        return format_signature(features)


def format_signature(features):
    return str(features['time_signature']) + "/4"


def format_tempo(features):
    return str(round(features['tempo']))


def format_key(features):
    key = features['key']
    mode = features['mode']
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return keys[key] + ('m' if not mode else '')


def format_value(value):
    return int(value * 100)


def color_from_value(value):
    color_high = [255, 104, 0]
    color_low = [96, 0, 255]
    result = [round((h - l) * value + l) for h, l in zip(color_high, color_low)]
    return f"rgb{tuple(result)}"


def uniform_title(title):
    """Does the best it can to get the actual song title from whatever the name of the track is

    Track names on Spotify are riddled with information on remixes, remasters, features, live versions etc.
    This function tries to remove these, but it might not work in every case, especially in languages other
    than English since it works by looking for keywords
    """
    keywords = ['remaster', 'delux', 'from', 'mix', 'version', 'edit', 'live', 'track', 'session', 'extend', 'feat',
                'studio']
    if not any(keyword in title.lower() for keyword in keywords):
        return title

    newtitle = title
    #  uses split to remove - everything after hyphen if there's a keyword there
    #  (doesn't separate ones without spaces since some titles are like-this)
    if ' - ' in newtitle:
        newtitle = newtitle.split(" - ", 1)
        if any(keyword in newtitle[1].lower() for keyword in keywords):
            newtitle = newtitle[0]

    # removes everything in parentheses if there's a keyword inside
    if '(' in newtitle:
        regex = re.compile(".*?\((.*?)\)")
        result = re.findall(regex, title)
        if len(result) > 0:
            if any(keyword in result[0].lower() for keyword in keywords):
                tag = '(' + result[0] + ')'
                newtitle = newtitle.replace(tag, '')

    newtitle = newtitle.strip()
    return newtitle


def parse_artists(artists):
    """Takes a list of artists and return a nice, comma separated, string, of their, names"""
    result = ''
    comma = False
    for artist in artists:
        if comma:
            result += ', '
        else:
            comma = True
        result += artist['name']
    return result


def remove_embed(text):
    """Removes the weird string from the end of genius results"""
    lyric = text.split('EmbedShare URLCopyEmbedCopy')[0]
    while lyric[-1].isnumeric():
        lyric = lyric[:-1]
    return lyric
