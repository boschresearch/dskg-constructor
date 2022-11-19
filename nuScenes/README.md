# Knowledge Graph Generator for the nuScenes Autonomous Driving Dataset 

Please follow the steps below to generate the nuScenes Knowledge Graph:

### 1. Download nuScenes dataset from the nuScenes Web site:

Link: https://www.nuscenes.org/nuscenes#download

Note: 
- You first have to sign up in order to download the dataset
- Please check the terms of use before: https://www.nuscenes.org/terms-of-use

If you want to use the full nuScenes dataset, look for 'Full dataset (v1.0)' and download the 'Trainval' Metadata dataset (approx. 0.43 GB).
Onces downloaded, extract it into a folder on your hard drive. 

### 2. Assuming that you already have downloaded the nuScenes ontology and python script. Install the required libraries:

```python
pip install -r requirements.txt
```
### 3. Run the python script *nuScenesKG.py*:

This script creates an RDF Knowledge Graph for the nuScenes dataset in Turtle format. For the large nuScenes dataset, it will create multiple files that can be concatenated (see step 4).

How to use:
```python
    python nuScenesToRDF.py -f <input-folder> -d <dataset-name> 
```
Example:
```python
    python nuScenesToRDF.py -f 'C:\Data\v1.0-trainval\' -d 'nuscenes_v1.0-trainval'
    python nuScenesToRDF.py -f '.\v1.0-trainval\' -d 'nuscenes_kg'
```

Notes: 
- The input folder is the directory where the nuScenes data are extracted, e.g. C:\Data\v1.0-trainval\
- The dataset-name is the name of the target RDF TTL file(s)

### 4. (OPTIONAL) Run the python script *combineAndGZFiles.py*:

As the name suggests, this script combines and GZIPs the individual Turtle files into a single .ttl.gz file.

How to use:
```python
    python combineAndGZFiles.py -p <path> -f <filter> -t <target-filename-gz> 
```
Example:
```python
    python combineAndGZFiles.py -f 'nuscenes_kg_' -t 'nuscenes_kg.ttl.gz'
    python combineAndGZFiles.py -p 'C:\Data\KG\' -f 'nuscenes_kg_' -t 'nuscenes_kg.ttl.gz'
```

Notes: 
- The path is optional. Default = current directory 
- The filter defines the prefix of the RDF Turtle files to be combined in GZIP'ed (e.g. 'nuscenes_kg_')
- The target filename defines the name of the GZIP file (e.g. 'nuscenes_kg.ttl.gz')

### 5. (OPTIONAL) Load the generated RDF data (KG) into a triple store.