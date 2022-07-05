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
import os.path
from math import floor

import pandas as pd

# A carefully chosen random seed
SEED = 42


def parse_args():
    """
    Reads the command line arguments and returns them

    :return: cmd args
    """
    parser = argparse.ArgumentParser("A script to split a building CSV file into a training and test part")
    parser.add_argument("-s", help="Relative size of the training set compared to the whole dataset", dest="split_ratio", type=float, default=0.8)
    parser.add_argument("input_csv_bz2", help="Buildings CSV file with Bzip2 compression as input")
    return parser.parse_args()


def main():
    """
    Reads the input CSV, performs a random split, and saves the training and test part in two separate files with
    appropriate file name suffixes in the current directory

    :return:
    """
    # Read the data
    args = parse_args()
    data = pd.read_csv(args.input_csv_bz2)
    # Random shuffle of the data
    data = data.sample(frac=1.0, random_state=SEED)
    # Simple way to find the index of the split
    train_split = floor(data.shape[0] * args.split_ratio)
    # Create the two parts for training and test
    train_data, test_data = data[:train_split], data[train_split:]
    # Extract the file prefix based on the file type separator and save the two files in the current directory
    prefix = os.path.basename(args.input_csv_bz2).split(".")[0]
    train_data.to_csv(prefix + "_train.csv.bz2", index=False)
    test_data.to_csv(prefix + "_test.csv.bz2", index=False)


if __name__ == '__main__':
    main()
