
from difflib import SequenceMatcher
from json.decoder import JSONDecodeError
from typing import List

from os.path import join, isdir, exists
from os import listdir
from json import dump, load
from datetime import datetime, timedelta
from csv import reader

__datasetTexts = {}

knownReposPath = join('knownRepos.json')

def getDurationString(passed: timedelta):
    hours, rem = divmod(passed.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    passedStr = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
    return passedStr

def getRepoMetadata(repoPath: str) -> dict:
    infoFilePath = join(repoPath, 'info.json')

    repoMetadata: dict = {}
    if exists(infoFilePath):
        with open(infoFilePath) as f:
            try:
                repoMetadata = load(f)
            except JSONDecodeError:
                repoMetadata = {}

    repoMetadata['path'] = repoPath
    return repoMetadata

def getModelsInRepository(repoPath: str) -> List[dict]:
    allModelsFolder = join(repoPath, 'models')
    
    if not exists(allModelsFolder): return []

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

def getDatasetsInRepository(repoPath: str) -> List[dict]:

    allDatasetsFolder = join(repoPath, 'datasets')
    if not exists(allDatasetsFolder): return []

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

def getGeneratedTextsInRepository(repoPath: str) -> List[dict]:
    allGensFolder = join(repoPath, 'generated')

    if not exists(allGensFolder): return []

    allPotentialGens = listdir(allGensFolder)

    validGens = []
    for dir in allPotentialGens:
        metaPath = join(allGensFolder, dir, 'meta.json')
        textsPath = join(allGensFolder, dir, 'texts.json')

        if exists(metaPath) and exists(textsPath):
            with open(metaPath) as f: meta = load(f)
            with open(textsPath) as f: texts = load(f)
            validGens.append({
                'texts': texts,
                'meta': meta
            })

    validGens.sort(key=lambda i: i['meta']['datetime'], reverse=True)
    return validGens
    
def getDatasetMetadata(repoPath: str, datasetName: str) -> dict:
    allDatasets = getDatasetsInRepository(repoPath)
    try:
        thisDataset = [i for i in allDatasets if i['pathName'] == datasetName][0]
        return thisDataset.get('meta', {})
    except IndexError:
        return {}

def getDatasetText(repoPath: str, datasetName: str) -> str:
    name = f'{repoPath}/{datasetName}'
    # if name in __datasetTexts: return __datasetTexts[name]

    targetDataset = join(repoPath, 'datasets', datasetName, 'dataset')
    text = None
    if exists(targetDataset):
        with open(targetDataset) as f:
            text = f.read()

    print(f'look for {targetDataset}')
    # __datasetTexts[name] = text
    return text

def getModelStepData(repoPath: str, modelName: str):
    modelLossDataPath = join(repoPath, 'models', modelName, 'steps.csv')

    if not exists(modelLossDataPath): return None

    rows = []
    with open(modelLossDataPath) as f:
        r = reader(f)
        for row in r:
            rows.append((float(row[0]), int(row[1]), float(row[2]), float(row[3])))
    return rows

def processGeneratedSamples(repoPath: str, genTexts: List[str], prompt: str) -> List[dict]:
    """
    We want to check each of the generated samples against the training data
    to see if there's overtraining going on.
    """

    output = [{ 'text': text, 'datasetMatches': []} for text in genTexts]

    for datasetMeta in getDatasetsInRepository(repoPath):
        datasetPath = join(repoPath, 'datasets', datasetMeta['pathName'], 'dataset')
        with open(datasetPath) as f: datasetText = f.read()
        seqMatcher = SequenceMatcher(
            isjunk=lambda x: x == prompt, 
            a=datasetText
        )

        for genTextIndex, genText in enumerate(genTexts):
            genText = genText.removeprefix(prompt)
            seqMatcher.set_seq2(genText)
            longestMatch = seqMatcher.find_longest_match()

            ratioMatchToGenerated = longestMatch.size / len(genText)

            outputItem = {
                'dataset': datasetMeta['pathName'],
                'datasetMatchIndex': longestMatch.a,
                'genTextMatchIndex': longestMatch.b,
                'size': longestMatch.size,
                'ratio': ratioMatchToGenerated
            }

            output[genTextIndex]['datasetMatches'].append(outputItem)

    return output

def initKnownRepos():
    # check if the knownRepos.json file exists
    if not exists(knownReposPath):
        print('Need to create knownRepos.json')
        with open(knownReposPath, 'w') as f:
            dump([], f)

def getKnownRepos():
    initKnownRepos()
    
    # It does exist, so let's read from it
    knownReposRaw = []
    try:
        with open(knownReposPath) as f:
            knownReposRaw = load(f)
    except IOError as e:
        print(e.strerror())
    except JSONDecodeError as e:
        print(e)

    # knownReposRaw is just a list of paths to repo folders
    # We need to check each repo and get its metadata
    knownRepos = []
    for repoPath in knownReposRaw:
        knownRepos.append(getRepoMetadata(repoPath))

    return knownRepos


def addKnownRepo(repoPath: str):
    initKnownRepos()

    knownReposRaw = []
    try:
        with open(knownReposPath) as f:
            knownReposRaw = load(f)
    except IOError as e:
        print(f'IO error: {e}')
    except JSONDecodeError as e:
        print(f'JSON decoding error: {e}')

    knownReposRaw.append(repoPath)

    try:
        with open(knownReposPath, 'w') as f:
            dump(knownReposRaw, f)
    except IOError as e:
        print(f'IO error: {e}')
    
def renameRepo(repoPath: str, title: str):
    infoFilePath = join(repoPath, 'info.json')
    existingMeta = getRepoMetadata(repoPath)

    existingMeta['title'] = title

    try:
        with open(infoFilePath, 'w') as f:
            dump(existingMeta, f)
    except IOError as e:
        print(f'IO error while trying to rename repo: {e}')