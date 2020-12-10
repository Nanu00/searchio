import wikipedia
class Query:
    def __init__(self, articletitle=None):
        self.articletitle = articletitle
        self.choice = False
    def searchwikipedia(self):
        if self.choice == False:
            result = wikipedia.search(self.articletitle) #Searches Wikipedia for query
            if len(result) == 0: #Checks if any results are found.
                return f"No results found for '{self.articletitle}'."
            else: return result
        else:
            while True:
                try:
                    return wikipedia.page(title=self.articletitle)
                except wikipedia.DisambiguationError as e: #If there is a disambiguation of search
                    e = str(e).split('\n')
                    e.pop(0)
                    return e
                    

    def articlescrape(self):
        pagetitle = self.articletitle
        if pagetitle == None: #Can pass search query string to search if needed
            pagetitle = Query.searchwikipedia().split('https://en.wikipedia.org/wiki/')[1]
            pass
        return wikipedia.WikipediaPage(title=pagetitle)