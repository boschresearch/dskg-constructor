# DSKG Constructor 

The Driving Scene Knowledge Graph Constructor (DSKG Constructor) is an Open Source
Project that support the automated creation of RDF Knowledge Graphs (KG) from 
publicly available autonomous driving datasets (e.g. nuScenes, Pandaset, BDD). 

## Purpose of the project

The DSKG Constructor aims to support the research community to create RDF Knowledge 
Graphs from publicly available autonomous driving dataset for the purpose of  
developing ML/DL architectures and learning models on the knowledge graph for 
various autonomous driving task, e.g. object prediction, motion prediction.

The software is not ready for production use. It has neither been developed nor
tested for a specific use case. However, the license conditions of the
applicable Open Source licenses allow you to adapt the software to your needs.
Before using it in a safety relevant setting, make sure that the software
fulfills your requirements and adjust it according to any applicable safety
standards (e.g. ISO 26262).

## General remarks

The DSKG Constructor aims to support the creation of a Driving Scene KG from 
various publicly available autonomous driving datasets. 

For each supported dataset type, we include all the required python scripts 
along with the respective ontology for that dataset and the documentation 
(README.md) that instructs how to run the script(s) in the respective 
sub-folder. 

Please note that this project provides only the software to construct the
knowledge graphs from the various source datasets. Due to the various licensing 
conditions of the source datasets, we just provide you with the download links 
in the respective README file. 

*The permission to use the dataset is NOT covered by the license of the DSKG 
Constructor. You MUST adhere to the license conditions set by the providers
of the source datasets.*

## License

The DSKG Constructor software is provided under the Apache-2.0 license. See the
[LICENSE](LICENSE) file for details.

For a list of other open source components included, see the
file [3rd-party-licenses.txt](3rd-party-licenses.txt).
