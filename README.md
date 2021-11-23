# Genni
**Genni** is an app that attempts to make GPT-2 model training and text generation easy and accessible to everyone. It started out as a basic wrapper around the Python library [aitextgen](https://github.com/minimaxir/aitextgen), but has grown to include a model version control system.

## Current Features
- **Model repositories** keep trained models, datasets, and generated texts all in one place
- **Interactive wizards**
    - **Train models** from a variety of sources
        - From scratch, based only on your dataset
        - From one of OpenAI's publicly available GPT-2 models
        - From a model on [Hugging Face](https://huggingface.co/models)
    - **Generate text**
        - Set Top P, Top K, and seed parameters
        - Compare texts against original datasets to avoid overtraining
- **Watch statistics on a training session in real-time**, including a graph of loss and average loss
    - History for each training session is saved so you can review it whenever you want

## Requirements
### Python 3.9
Genni is being developed and tested with Python 3.9.9. Other versions of Python *may* work, but I can't say for sure.
### PyQt6 and PyQt6-Charts
These libraries can be installed with the terminal command:
```
pip install PyQt6 PyQt6-Charts
```

### Custom fork of aitextgen
To display live training data, a customized version of aitextgen must be used. You can find this version at https://github.com/Meorge/aitextgen/tree/callbacks. Changes are being made to the way aitextgen performs training, so hopefully in the future Genni will migrate to using that instead.

As of right now, this repository should be cloned into a directory named `aitextgen_dev` in the same directory as this file.

### TensorFlow (optional)
If you'd like to use OpenAI GPT-2 models, you will need to have TensorFlow installed. You can install TensorFlow with the terminal command:
```
pip install TensorFlow
```
Note: In my personal experience while developing Genni, I've gotten what seemed like better results from Hugging Face models (such as `EleutherAI/gpt-neo-125M`) than from OpenAI models. Additionally, it seems that having TensorFlow installed causes training initialization to take a bit longer - so it may be better to leave it uninstalled.

### PyQtNotifications (optional, macOS)
If you're running Genni on macOS, you can install PyQtNotifications to receive native macOS notifications for events that might take a while (such as training and generation). Clone the repository at https://github.com/Meorge/PyQtNotifications into a directory named `PyQtNotifications` in the same directory as this file.


## Roadmap/Future Features
- Training
    - Generate samples or save model on demand, in addition to automatically
    - Migrate to main aitextgen repository if/when there is callback support for improved trainer
- Generation
    - Display generation progress (if aitextgen can provide access to it)
    - Compare generated texts against a user-defined word blocklist to prevent inappropriate language
- Datasets
    - Add aggregate datasets (combinations of multiple files)
    - Build datasets based off of Tweets from a given Twitter account