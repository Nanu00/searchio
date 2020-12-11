import wikipedia
class Query:
    def __init__(self, articletitle=None, lang='en'):
        self.articletitle = articletitle
        self.choice = False
        wikipedia.set_lang(lang)
    def searchwikipedia(self):
        if self.choice == False:
            result = wikipedia.search(self.articletitle) #Searches Wikipedia for query
            if len(result) == 0: #Checks if any results are found.
                return False
            else: return result
        else:
            while True:
                try:
                    return wikipedia.WikipediaPage(title=self.articletitle)
                except wikipedia.DisambiguationError as e: #If there is a disambiguation of search
                    e = str(e).split('\n')
                    e.pop(0)
                    return e
                    

    def articlescrape(self):
        try:
            return wikipedia.WikipediaPage(title=self.articletitle)
        except wikipedia.DisambiguationError:
            raise
    
    def languages(self):
        return wikipedia.languages()