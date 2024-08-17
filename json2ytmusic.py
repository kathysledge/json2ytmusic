import html
import json
import os
import requests
import string
import time
from ytmusicapi import YTMusic


"""
Utility function
"""
def clean_filename(content):
    characters_to_remove = "/<>:\"\\|?*#"
    translation_table = str.maketrans("", "", characters_to_remove)
    return content.translate(translation_table).replace(" ", "_")


"""
Main script:
> Load JSON and sort albums alphabetically by artist then album.
> Search each album on YouTube Music.
> Download covers.
> Generate HTML.
> Save HTML.
"""
def find_albums_from_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)

    albums = []
    for item in data.get("albums", []):
        artist = item.get("artist").strip()
        album = item.get("album").strip()
        if artist and album:
            albums.append((artist, album))

    albums.sort()

    yt = YTMusic()

    all_results = []
    all_raw_results = []

    print("Searching albums...")
    # Search albums on YouTube Music
    for artist, album in albums:
        album_query = f"{artist}, {album}"
        try:
            search_results = yt.search(album_query, 'albums')
        except:
            print(f"Server timeout searching: {album_query}")
            continue

        # Process search_results
        for result in search_results:
            if result.get("type") == "Album":

                # Extract artist names from the 'artists' array
                artist_names = [artist_obj.get("name") for artist_obj in result.get("artists", [])]

                # Find the largest thumbnail
                largest_thumbnail_url = None
                largest_max_dimension = 0
                for thumbnail in result.get("thumbnails", []):
                    max_dimension = thumbnail["width"]
                    if max_dimension > largest_max_dimension:
                        largest_max_dimension = max_dimension
                        largest_thumbnail_url = thumbnail["url"]

                album_data = {
                    "artists": ", ".join(artist_names),
                    "title": result.get("title"),
                    "url": f"https://music.youtube.com/browse/{result.get("browseId")}",
                    "playlistId": result.get("playlistId"),
                    "year": result.get("year"),
                    "isExplicit": result.get("isExplicit"),
                    "thumbnail": largest_thumbnail_url
                }

                all_results.append((album_query, album_data))
                all_raw_results.append((album_query, search_results))
                break

        time.sleep(0.7)

    all_results_json_string = json.dumps(all_results, indent=2)
    with open("data.json", "w") as outfile:
        outfile.write(all_results_json_string)

    all_raw_results_json_string = json.dumps(all_raw_results, indent=2)
    with open("data_raw.json", "w") as outfile:
        outfile.write(all_raw_results_json_string)

    # HTML templates
    main_html_template = """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Results on YouTube Music</title>
        <style>
          body {
            background-color: black;
            box-sizing: border-box;
            color: white;
            margin: 0;
            padding: 25px;
          }

          .container {
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
              grid-auto-rows: minmax(100px, auto);
              gap: 10px;
          }

          .item {
            background-color: #111;
            border: 1px solid #222;
            border-radius: 7px;
            max-width: 270px;
            padding: 10px;
          }

          .item a:not(.cover-link) {
            color: white;
            text-decoration: none;
            border-bottom: 1px dotted #999;
          }

          .item dl {
            margin: 0;
          }

          .item dl dd {
            margin-inline-start: 0;
          }

          .item dl dt {
            font-size: 80%;
            margin-top: 10px;
            opacity: 0.7;
          }

          .item img {
            max-width: 100%;
            width: 270px;
          }
        </style>
      </head>
      <body>
        <div class="container">

    __ALBUMS_PLACEHOLDER__

        </div>
      </body>
    </html>
    """

    album_html_template = """
          <div class="item">
            <a href="{3}" class="cover-link">
                <img src="covers/{2}" alt="{1}">
            </a>
            <dl>
              <dt>Searched</dt>
              <dd>{0}</dd>
              <dt>Found</dt>
              <dd><a href="{3}">{1}</a></dd>
            </dl>
          </div>
    """

    # Download covers and generate HTML
    directory_path = "./covers"

    print("Creating covers directory...")
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
        except:
            print("Unable to create covers directory.")
            quit()

    print("Downloading covers...")

    albums_html = []

    for album in all_results:

        searched = album[0]

        album_data = album[1]

        artists = album_data.get('artists')
        title = album_data.get('title')
        thumbnail = album_data.get('thumbnail')
        url = album_data.get('url')

        filename = clean_filename(f"{artists} - {title}")
        try:
            r = requests.get(thumbnail, allow_redirects=True)
            open(f"covers/{filename}", 'wb').write(r.content)
        except:
            print(f"Couldn't download cover: {artists} - {title}")

        searched_safe = html.escape(searched)
        full_name_safe = html.escape(f"{artists} - {title}")
        filename_safe = html.escape(filename)
        url_safe = html.escape(url)

        merged_html = album_html_template.format(
            searched_safe,
            full_name_safe,
            filename_safe,
            url_safe
        )

        albums_html.append(merged_html)

    print("Saving HTML...")
    # Save generated HTML
    open("results.html", 'w').write(main_html_template.replace("__ALBUMS_PLACEHOLDER__", "\n".join(albums_html)))

    print("Done. Open results.html in your browser.")


# Assuming YourLibrary.json is in the same directory as this script
find_albums_from_json("YourLibrary.json")
