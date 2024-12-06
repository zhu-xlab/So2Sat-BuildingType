# So2Sat-BuildingType
A large-scale dataset for building type classification using social media and aerial data

## Dataset

### Balancing

In this section the balancing algorithm discussed in section 4.1 in our paper is shown with greater detail.

![balancing algorithm pseudo code](figures/balancing_algorithm.png)

The two figures below depict the distribution of the labeled buildings before (left) and after (right) balancing, where the balancing algorithm down-sample the *residential* and *commercial* classes to meet the number of buildings in the *other* class.

![Class-wise distribution of labeled buildings, (a) before balancing and (b) after balancing](figures/class_dist_for_buildings.png)
![Class-wise distribution of labeled buildings, (a) before balancing and (b) after balancing](figures/class_dist_for_buildings_balanced.png)


### Download

The dataset is split into two parts with different licenses
1. Building data is available at [https://mediatum.ub.tum.de/1662350](https://mediatum.ub.tum.de/1662350) (ODbL)
2. Twitter tweet IDs are available at [https://mediatum.ub.tum.de/1662351](https://mediatum.ub.tum.de/1662351) (CC BY-NC-SA)

### Details

- All labeled buildings (`buildings.csv.bz2`) are in part I. It contains information about the 6,950,182 OSM labeled buildings that we are able to identify in the 42 cities. For each building, we share: `osm_building_id`, `class`, `city`, and `geometry` (polygon or multi-polygons coordinates). The geometry column includes WKT strings which contain comas but enclosed with double quotes. When reading the csv with Python libraries such as pandas, it is possible to specify the quote char to circumvent a wrongly imported file. It is possible due to the adjacency of some urban areas that buildings are assigned to multiple places. Please filter according to your task/area specifications.
- Twitter dataset for text classification (`tweets.csv.bz2`) is in part II. It contains the list of 26,666,198 geo-tagged tweets that are collected in the 42 cities and that are assigned to a labeled building. For each tweet, we share: `tweet_id`, `osm_building_id`, `building_class`, `building_city`, `tweet_lang`, `distance_to_building` (in meter), `tweet_creation_time` (in UTC), `tweet_longitude`, and `tweet_latitude`.
- Google aerial images dataset. We do not provide a data file, but we provide the script that we used to download the aerial images from Google in the code repository.


## Code

- ``download_building_aerial_images.py`` yields the corresponding aerial images for each building
- ``undersample.py`` performs two-dimensional undersampling as described in the paper
- ``split_train_test.py`` splits the imbalanced and balanced buildings.csv.bz2 into a training and test part

## Appendix of the paper
In this section we provide subsequent statistics and baseline results achieved with our proposed dataset.

### Additional Dataset Statistics

#### Twitter
In this subsection we provide additional information about the Twitter modality. The table below shows the word count under
consideration of the α value.

| $\alpha$   | Number of unique words |
| :--------: | -----------------:     |
| 41         | 36,058                 |
| 12         | 24,151                 |
| 9          | 21,519                 | 
| 6          | 18,006                 | 
| 4          | 14,647                 |
| 3          | 12,741                 |
| 2          | 10,429                 |
| 1          | 6,978                  |

*Number of unique words in the textual corpus for each value of α, where α refers to the maximum number of
tweets to consider per building*

The next table gives statistics about the distribution of tweets per building.

|              | min   | max       | median | mean   | variance   | sd      |
| :--------    | :---: | :---:     | :---:  | :---:  |  :---:     | :---:   |
| Commercial   |  1    | 584,296   |  4     | 66.99  | 4,975,237  | 2230.52 |
| Residential  |  1    | 134,995   |  1     | 10.57  | 81,421.64  | 285.34  |
| Other        |  1    | 1,541,532 |  4     | 133.49 | 39,229,660 | 6263.36 | 
| All          |  1    | 1,541,532 |  2     | 40.69  | 6,513,908  | 2552.24 | 

*The minimum, maximum, median, mean average, variance, and standard deviation for the number of tweets per
building. “All” refers to all buildings of all classes*

The following table depicts the main statistics about the number of tweets per building for: 0, 1, 2, 5, 10, 15, 20 and 25% excluding rate. Addionally, the table shows that by excluding more outlier values, we obtain more homogeneous dataset reflected through lower variance and standard deviation values:


| Data share (#buildings)      | min   | max       | median    | mean       | variance   | sd      |
| :--------                    | :---: | :---:     | :---:     | :---:      |  :---:     | :---:   |
| 0% (655,425)                 | 1     | 1,541,532 | 2         | 40.69 (41) | 6,513,908  | 2552.24 |
| 1% (642,316)                 | 1     | 426       | 2         | 11.95 (12) | 1377.23    | 37.11   |
| 2% (629,208)                 | 1     | 207       | 2         | 9.14 (9)   | 535.29     | 23.14   |
| 5% (589,882)                 | 1     | 71        | 2         | 5.77 (6)   | 113.76     | 10.67   |
| 10% (524,340)                | 1     | 27        | 2         | 3.72 (4)   | 24.45      | 4.94    |
| 15% (458,798)                | 1     | 14        | 2         | 2.79 (3)   | 7.93       | 2.82    | 
| 20% (393,255)                | 1     | 8         | 2         | 2.27 (2)   | 3.13       | 1.77    |
| 25% (327,712)                | 1     | 5         | 2         | 1.94 (1)   | 1.40       | 1.18    |

*The minimum, maximum, median, mean average, variance, and standard deviation for the number of tweets per
building. In the last case, we put* α *= 1 instead of 2 to differentiate it from the previous case.*







## Citation

Available at _TBA_

BibTeX:
```commandline
insert_paper_bibtex_here
```
