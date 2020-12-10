from query import Query

search = Query(input('Wikipedia Article Search \nInput Wikipedia Page title:'))
options = input('[0] Search \n[1] Scrape \nPlease choose an option: ')
while True:
    if options == '0':
        result = search.searchwikipedia()
        break
    elif options == '1':
        result = search.articlescrape()
        break
    else:
        print('Please choose a valid option')
        continue

print(result)