Collection of notebooks to train and test various models:

## Performance Logging
Performance logging of different models.
### Comma Models
Model | Date | Data | Datasize | Epochs | Batch | Lr | WDecay | Scope | Test accuracy | Test F1 
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
9 | 05-04-2023 | EuroParl | 4.000.000 | 1 | 16 | 1e-5 | 1e-4 | 5-5 | **98.09%** | **0.931**
8 | 04-04-2023 | EuroParl | 2.000.000 | 2 | 32 | 1e-5 | 0 | 10-10 | 97.41% | 0.905
7 | 04-04-2023 | EuroParl | 2.000.000 | 2 | 32 | 1e-5 | 0 | 5-5 | 97.64% | 0.915
6 | 03-04-2023 | TV2 | 1.080.000 | 2 | 32 | 1e-5 | 0 | 3-3 | 97,43% | x
5 | 03-04-2023 | TV2 | 250.000 | 2 | 32 | 1e-5 | 0 | 3-3 | 96,69% | x
4 | 31-03-2023 | Danavis | 1.000.000 | 3 | 32 | 1e-5 | 0 | 3-3 | 94.19% | 0.83

### Nutids-r Models
Model | Date | Datasize | Epochs | Batch | Lr | Scope | Test correct | Test wrong | Time (113 sentences)
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
1-Bert | 04-04-2023 | 80.000 | 2 | 16 | 1e-5 | 4-4 | **74.47%** | 02.66% | 30 sec
3-Electra | 04-04-2023 | 80.000 | 2 | 16 | 1e-5 | 4-4 | 48.4% | **0%** | 24 sec
1-Bert | 04-04-2023 | 80.000 | 2 | 16 | 1e-5 | 4-4 | **74.47%** | 02.66% | 30 sec

### Notes about training:
- After epoch 2 the validation loss typically goes up slighty suggestion that the model has already fitted the data pretty good and is already starting to overfit.
- We tried making a tense model to check for nutids-r, but a hard-coded checker seems to work much better.

### Road to 99% Comma Model
- Remember to change max_length in tokenization and potentially experiment with even more data
- Multiple epochs?
- Maybe another structure? Full sentences as input?
