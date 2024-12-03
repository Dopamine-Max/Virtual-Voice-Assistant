import wikipediaapi

def search_wikipedia(query):
    # Create a Wikipedia API object
    wiki_wiki = wikipediaapi.Wikipedia('Oxy (maxtestgamer@gmail.com)','en')

    # Perform a search and get the page results
    search_results = wiki_wiki.page(query)

    # Check if there are any results
    if search_results.exists():
        return search_results.text[:1000]  # Displaying the first 1000 characters for brevity
    else:
        return "Sorry, no results found for that query."

