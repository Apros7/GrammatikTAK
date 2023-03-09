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

### Structure of backend:
The backend is built from the principles of refactoring. It follows the following structure:  
* main.py is the script to run the flask app. It initialize correctors and only has 1 function that runs the sentence through the all the correctors
* Utilities are a collection of function typically used to prepare the sentence in a module and make sure the errors are correct.
* All other directories are modules built to solve a specific kind of error.

### New modules:
You're a champ for building a new module :sunglasses:!  
When building a module please keep the following in mind:  
* As much of the code as possible should be done in the __init__ function to improve the speed of correction.
* The input sentence is given to all modules as a raw input. Use util function to prepare the way you want. Always return a list of elements. If no errors return a empty list
* Errors should be a list with the following elements in this order (with examples):
  * wrong_word (str): "christian"
  * right_word (str): "Christian"
  * indexes (list) (Use util function): [4, 13]
  * description (str): "Christian skal stå med stort, da det er et egenavn."
  
  
### Commen module errors:
Are you using the utilities functions?
* Find index based on sentence.split() index with find_index
* Did you remember to move_index_based_on_br()?
* Did you remember to update concat_errors()?

If this does not fix it, I honestly doesn't know.  
If you find a commen error, please add it above.  
Good luck :wink:, tihi.
