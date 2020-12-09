import wikipedia
from query import Query

search = Query(input('Search for a wikipedia article: '))
print(search.searchwikipedia())