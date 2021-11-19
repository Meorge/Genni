# Model Repository/Version Control
I'd like to have some basic version control for models. The user should be able to view all of the iterations of a model they've generated and statistics associated with them (e.g. average loss, data set, hyperparameters used for that training) and train new models off of any model in the history.


## Version 1
The initial version is pretty basic:

### Models
- There should be a file `info.json` inside of the repository folder. It contains a key `latest`, which points to the most recent model. The program will use this as the base model to finetune on.
- If there's no `info.json`, then the program assumes this is a fresh repository and creates a new model.
- Every time the model saves, a `config.json` and `steps.csv` file is saved to the folder. The `info.json` is updated to point to this new model.

### Datasets
In addition to containing the models, the repository will also have a folder `datasets`, which in turn will contain a folder for each dataset the user has loaded.

Each folder inside of `datasets` will contain files:
- `aitextgen.tokenizer.json` - holds the token data
- `meta.json` - holds metadata (such as a user-provided title and description)
- `data.txt` - actual dataset text