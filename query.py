import wikipedia
class Query:
    def __init__(self, usersearch):
        self.usersearch = usersearch

    def searchwikipedia(self):
        result = wikipedia.search(self.usersearch)
        if len(result) == 0:
            while True:
                didyoumean = input(f"Did you mean: {wikipedia.suggest(self.usersearch)}? y/n:")
                if didyoumean == 'y':
                    return f"Titles matching '{self.usersearch}': {wikipedia.search(wikipedia.suggest(self.usersearch))}"
                elif didyoumean == 'n':
                    return f"No results found for '{self.usersearch}'."
                else:
                    print(f"Please input a valid choice (y/n)")
                    continue
        else:
            print(f"Titles matching '{self.usersearch}':")
            while True:
                for index, value in enumerate(result):
                    print(f'[{index}]: {value}')
                choice = int(input("Please choose an article: "))
                try:
                    return(f'{wikipedia.summary(result[choice], sentences=2)} \n For more information, go to {wikipedia.page(result[choice]).url}')
                except wikipedia.DisambiguationError as e:
                    e = str(e).split('\n')
                    print(e.pop(0))
                    result = e
                    continue


