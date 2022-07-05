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
import logging
from itertools import product

import pandas as pd
from tqdm import tqdm

# A carefully chosen random seed
SEED = 42


def parse_args():
    """
    Reads the command line arguments and returns them

    :return: cmd args
    """
    parser = argparse.ArgumentParser("Two dimensional downsampling on city and class level")
    parser.add_argument("input_csv_bz2", help="Imbalanced buildings CSV file with Bzip2 compression as input")
    parser.add_argument("output_csv_bz2", help="Balanced buildings CSV file with Bzip2 compression as output")
    return parser.parse_args()


def calc_num_samples_per_city_and_class(data):
    """
    Calculates the number of building samples per class and city as well as the desired number of building samples per
    class and city. This number is defined as the

    :param data: a Pandas dataframe read from the input buildings CSV file
    :return: 1. a list of all city names, 2. a list of all classes, 3. the designated number of
    """
    # Count the number of cities and classes
    class_count = data.groupby("class").nunique()
    city_count = data.groupby("city").nunique()
    logging.debug(f"Found {city_count} cities")
    # Get the class with the lowest number of building samples
    min_class, min_samples = class_count["building_id"].idxmin(),  class_count["building_id"].min()
    # Calculate the desired number of samples per city and class
    num_samples_per_city = min_samples // city_count.shape[0]
    logging.debug(f"Class {min_class} has least support with {min_samples} samples")
    return city_count.index.tolist(), class_count.index.tolist(), num_samples_per_city


def random_city_split(data, city, clazz, desired_num_samples_per_city_and_class):
    """
    Tries to obtain the desired number of building samples from the given data for a specified city and class. If
    samples are missing, they will be reported as a number. If more samples are available, they are returned in a
    separate list

    :param data: a Pandas dataframe read from the input buildings CSV file
    :param city: one of the cities out of the list of cities
    :param clazz: one of the classes out of the list of classes
    :param desired_num_samples_per_city_and_class: the ideal number of samples per class and city
    :return: 1. a random sample of buildings from the given data, might be smaller than the ideal number of samples if
    there is no sufficient data
    2. unused samples of cities and class, which can be used for backfilling. None if there is no sufficient data
    3. number of samples missing for the city and the class
    """
    # Select the subset for city and class
    city_class_subset = data[data["city"] == city]
    city_class_subset = city_class_subset[city_class_subset["class"] == clazz]
    # Perform random shuffling
    city_class_subset = city_class_subset.sample(frac=1.0, random_state=SEED)
    num_city_class_samples = city_class_subset.shape[0]
    # Return the results
    if num_city_class_samples < desired_num_samples_per_city_and_class:
        missing_items = desired_num_samples_per_city_and_class - num_city_class_samples
        return city_class_subset, None, missing_items
    elif num_city_class_samples > desired_num_samples_per_city_and_class:
        return city_class_subset[:desired_num_samples_per_city_and_class], \
               city_class_subset[desired_num_samples_per_city_and_class:], \
               0
    else:
        return city_class_subset, None, 0


def main():
    """
    This is where all parts of the code come together and the main procedure happens
    :return:
    """
    # Read the command line arguments
    args = parse_args()
    # Read the buildings.csv.bz2
    logging.info(f"Reading {args.input_csv_bz2} ...")
    data = pd.read_csv(args.input_csv_bz2)
    logging.info(f"Read {args.input_csv_bz2} with {data.shape[0]:,} buildings")
    # Make sure that each building is only once in the dataset
    data.drop_duplicates(subset="building_id", inplace=True)
    logging.info(f"Deduplication yielded {data.shape[0]:,} buildings")
    # Calculate the statistics including the desired number of samples per city and class
    cities, classes, num_samples_per_city = calc_num_samples_per_city_and_class(data)
    logging.info(f"Need {num_samples_per_city:,} samples per city and class")
    # Initialize the dataset
    dataset = []
    excess_list = {cls: [] for cls in classes}
    missing_numbers = {cls: 0 for cls in classes}
    # Perform the initial balancing by iterating over all cities and classes
    for city, cls in tqdm(product(cities, classes), total=len(cities) * len(classes)):
        sub_data, excess, missing = random_city_split(data, city, cls, num_samples_per_city)
        dataset.append(sub_data)
        if excess is not None:
            excess_list[cls].append(excess)
        missing_numbers[cls] += missing
    # Backfill with data from excess lists
    for cls in classes:
        excess = pd.concat(excess_list[cls], axis=0)
        dataset.append(excess.sample(n=missing_numbers[cls], random_state=SEED))
    # Put the final balanced dataset together and write it to a file
    dataset = pd.concat(dataset, axis=0)
    logging.info(f"Balanced dataset {args.output_csv_bz2} has {dataset.shape[0]:,} rows")
    dataset.to_csv(args.output_csv_bz2, index=False)
    # print(dataset)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    main()
