Collection of notebooks to train and test various models:

## Performance Logging
Performance logging of different models.
### Comma Models
Model | Date | Data | Datasize | Epochs | Batch | Lr | Weight | Scope | Test accuracy | Test F1 
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
9 | 05-04-2023 | EuroParl | 4.000.000 | 1 | 16 | 1e-5 | 1e-4 | 5-5 | 98.09% | 0.931
8 | 04-04-2023 | EuroParl | 2.000.000 | 2 | 32 | 1e-5 | 0 | 10-10 | 97.41% | 0.905
7 | 04-04-2023 | EuroParl | 2.000.000 | 2 | 32 | 1e-5 | 0 | 5-5 | **97.64%** | **0.915**
6 | 03-04-2023 | TV2 | 1.080.000 | 2 | 32 | 1e-5 | 0 | 3-3 | 97,43% | x
5 | 03-04-2023 | TV2 | 250.000 | 2 | 32 | 1e-5 | 0 | 3-3 | 96,69% | x
4 | 31-03-2023 | Danavis | 1.000.000 | 3 | 32 | 1e-5 | 0 | 3-3 | 94.19% | 0.83

### Tense Models
Name | Date | Data | Datasize | Epochs | Batch Size | Test accuracy
--- | --- | --- | --- | --- | --- | ---
x | x | x | x | x | x | x

### Notes about training:
- After epoch 2 the validation typically goes up slighty suggestion that the model has already fitted the data pretty good and is already starting to overfit.
- Remember to change max_length in tokenization and potentially experiment with even more data
