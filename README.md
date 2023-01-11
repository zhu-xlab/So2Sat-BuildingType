# So2Sat-BuildingType
A large-scale dataset for building type classification using social media and aerial data

## Dataset

The dataset is split into two parts with different licenses
1. Building data and metadata feature vectors are available at [https://mediatum.ub.tum.de/1662350](https://mediatum.ub.tum.de/1662350)
2. Twitter tweet IDs and Flickr image urls are available at [https://mediatum.ub.tum.de/1662351](https://mediatum.ub.tum.de/1662351)

### Details

- All labeled buildings (`buildings.csv.bz2`) are in part I. It contains information about the 6,950,182 OSM labeled buildings that we are able to identify in the 42 cities. For each building, we share: `osm_building_id`, `class`, `city`, and `geometry` (polygon or multi-polygons coordinates). The geometry column includes WKT strings which contain comas but enclosed with double quotes. When reading the csv with Python libraries such as pandas, it is possible to specify the quote char to circumvent a wrongly imported file. It is possible due to the adjacency of some urban areas that buildings are assigned to multiple places. Please filter according to your task/area specifications.
- Twitter dataset for text classification (`tweets.csv.bz2`) is in part II. It contains the list of 26,666,198 geo-tagged tweets that are collected in the 42 cities and that are assigned to a labeled building. For each tweet, we share: `tweet_id`, `osm_building_id`, `building_class`, `building_city`, `tweet_lang`, `distance_to_building` (in meter), `tweet_creation_time` (in UTC), `tweet_longitude`, and `tweet_latitude`.
- Google aerial images dataset. We do not provide a data file, but we provide the script that we used to download the aerial images from Google in the code repository.
- Flickr images dataset (`flickr.csv.bz2`) is in part II. It contains the list of 26,381 filtered Flickr images that are collected in the 42 cities and that are assigned to a labeled building. For each Flickr image, we share: `image_url`, `image_city`, `building_id`, `building_class`, `distance_to_building (in meter).
- Twitter metadata vectors for the buildings that have more than 5 tweets (`metadata.csv.bz2`) are in part I. It contains the metadata features of the 385,764 buildings that have more than 5 tweets assigned. For each metadata vector, we share: `building_id`, `building_class`, `building_city`, `lng` building centroid longitude, `lat` building centroid latitude, and a list of the 181 feature values.


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
