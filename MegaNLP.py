import nltk 
from nltk.corpus import wordnet 
from nltk.stem.wordnet import WordNetLemmatizer
import spacy
from spacy_wordnet.wordnet_annotator import WordnetAnnotator


class MegaNLP:
    def __init__(self):
        print('loading the wordnet corpus...')
        wordnet.ensure_loaded()
        print('loading done')
        self.nlp = spacy.load('en')
        self.nlp.add_pipe(WordnetAnnotator(self.nlp.lang), after='tagger')
        f= open('sorted_first_names.txt','r')
        lines = f.readlines()
        self.first_name_array = []
        for line in lines:
           line = line.rstrip()
           self.first_name_array.append(line)
        f= open('sorted_last_names.txt','r')
        lines = f.readlines()
        self.last_name_array = []
        for line in lines:
           line = line.rstrip()
           self.last_name_array.append(line)
        f= open('bad_words.txt','r')
        lines = f.readlines()
        self.profane_words_array = []
        for line in lines:
           line = line.rstrip()
           self.profane_words_array.append(line)


     
    def binarySearch(self ,arr, x): 
        l = 0
        r = len(arr) -1
        while (l <= r): 
            m = l + ((r - l) // 2) 
            #print('l= ',l,' ; r= ',r,' ; m= ',m)
            # Check if x is present at mid 
            if ( x.lower() == arr[m].lower() ): 
                return m - 1
      
            # If x greater, ignore left half 
            if ( x.lower() > arr[m].lower()): 
                l = m + 1
      
            # If x is smaller, ignore right half 
            else: 
                r = m - 1
      
        return -1
  
    def is_first_name(self, name):
       result = self.binarySearch(self.first_name_array, name) 
       if (result == -1): 
          return False
       else:
          return True 

    def is_last_name(self, name):
       result = self.binarySearch(self.last_name_array, name) 
       if (result == -1): 
          return False
       else:
          return True 

    def is_profane_word(self, name):
       name = name.replace('\'','')
       result = self.binarySearch(self.profane_words_array, name) 
       if (result == -1): 
          return False
       else:
          return True 
    def find_first_names(self, mystr):
       sent = mystr.split()
       sent = self.remove_common_words(sent)
       names = []
       for word in sent:
           if( self.is_first_name(word)):
               names.append(word)
       return names

    def find_profane_words(self, mystr):
       sent = mystr.split()
       sent = self.remove_common_words(sent)
       names = []
       for word in sent:
           if( self.is_profane_word(word)):
               names.append(word)
       return names

    def find_last_names(self, mystr):
       sent = mystr.split()
       sent = self.remove_common_words(sent)
       names = []
       for word in sent:
           if( self.is_first_name(word)):
               names.append(word)
       return names
    def remove_common_words(self, words):
        commonwords = ['i','the','is','a','an','am','are','was','were' ,'have','has','had','will','going','she','he','they','can','may','might','should','could','can','would','please','thanks','then','to','for','with','upon','on','in','from','since','after','before','want','need','there','here','be','my','your','her','his','mine','yours','hers']
        new_words = [word for word in words if word not in commonwords]
        return new_words


    def contain_domain(self, sentence,domain): 
        domains = []
        words = sentence.split()
        words = self.remove_common_words(words)
        for word in words:
            token = self.nlp(word)[0]
            tmp_domains = token._.wordnet.wordnet_domains()
            for dom in tmp_domains:
                 domains.append(dom)
    
        domains = list(set(tmp_domains))
        print(domains)
        for dom in domains:
            if( dom == domain):
                return True
        return False
    
    def find_synonym(self, word, sentence):	
        synonyms = [] 
        answers = []
        for syn in wordnet.synsets(word): 
            for l in syn.lemmas(): 
                synonyms.append(l.name()) 
        synonyms = list(set(synonyms))
        words = sentence.split()
        words = self.remove_common_words(words)
        for myword in words:
           simpleword = WordNetLemmatizer().lemmatize(myword)
           for synonym in synonyms:
               simple_syn = WordNetLemmatizer().lemmatize(synonym)
               if (simpleword==synonym):
                   answers.append(myword)
        return answers

    def find_antonyms(self, word, sentence):	
        antonyms = [] 
        synonyms = [] 
        answers = []
        for syn in wordnet.synsets(word): 
            for l in syn.lemmas(): 
                synonyms.append(l.name()) 
                if l.antonyms(): 
        	        antonyms.append(l.antonyms()[0].name()) 
        
        for syn in wordnet.synsets(word): 
            for l in syn.lemmas(): 
                synonyms.append(l.name()) 
        synonyms = list(set(antonyms))
        words = sentence.split()
        word = self.remove_common_words(words)
        for myword in words:
           simpleword = WordNetLemmatizer().lemmatize(myword)
           for synonym in synonyms:
               simple_syn = WordNetLemmatizer().lemmatize(synonym)
               if (simpleword==synonym):
                   answers.append(myword)
        return answers

    def find_similar(self, word, sentence):	
        similars = []
        synsets_word = wordnet.synsets(word)
        words = sentence.split()
        words = self.remove_common_words(words)
        for myword in words:
           synsets_myword = wordnet.synsets(myword)
           for mysyn in synsets_myword :
               for syn in synsets_word:
                   sim = mysyn.wup_similarity(syn)
                   #print('similarity of',syn,', ', mysyn,' is ', sim)
                   if (sim is not None):
                       if (sim > 0.6):
                           similars.append(myword)
        similars = list(set(similars))
        return similars

