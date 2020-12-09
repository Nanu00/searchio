import wikipedia

while True:
    query = input('Search for wikipedia article: ')
    results = wikipedia.search(query)

    if len(results) == 0:
        if input(f"Did you mean: {wikipedia.suggest(query)}? y/n:") == 'y':
            print(f"Titles matching '{query}': {wikipedia.search(wikipedia.suggest(query))}")
        else:
            print(f"No results found for '{query}'.") 
            continue
    else:
        print(f"Titles matching '{query}':")
        for index, value in enumerate(results):
            print(f'[{index}]: {value}')
        choice = int(input("Please choose an article: "))
        print(wikipedia.summary(results[choice], sentences=2))