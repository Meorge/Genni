
from typing import List

from os.path import join, isdir, exists
from os import listdir
from json import load

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

def getDatasetMetadata(repoName: str, datasetName: str) -> dict:
    allDatasets = getDatasetsInRepository(repoName)
    thisDataset = [i for i in allDatasets if i['pathName'] == datasetName][0]
    return thisDataset['meta']