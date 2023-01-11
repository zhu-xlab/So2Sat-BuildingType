# So2Sat-BuildingType
A large-scale dataset for building type classification using social media and aerial data

## Dataset

The dataset is split into two parts with different licenses
1. Building data and metadata feature vectors are available at [https://mediatum.ub.tum.de/1662350](https://mediatum.ub.tum.de/1662350)
2. Twitter tweet IDs and Flickr image urls are available at [https://mediatum.ub.tum.de/1662351](https://mediatum.ub.tum.de/1662351)

### Details

- All labeled buildings (`buildings.csv.bz2`}) are in part I. It contains information about the \num{6950182} OSM labeled buildings that we are able to identify in the \num{42} cities. For each building, we share: \texttt{osm\_building\_id}, \texttt{class}, \texttt{city}, and \texttt{geometry} (polygon or multi-polygons coordinates). The geometry column includes WKT strings which contain comas but enclosed with double quotes. %When reading the csv with Python libraries such as pandas, it is possible to specify the quote char to circumvent a wrongly imported file. It is possible due to the adjacency of some urban areas that buildings are assigned to multiple places. Please filter according to your task/area specifications.
    - Twitter dataset for text classification (\texttt{tweets.csv.bz2}) is in part II. It contains the list of \num{26666198} geo-tagged tweets that are collected in the \num{42} cities and that are assigned to a labeled building. For each tweet, we share: \texttt{tweet\_id}, \texttt{osm\_building\_id}, \texttt{building\_class}, \texttt{building\_city}, \texttt{tweet\_lang}, \texttt{distance\_to\_building} (in meter), \texttt{tweet\_creation\_time} (in UTC), \texttt{tweet\_longitude}, and \texttt{tweet\_latitude}.
    - Google aerial images dataset. We do not provide a data file, but we provide the script that we used to download the aerial images from Google in the code repository.
    - Flickr images dataset (\texttt{flickr.csv.bz2}) is in part II. It contains the list of \num{26381} filtered Flickr images that are collected in the \num{42} cities and that are assigned to a labeled building. For each Flickr image, we share: \texttt{image\_url}, \texttt{image\_city}, \texttt{building\_id}, \texttt{building\_class}, \texttt{distance\_to\_building} (in meter).
    - Twitter metadata vectors for the buildings that have more than 5 tweets (\texttt{metadata.csv.bz2}) are in part I. It contains the metadata features of the \num{385764} buildings that have more than 5 tweets assigned. For each metadata vector, we share: \texttt{building\_id}, \texttt{building\_class}, \texttt{building\_city}, \texttt{lng} building centroid longitude, \texttt{lat} building centroid latitude, and a list of the \num{181} feature values.


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
