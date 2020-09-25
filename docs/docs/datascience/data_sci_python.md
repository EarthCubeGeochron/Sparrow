---
id: dataSci
title: Introductory Python for Data Science
sidebar_label: Data Science Intro
---

### Metadata Handling and Exporting in Python

This collection of notebooks is designed to guide a programming novice through a basic process of handling metadata collection for geologic samples. We start by fetching data from an API and uploading data from local excel spreadsheets. With that gathered data we then do some dataframe manipulation to un-nest some of the columns. After that, we go over an example of how to use Numpy and Pandas to gather some meaningful statistics about the state of data collection. We also learn how to create dataframes for specific samples, like ones that still need metadata, and we export the pandas dataframes into excel sheets for easy access. We also learn how to do some mapping. The code in these notebooks are bits of code that I wrote and used, with explanations of what the code does and why it is used.

### Bio:

I work for the WiscAr lab at the University of Wisconsin Madison. This code was written as part of an effort to collect metadata for samples proccessed in the lab, and upload them to Sparrow. As part of collecting metadata for samples, I searched through the primary literature for samples as well as reached out to P.I's in labs for missing data. I wrote this code to fetch data from an API and from local excell sheets, and to then perform some basic analysis such as finding percentages of samples with data and those without data, etc. I also used python to generate JSON of samples with new data that could be uploaded to an API. When I began writing this code I was an undergraduate Geoscience major and had **_no_** experience in python or any programming language. Now on top of python, I have taught myself React.js (which uses javascript/typescript, JSX and ES6).

### The Code

If you are new to coding don't worry! There is a plethora of free, online resources that makes learning the basics of python easy and unintimidating. A little bit of time dedication and learning and you'll be up to speed in no time!

I try to explain my code as best I can in the notebooks but I would reccomend becoming familiar with these python libraries:

- [Pandas](https://pandas.pydata.org/)
- [Numpy](https://numpy.org/)
- [JSON](https://www.w3schools.com/whatis/whatis_json.asp) (this isn't a library but its good to be familiar with JSON because it is the main way information is transferred)
  **You can look through the notebooks before hand to see what functions I use from specific libraries and then search for those specifically**

Also become familiar with basic python logic and syntax such as:

- [For loops](https://www.w3schools.com/python/python_for_loops.asp)
- [Data Types](https://realpython.com/python-data-types/) (integers, float, string, boolean, etc)
- [Arrays and Lists](https://www.w3schools.com/python/python_arrays.asp)
- [Dictionaries](https://www.w3schools.com/python/python_dictionaries.asp)

### Jupyter Notebooks

Below are a collection of Jupyter Notebooks as static HTML pages. They go in order as they are listed from top to bottom. It isn't necessary to follow in order, however it may be unclear what dataframes are being referred to if they are looked at out of order. It is suggested to at least skim over all in order and then focus more on the notebooks that contain the most pertinent information for you.

- [Requests and Uploads](/docs/datascience/requestsUploads)
- [Column Splitting](/docs/datascience/columnSplit)
- [Combining and Exporting](/docs/datascience/combine)
- [Basic Data Analytics](/docs/datascience/dataAnalytics)
- [Exporting Meaningful Data](/docs/datascience/export)
- [Mapping with Folium](/docs/datascience/mapping)
