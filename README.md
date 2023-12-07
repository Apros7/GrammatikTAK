<div align="center">
<br><br>
<img src="LogoText.png" alt="Logo">
<br><br>
</div>

## What is GrammatikTAK?

Project to use a combination of NLP, AI and Linguists to make danish grammar assistant.

This currently only corrects danish text at [**GrammatikTAK.com.**](https://www.grammatiktak.com) Models and datasets are not included in this repo.

## How to see what this repo is capable of:

The backend is no longer hosted. You can run this locally and change the code of the [website](https://github.com/Apros7/Apros7.github.io) to point to your locally hosted backend.

The backend uses trained models. To use the backend without the models change the first line in GrammatiktakBackend/main.py to ```use_models = False``` then ```cd GrammatiktakBackend``` and host with ```flask --app main run```

This project could definitely be better documented. If you need any assistance, what to go through the project or want my datasets/models to further experiment, feel free to contact me.

## Why?
The rise in NLP and AI has greatly affected popular languages, their respective grammar assistants and NLP work. The nordic, especially danish, are sadly way behind. This repo is hopefully going to help cover some basic NLP needs and make a great danish, an potential nordic, grammar assistant.

## Design principles
I focus on making **GrammatikTAK**:

- **Simple**: Build in [modules](https://github.com/Apros7/GrammatikTAK/tree/main/GrammatiktakBackend), a module can easily be replaced, reworked or even deleted without affecting other modules.
- **Adaptable**: Although speed is important, I have focused on adaptability and readability over speed.
- **Well-tested**: I have tried to do [extensive testing](https://github.com/Apros7/GrammatikTAK/tree/main/FineTuneModels) to my models to secure a high accuracy.


## Directories:

Here is a small overview of the most important directories:

* BackendAssistants: Scripts for analysing the backend performance & complexity.
* DataProcessing: Scripts & notebooks for converting text to datasets.
* FineTuneModels: Scripts for finetuning models and logging performance
* GoogleDocsAddOn: Scripts for the GrammatikTAK Google Docs Add-on
* GoogleExtension: Scripts for the GrammatikTAK Google Extension (not finished)
* GrammatiktakBackend: development of backend 2.0. main.py is the backend. Currently used.
* Other: Powerpoints
* TestingOtherModels: Scripts for testing models from other people to use or compare with.
