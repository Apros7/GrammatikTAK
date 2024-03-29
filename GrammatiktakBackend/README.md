## Structure of backend:
The backend is built from the principles of refactoring. It follows the following structure:  
* main.py is the script to run the flask app. It initialize correctors and only has 1 function that runs the sentence through the all the correctors
* Utilities are a collection of function typically used to prepare the sentence in a module and make sure the errors are correct.
* All other directories are modules built to solve a specific kind of error.

## Deployment checklist
1. Set time_tracker.inactive = True.
2. Make sure no input runs on startup.
3. Set save = True in correct_input in index().
4. Run `flask —app main run` and test with webapp to make sure the script runs without errors.

## New modules:
You're a champ for building a new module :sunglasses:!  
When building a module please keep the following in mind:  
* As much of the code as possible should be done in the __init__ function to improve the speed of correction.
* The input sentence is given to all modules as a raw input. Use util function to prepare the way you want. Always return a list of elements. If no errors return a empty list
* Errors should be the Error class: Examples of content:
  * wrong_word (str): "christian"
  * right_word (str): "Christian"
  * indexes (list) (Use util function): [4, 13]
  * description (str): "Christian skal stå med stort, da det er et egenavn." 
* All errors from a module should go into a ErrorList - See [Utilities](https://github.com/Apros7/GrammatikTAK/blob/main/GrammatiktakBackend/Utilities/error_handling.py) for more information

## Before releasing a new module. 
1. Use 'check_if_index_is_correct' to check if your errors are correct
  * This could especially be due to you not using 'move_index_based_on_br'

**To test a relevant csv file (required):**
1. Collect at least 100 sentences to correct in a csvfile (wrong, correct)
2. Test your file with tester in Utilities.
3. Log the accuracy and save the dataset in GrammatiktakTestDataset

**Test your own text (optional):**
1. Implement your module in the main script.  
2. Run "flask --app main run" in this directory.  
3. Open "GrammatiktakWebsite/Handle_errors.js. Change it so that the second line is active, and the third line is commented out.  
4. Go live with "GrammatiktakWebsite" in your browser. When you now press "ret min tekst" this will happen on your device.

## Commen module errors:
Are you using the utilities functions?
* Find index based on sentence.split() index with find_index
* Did you remember to move_index_based_on_br()?
* Did you remember to update concat_errors()?

If this does not fix it, I honestly don't know.  
If you find a commen error, please add it above.  
Good luck :wink:, tihi.
