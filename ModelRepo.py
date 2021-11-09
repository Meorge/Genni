
from typing import List

from os.path import join, isdir, exists
from os import listdir
from json import load
from datetime import datetime, timedelta
from csv import reader

def getDurationString(passed: timedelta):
    hours, rem = divmod(passed.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    passedStr = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    return passedStr

def getRepoMetadata(repoName: str) -> dict:
    infoFilePath = join(repoName, 'info.json')

    repoMetadata: dict = {}
    if exists(infoFilePath):
        with open(infoFilePath) as f:
            repoMetadata = load(f)

    return repoMetadata

def getModelsInRepository(repoName: str) -> List[dict]:
    allModelsFolder = join(repoName, 'models')
    allPotentialModels = listdir(allModelsFolder)

    validModels = []
    for dir in allPotentialModels:
        configPath = join(allModelsFolder, dir, 'config.json')
        metaPath = join(allModelsFolder, dir, 'meta.json')
        modelBinPath = join(allModelsFolder, dir, 'pytorch_model.bin')

        if exists(configPath) and exists(metaPath) and exists(modelBinPath):
            with open(metaPath) as f:
                data = load(f)
                data['filePath'] = dir
                validModels.append(data)

    validModels.sort(key=lambda i: datetime.fromisoformat(i.get('datetime', '1970-01-01T00:00:00')), reverse=True)
    return validModels

def getDatasetsInRepository(repoName: str) -> List[dict]:
    allDatasetsFolder = join(repoName, 'datasets')
    allPotentialDatasets = listdir(allDatasetsFolder)

    validDatasets = []
    for dir in allPotentialDatasets:
        datasetPath = join(allDatasetsFolder, dir, 'dataset')
        metaPath = join(allDatasetsFolder, dir, 'meta.json')
        tokenizerPath = join(allDatasetsFolder, dir, 'aitextgen.tokenizer.json')

        if exists(datasetPath) and exists(metaPath) and exists(tokenizerPath):
            with open(metaPath) as f: meta = load(f)
            validDatasets.append({
                'pathName': dir,
                'meta': meta
            })
            
    validDatasets.sort(key=lambda i: i['meta']['imported'], reverse=True)
    return validDatasets

def getGeneratedTextsInRepository(repoName: str) -> List[dict]:
    allGensFolder = join(repoName, 'generated')
    allPotentialGens = listdir(allGensFolder)

    validGens = []
    for dir in allPotentialGens:
        metaPath = join(allGensFolder, dir, 'meta.json')
        textsPath = join(allGensFolder, dir, 'texts.json')

        if exists(metaPath) and exists(textsPath):
            with open(metaPath) as f: meta = load(f)
            with open(textsPath) as f: texts = load(f)
            validGens.append({
                'texts': textsPath,
                'meta': meta
            })

    validGens.sort(key=lambda i: i['meta']['datetime'], reverse=True)
    return validGens
    
def getDatasetMetadata(repoName: str, datasetName: str) -> dict:
    allDatasets = getDatasetsInRepository(repoName)
    try:
        thisDataset = [i for i in allDatasets if i['pathName'] == datasetName][0]
        return thisDataset.get('meta', {})
    except IndexError:
        return {}

def getModelStepData(repoName: str, modelName: str):
    modelLossDataPath = join(repoName, 'models', modelName, 'steps.csv')

    if not exists(modelLossDataPath): return None

    rows = []
    with open(modelLossDataPath) as f:
        r = reader(f)
        for row in r:
            rows.append((float(row[0]), int(row[1]), float(row[2]), float(row[3])))
    return rows
