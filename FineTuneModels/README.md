Collection of notebooks to train and test various models:

# Performance Logging
Performance logging of different models.
## Comma Models
Model | Date | Data | Datasize | Epochs | Batch | Lr | WDecay | Scope | Test accuracy | Test F1 
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
Distil2 | 28-09-2023 | EuroParl | 46.000.000 | 2 | 32 | 2e-5 | 0 | 15-5 | 98.82% | Unknown
Distil1 | 24-09-2023 | EuroParl | 25.000.000 | 2 | 32 | 2e-5 | 0 | 15-5 | 98.51% | Unknown
10 | 25-05-2023 | EuroParl | 6.900.000 | 2 | 32 | 2e-5 | 1e-2 | 15-10 | **98.99%** | Unknown
9 | 05-04-2023 | EuroParl | 4.000.000 | 1 | 16 | 1e-5 | 1e-4 | 5-5 | 98.09% | **0.931**
8 | 04-04-2023 | EuroParl | 2.000.000 | 2 | 32 | 1e-5 | 0 | 10-10 | 97.41% | 0.905
7 | 04-04-2023 | EuroParl | 2.000.000 | 2 | 32 | 1e-5 | 0 | 5-5 | 97.64% | 0.915
6 | 03-04-2023 | TV2 | 1.080.000 | 2 | 32 | 1e-5 | 0 | 3-3 | 97,43% | x
5 | 03-04-2023 | TV2 | 250.000 | 2 | 32 | 1e-5 | 0 | 3-3 | 96,69% | x
4 | 31-03-2023 | Danavis | 1.000.000 | 3 | 32 | 1e-5 | 0 | 3-3 | 94.19% | 0.83

### Notes about training:
- After epoch 2 the validation loss typically goes up slighty suggestion that the model has already fitted the data pretty good and is already starting to overfit.
- Max data avaliable is 6.9 mil. A potential data collection funnel could be created to gather more data and thereby increasing accuracy.
- About 0.7% increase in accuracy with epoch 2, 0.05% increase with epoch 3, and decrease in accuracy with >3 epochs.
- DistilBERT is 2.3 times as fast as BERT.

## Nutids-r Models
Model | Date | Datasize | Epochs | Batch | Lr | Scope | Test correct | Test wrong | Test F1 | Cutoff
--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---
10-Bert | 07-06-2023 | 2.100.000 | 2 | 32 | 2e-5 | 15-5 | 96.12% | 00.41% |  0.98897 | 0.95
9-Bert | 25-05-2023 | 1.100.000 | 3 | 32 | 2e-5 | 15-5 | **96.62%** | 00.46% | **0.990** | 0.95
9-Bert | 25-05-2023 | 1.100.000 | 3 | 32 | 2e-5 | 15-5 | 98.87% | 01.13% | **0.990** | 0
5-Bert | 04-04-2023 | 200.000 | 4 | 16 | 1e-5 | 5-5 | 75.53% | 02.66% | Unknown | 0.95
4-Bert | 04-04-2023 | 200.000 | 2 | 16 | 1e-5 | 5-5 | 75.53% | 02.66% | Unknown | 0.95
3-Electra | 04-04-2023 | 80.000 | 2 | 16 | 1e-5 | 5-5 | 48.4% | **0%** | Unknown | 0.95
1-Bert | 04-04-2023 | 80.000 | 2 | 16 | 1e-5 | 5-5 | 74.47% | 02.66% | Unknown | 0.95
SimpleNN | 07-06-2023 | 2.6 mil | 10 | 64 | 2e-6 | 15-5 | 97.56% | ___ | ___ | 0 

### Notes about training:
- The data used is EuroParlNutidsr-trainset_verbs.
- Training on POS and not the words. I have not been able to make it work with just words.
- Hard coded to:
  - not guess if comma or "og" right before.
  - guess "infinitiv" if "at" right before.
- Hard coded improved accuracy with ~.3%. Ideally these should be deleted for later models.
- SimpleNN in pytorch: can't seem to get above 97.5%
- Model 11 had all data manually cleaned before testing, hence the same dataset size as model 10, but better performance.
