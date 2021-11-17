
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

def getRepoMetadata(repoName: str) -> dict:
    infoFilePath = join(repoName, 'info.json')

    repoMetadata: dict = {}
    if exists(infoFilePath):
        with open(infoFilePath) as f:
            try:
                repoMetadata = load(f)
            except JSONDecodeError:
                repoMetadata = {}

    repoMetadata['path'] = repoName
    return repoMetadata

def getModelsInRepository(repoName: str) -> List[dict]:
    allModelsFolder = join(repoName, 'models')
    
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

def getDatasetsInRepository(repoName: str) -> List[dict]:

    allDatasetsFolder = join(repoName, 'datasets')
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

def getGeneratedTextsInRepository(repoName: str) -> List[dict]:
    allGensFolder = join(repoName, 'generated')

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
    
def getDatasetMetadata(repoName: str, datasetName: str) -> dict:
    allDatasets = getDatasetsInRepository(repoName)
    try:
        thisDataset = [i for i in allDatasets if i['pathName'] == datasetName][0]
        return thisDataset.get('meta', {})
    except IndexError:
        return {}

def getDatasetText(repoName: str, datasetName: str) -> str:
    name = f'{repoName}/{datasetName}'
    # if name in __datasetTexts: return __datasetTexts[name]

    targetDataset = join(repoName, 'datasets', datasetName, 'dataset')
    text = None
    if exists(targetDataset):
        with open(targetDataset) as f:
            text = f.read()

    print(f'look for {targetDataset}')
    # __datasetTexts[name] = text
    return text

def getModelStepData(repoName: str, modelName: str):
    modelLossDataPath = join(repoName, 'models', modelName, 'steps.csv')

    if not exists(modelLossDataPath): return None

    rows = []
    with open(modelLossDataPath) as f:
        r = reader(f)
        for row in r:
            rows.append((float(row[0]), int(row[1]), float(row[2]), float(row[3])))
    return rows

def processGeneratedSamples(repoName: str, genTexts: List[str], prompt: str) -> List[dict]:
    """
    We want to check each of the generated samples against the training data
    to see if there's overtraining going on.
    """

    output = [{ 'text': text, 'datasetMatches': []} for text in genTexts]

    for datasetMeta in getDatasetsInRepository(repoName):
        datasetPath = join(repoName, 'datasets', datasetMeta['pathName'], 'dataset')
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
    
