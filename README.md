## GrammatikTAK!
This is my danish grammar assistent project.  
All datasets and bert models are not included due to space limitations.  
This is alle the code for the front- and backend for site: GrammatikTAK.com

### Structure of the current code:
Here is a small overview of the most important directories:  
* DataCreation: A tool for getting data from wikipedia, correct it, and save it.
* DataProcessing: Notebooks for converting text to datasets.
* Use&FineTuneModels: For training BERT models and experimenting with using other models in the main script.
* GoogleAppEngine: (Not used anymore) Google App Engine script to run backend.
* GoogleDocsAddOn: Scripts for the GrammatikTAK Google Docs Add-on
* GoogleExtension: Scripts for the GrammatikTAK Google Extension
* GrammatiktakFlask (outdated) : main.py is the backend currently running on Google Cloud Engine
* GrammatiktakBackend: development of backend 2.0. main.py is the backend. Currently used.
* GrammatiktakTestDatasets: Datasets that have been used specifically to test modules. Accuracy is in the corresponding readme.

### Read more:
- **GrammatiktakBackend: The structure of the backend.**  
- **FineTuneModels: Model development and performance logging**
