# wikipediasearch
A Wikipedia article search engine implemented in Python

See requirements.txt for required packages


Requirements can be installed with
```
pip install -r requirements.txt
```

How to use:

Obtain Discord bot credentials, and place in .env file in the same directory as main.py as `DISCORD_TOKEN`

Run main.py from commandline


# To develop:
  Create a pull request.
  
  All search modules are imported from ./src
  
  The modules each have the ability to send messages using discord.py.
     
     Example:
     
     https://github.com/ACEslava/wikipediasearch/blob/b6f1e54c185c3191a1496c817c27f5b59868dca9/src/wikipedia.py#L1-L17
     
     Each module is required to be hooked up to the logging system
     
     The required instance variables are:
        
        self.bot (Discord.py Bot object)
        
        self.searchQuery (The user search query)
        
        OPTIONAL: self.language (language switching)
       
     
  Any edits to main.py will be rejected. I will integrate the modules. Please have sufficient documentation for the module.
