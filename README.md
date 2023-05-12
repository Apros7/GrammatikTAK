<div align="center">

# GrammatikTAK!

</div>

## What is GrammatikTAK?

Working on becoming the best grammar assistant for nordic languages. With a combination of NLP, AI and Linguists, this erpo has been developed.

This currently only corrects danish text at **GrammatikTAK.com.** Models and datasets are not included in this repo.

## Why?
The rise in NLP and AI has greatly affected popular languages, their respective grammar assistants and NLP work. The nordic, especially danish, are sadly way behind. This repo is hopefully going to help cover some basic NLP needs and make a great danish, an potential nordic, grammar assistant.

## Design principles
**GrammatikTAK** is:

- **Simple**: Build in modules, a module can easily be replaced, reworked or even deleted without affecting other modules.
- **Adaptable**: Although speed is important, we focus on adaptability and readability over speed.
- **Well-tested**: Every module is well-tested to secure a high accuracy.


## Directories:

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