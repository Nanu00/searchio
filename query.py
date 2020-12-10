import wikipedia
class Query:
    def __init__(self, articletitle=None):
        self.articletitle = articletitle

    def searchwikipedia(self):
        usersearch = self.articletitle
        if usersearch == None: #Can pass search query string to search if needed
            usersearch = input('Search for a wikipedia article: ')
            pass

        result = wikipedia.search(usersearch) #Searches Wikipedia for query
        
        if len(result) == 0: #Checks if any results are found.
            while True:
                didyoumean = input(f"Did you mean: {wikipedia.suggest(usersearch)}? y/n:")
                if didyoumean == 'y':
                    return f"Titles matching '{usersearch}': {wikipedia.search(wikipedia.suggest(usersearch))}"
                elif didyoumean == 'n':
                    return f"No results found for '{usersearch}'."
                else:
                    print(f"Please input a valid choice (y/n)")
                    continue
        else:
            print(f"Titles matching '{usersearch}':") #Gives user options
            while True:
                for index, value in enumerate(result):
                    print(f'[{index}]: {value}')
                choice = int(input("Please choose an article: "))
                try:
                    return(f'{wikipedia.summary(result[choice])} \nFor more information, go to {wikipedia.page(result[choice]).url}')
                except wikipedia.DisambiguationError as e: #If there is a disambiguation of search
                    e = str(e).split('\n')
                    print(e.pop(0))
                    result = e
                    continue

    def articlescrape(self):
        pagetitle = self.articletitle
        if pagetitle == None: #Can pass search query string to search if needed
            pagetitle = Query.searchwikipedia().split('https://en.wikipedia.org/wiki/')[1]
            pass
        return wikipedia.WikipediaPage(title=pagetitle)