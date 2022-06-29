"""
MIT License

Copyright (c) 2022 Eike Jens Hoffmann [eike.jens.hoffmann [at] tum.de]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import argparse
import bz2
import csv
import logging
import os
import random
import time
from io import BytesIO
from itertools import product

import mercantile
import numpy as np
import requests
from PIL import Image
from rasterio import transform
from shapely.wkt import loads
from tqdm import tqdm

# Base URL for Google Maps tile server
BASE_URL = "https://mt1.google.com/vt"


def parse_args():
    """
    Parsing of commandline arguments. All come with a predefined value to use it right away
    :return: the parsed commandline arguments with sensible defaults
    """
    parser = argparse.ArgumentParser(
        description="Script to download Google aerial images for So2Sat BuildingType dataset")
    parser.add_argument("-c", dest="tiles_cache_dir", help="Cache directory for downloaded tiles", default="/tmp/tile_cache")
    parser.add_argument("-i", dest="input_file", help="buildings.csv.bz2 file from So2Sat BuildingType dataset ", default="./part1/buildings.csv.bz2")
    parser.add_argument("-o", dest="output_image_dir", help="Directory ", default="./aerial-images")
    parser.add_argument("-s", dest="img_size", default=256, type=int)
    parser.add_argument("-v", dest="verbose", action="store_true")
    parser.add_argument("-z", dest="zoom_level", default=18, type=int)
    return parser.parse_args()


def process_buildings_from_file(file_name, tiles_cache_dir, output_image_dir, zoom_level, out_img_size,
                                make_dirs=True, has_header=True):
    """
    Core method that iterates over the buildings.csv.bz2 and retrieves the aerial images for each building. It works
    with a caching directory that stores all downloaded tiles to prevent downloading the same tile multiple times. If an
    image file is already present, it will be skipped to make it fail-safe.
    :param file_name: the input CSV file containing building_ids, labels, and geometries
    :param tiles_cache_dir: the cache directory that stores all downloaded tiles
    :param output_image_dir: the output directory where to place all building images
    :param zoom_level: the zoom level of the tiles, experiments showed that 18 works best for building function
    classification
    :param out_img_size: width and height of the aerial building images, 256 has proven to work best
    :param make_dirs: create all directories if not existing, default is yes
    :param has_header: the input CSv file has a header in the first row, which should be skipped, default is yes
    :return:
    """
    # Different operators to work with raw and compressed CSV files
    open_func, params = (bz2.open, ["rt"]) if file_name.endswith("bz2") else (open, [])
    with open_func(file_name, *params) as in_file:
        # Iterate over file
        reader = csv.reader(in_file, delimiter=",", quotechar='"')
        for idx, cols in tqdm(enumerate(reader)):
            # Skip the header if present
            if has_header and idx == 0:
                continue
            # Assuming the column order from buildings.csv.bz2
            building_id, building_label, building_geometry = cols[0], cols[1], loads(cols[-1])
            building_centroid = building_geometry.centroid
            logging.debug("Processing ID {}".format(building_id))
            # Check if aerial image for building is already present
            out_img_path = os.path.join(output_image_dir, f"aerial-{zoom_level}", building_label, f"{building_id}.png")
            if os.path.isfile(out_img_path):
                logging.debug("Found existing file at {}".format(out_img_path))
                continue
            # Make sure that all directories are present and create them if necessary
            path = os.path.dirname(out_img_path)
            if make_dirs:
                if not os.path.exists(path):
                    os.makedirs(path)
                if not os.path.exists(tiles_cache_dir):
                    os.makedirs(tiles_cache_dir)
            # Make two attempts to create the image: one with the directly adjacent tiles and a second one with the
            # second rank neighbor tiles (if necessary)
            try:
                img = extract_view(building_centroid, tiles_cache_dir, zoom_level, out_img_size)
            except ValueError:
                try:
                    img = extract_view(building_centroid, tiles_cache_dir, zoom_level, out_img_size, surrounding=2)
                except ValueError:
                    logging.warning("Could not extract building {} in second try, giving up".format(building_id))
                    continue
            except FileNotFoundError as e:
                logging.warning(e)
                continue
            # Convert the numpy array to an Pillow object and save it
            img = Image.fromarray(img, mode="RGB")
            img.save(out_img_path)
            logging.debug("Wrote file to {}".format(out_img_path))
    logging.info("Done.")


def extract_view(building_centroid, tiles_dir, zoom_level, out_img_size, in_tile_size=256, surrounding=1):
    """
    Creates an aerial image for a location specified with a center point. The method raises a ValueError if the expected
    area is not covered by the surrounding tiles. Can be caught to do redo the operation with a higher surrounding
    :param building_centroid: the location at which the resulting aerial image is centered on
    :param tiles_dir: the cache directory of tiles
    :param zoom_level: the zoom level for which the aerial image is created
    :param out_img_size: width and height of the resulting aerial image as _ONE_ parameter for quadratically images
    :param in_tile_size: the size of the input tiles, usually 256 for normal tile services (default), but can be 512 for
     HD tiles
    :param surrounding: the number of adjacent tiles to be taken into account recursively, e.g., 1 are all tiles which
    are directly next to the center tile, 2 are all tiles next to all 1 tiles, and so on
    :return: a numpy image representing the aerial image focused on point
    """
    # Calculate the tile containing the building centroid
    tile = mercantile.tile(building_centroid.x, building_centroid.y, zoom_level)
    # Calculate the adjacent tiles including the center tile
    tiles = [mercantile.Tile(tile.x + x, tile.y + y, zoom_level) for x, y in
             product(range(-surrounding, surrounding + 1), repeat=2)]
    # Download all calculated tiles
    download_tiles(tiles, tiles_dir)
    # Create a big patch from all tiles
    img = stich_tiles(tiles, tiles_dir, in_tile_size)
    # Calculate the geo reference for the big patch
    transformation = calc_transform(tiles, img)
    # Calculate the pixel position of the centroid in the big patch
    xs, ys = transform.rowcol(transformation, building_centroid.x, building_centroid.y)
    # Calculate the mask for cutting
    x_start = xs - out_img_size // 2
    y_start = ys - out_img_size // 2
    x_end = xs + out_img_size // 2
    y_end = ys + out_img_size // 2
    # For stability issues: making sure not to get index errors if one pixel is out of stiched image
    # (happens in rare cases)
    if x_start < 0 or y_start < 0 or x_end >= img.shape[0] or y_end >= img.shape[1]:
        raise ValueError("Stiched image was not big enough")
    # Cut the final building patch
    img = img[x_start:x_end, y_start:y_end, :]
    return img


def download_tiles(tiles, out_dir):
    """
    Download a list of tiles
    :param tiles: a list of tiles
    :param out_dir: the output directory
    :return:
    """
    for t in tiles:
        file_path = get_file_path(out_dir, t)
        if os.path.isfile(file_path):
            continue
        download_tile(t, file_path)


def download_tile(tile, file_path, mean_sleep_time=1.0, std_sleep_time=0.5):
    """
    Download one tile and save it to a given path. A kind downloader does not send as many requests as possible to the
    server but instead waits a moment between two requests. The waiting time is drawn from a Gaussian distribution based
    on the given parameters. Raises a FileNotFoundError when the tile is not available
    :param tile: the tile to be downloaded
    :param file_path: file path of the download
    :param mean_sleep_time: mean of waiting time
    :param std_sleep_time: standard deviation of waiting time
    :return:
    """
    params = {"lyrs": "s", "x": tile.x, "y": tile.y, "z": tile.z}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img.save(file_path)
        time.sleep(abs(random.gauss(mean_sleep_time, std_sleep_time)))
    else:
        raise FileNotFoundError("No image for tile {}, got code {}".format(tile, response.status_code))


def stich_tiles(tiles, tiles_dir, tile_size):
    """
    Loads a list of neighboring tiles and puts them together to a big image patch
    :param tiles: a list of tiles covering an area
    :param tiles_dir: the directory containing the tiles
    :param tile_size: size of a single tile
    :return: a big image patch from all tiles
    """
    # Calculate the offsets
    num_tiles_x = len(set([t.x for t in tiles]))
    num_tiles_y = len(set([t.y for t in tiles]))
    x_offset = min([t.x for t in tiles])
    y_offset = min([t.y for t in tiles])
    # Create an empty canvas
    img_template = np.zeros((num_tiles_y * tile_size, num_tiles_x * tile_size, 3), dtype=np.uint8)
    # Fill the canvas
    for t in tiles:
        # Load the tile
        tile_file_path = get_file_path(tiles_dir, t)
        img = Image.open(tile_file_path)
        img = np.array(img)
        if img is None:
            logging.warning("Tile {} not available".format(tile_file_path))
            continue
        # Calculate the where to put the tile in canvas
        x_start = (t.x - x_offset) * tile_size
        x_end = x_start + tile_size
        y_start = (t.y - y_offset) * tile_size
        y_end = y_start + tile_size
        # Fill it in
        img_template[y_start:y_end, x_start:x_end, :] = img
    # Return the filled canvas
    return img_template


def calc_transform(tiles, img):
    """
    Calculates the transformation matrix from pixel coordinates to WGS84 geo-coordinates
    :param tiles: a list of tiles covering an area
    :param img: the image patch from all tiles
    :return: a transformation matrix
    """
    bounds = [mercantile.bounds(t) for t in tiles]
    west = min([b.west for b in bounds])
    south = min([b.south for b in bounds])
    east = max([b.east for b in bounds])
    north = max([b.north for b in bounds])
    out_transform = transform.from_bounds(west, south, east, north, img.shape[0], img.shape[1])
    return out_transform


def get_file_path(base_dir, tile):
    """
    A simple method to unify the way tile objects are mapped to file paths. Does not check if file exists!
    :param base_dir: the directory containing all tiles, i.e., the caching directory
    :param tile: a tile object
    :return: the file path where the file should be stored
    """
    file_name = "{}-{}-{}.png".format(tile.x, tile.y, tile.z)
    file_path = os.path.join(base_dir, file_name)
    return file_path


def main():
    """
    Get the command line arguments, set up the logging, and start the download process
    :return:
    """
    args = parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format='%(asctime)s %(message)s', level=level)

    process_buildings_from_file(args.input_file, args.tiles_cache_dir, args.output_image_dir, args.zoom_level,
                                args.img_size)


if __name__ == '__main__':
    main()
