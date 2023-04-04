Collection of notebooks to train and test various models:

## Performance Logging
Performance logging of different models.
### Comma Models
Name | Date | Data | Datasize | Epochs | Batch Size | Scope | Test accuracy | Test F1 
--- | --- | --- | --- | --- | --- | ---
CommaModel8 | 03-04-2023 | EuroParlwithPadding | 2.000.000 | 2 | 32 | 10-10 | % | 
CommaModel7 | 03-04-2023 | EuroParlwithPadding | 2.000.000 | 2 | 32 | 5-5 | % | 
CommaModel6 | 03-04-2023 | TV2withPadding | 1.080.000 | 2 | 32 | 3-3 | **97,43%** | 
CommaModel5 | 03-04-2023 | TV2withPadding | 250.000 | 2 | 32 | 3-3 | 96,69% | 
CommaModel4 | 31-03-2023 | DanaviswithPadding | 1.000.000 | 3 | 32 | 3-3 | 94.19% | 0.83

### Tense Models
Name | Date | Data | Datasize | Epochs | Batch Size | Test accuracy
--- | --- | --- | --- | --- | --- | ---
x | x | x | x | x | x | x

### Notes about training:
- After epoch 2 the validation typically goes up slighty suggestion that the model has already fitted the data pretty good and is already starting to overfit.