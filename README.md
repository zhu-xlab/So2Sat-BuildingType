# So2Sat-BuildingType
A large-scale dataset for building type classification using social media and aerial data

## Dataset

The dataset is split into two parts with different licenses
1. Building data and metadata feature vectors are available at [https://mediatum.ub.tum.de/1662350](https://mediatum.ub.tum.de/1662350)
2. Twitter tweet IDs and Flickr image urls are available at [https://mediatum.ub.tum.de/1662351](https://mediatum.ub.tum.de/1662351)

## Code

- ``download_building_aerial_images.py`` yields the corresponding aerial images for each building
- ``undersample.py`` performs two-dimensional undersampling as described in the paper
- ``split_train_test.py`` splits the imbalanced and balanced buildings.csv.bz2 into a training and test part

## Paper

Available at _TBA_

BibTeX:
```commandline
insert_bibtex_here
```
