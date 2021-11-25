from Threads.DatasetBuilder import BaseDatasetBuilder

class TwitterDatasetBuilder(BaseDatasetBuilder):
    def __init__(self, parent=None, repoName=None):
        super().__init__(parent, repoName)
        self.setLineByLine(False)

    __searchQuery = ''
    def searchQuery(self) -> str: return self.__searchQuery
    def setSearchQuery(self, query: str): self.__searchQuery = query

    def createDataset(self) -> dict:
        from snscrape.modules.twitter import TwitterSearchScraper
        self.setTitle(f'Twitter search: \"{self.searchQuery()}\"')

        tweets = []

        scraper = TwitterSearchScraper(self.searchQuery())
        for t in scraper.get_items():
            content = t.content
            print(f'Scraped tweet: {content}')
            tweets.append(content)
        
        print(f'{len(tweets)} Tweets scraped!')

        with open(self.thisDatasetFileDestPath, 'w', encoding='utf-8') as f:
            f.writelines([i + '<|endoftext|>' for i in tweets])

        print(f'Written to {self.thisDatasetFileDestPath}')
        
        return { 'source': 'twitter', 'query': self.searchQuery() }