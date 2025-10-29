import os, nltk
os.system('color')
from nltk.tokenize import wordpunct_tokenize
nltk.download('stopwords')
from nltk.corpus import stopwords
from Levenshtein import distance

def preProcessor(String):
    String = wordpunct_tokenize(String.replace(".", "").lower()) #Case Folding & Tokenisations
    null, Consonants, Irregulars, stopWords = "", "qwrtypsdfghjklzxcvbnm", {"children":"child", "feet":"foot", "teeth": "tooth", "mice": "mouse", "people": "person"}, stopwords.words('english')

    for Index in range(len(String)):
        if String[Index] in stopWords: #Stop Words Elimination
            String[Index] = null
            
        #Asymmetric Expansion
        elif String[Index][-3:] == "ies" and String[Index][-4] in Consonants:
            String[Index] = String[Index][:-3] + "y"

        elif String[Index][-3:] == "ves":
            String[Index] = String[Index][:-3] + "f"
            
        elif String[Index][-2:] == "es" and (String[Index][-3] in ["s", "x", "z"] or String[Index][-4:-2] in ["ch, sh"] or (String[Index][-3] == "o" and String[Index][-4] in Consonants)):
            String[Index] = String[Index][:-2]
        
        elif String[Index][-1] == "s":
            String[Index] = String[Index][:-1]
            
        elif String[Index][-3:] == "men":
            String[Index] = String[Index][:-3] + "man"
        
        elif String[Index] in Irregulars.keys():
            String[Index] = Irregulars[String[Index]]
        
    while null in String:
            String.remove(null)      
    return String

def And(Query):
    Query = preProcessor(Query.replace(" and ", " "))
    if any(Q not in InvertedIndexStruct for Q in Query):
        return []
    
    ID1, ID2 = InvertedIndexStruct[Query[0]], InvertedIndexStruct[Query[1]]
    if ID1[-1] < ID2[0] or ID2[-1] < ID1[0]:
        return []

    AND = []
    for ID in ID1:
        if ID in ID2:
            AND.append(ID)
    return sorted(AND)

def Not(Query):
    Query = preProcessor(Query.replace(" not ", " "))
    if Query[0] not in InvertedIndexStruct:
        return []
    
    if Query[1] not in InvertedIndexStruct:
        return InvertedIndexStruct[Query[0]]
    
    NOT = []
    ID1, ID2 = InvertedIndexStruct[Query[0]], InvertedIndexStruct[Query[1]]
    for ID in ID1:
        if ID not in ID2:
            NOT.append(ID)
    return sorted(NOT)
    
def Or(Query):
    Query = preProcessor(Query.replace(" or ", " "))
    if all(Q not in InvertedIndexStruct for Q in Query):
        return []
    
    for Q in Query:
        if Q in InvertedIndexStruct:
            QID = InvertedIndexStruct[Q]
            if len(QID) == lengthDocs:
                return QID
            
    OR = []
    for Q in Query:
        if Q in InvertedIndexStruct:
            OR += InvertedIndexStruct[Q]     
    return sorted(set(OR))

def Proximity(Query):
    String = f" near/{Query.split()[1][-1]} "
    Query = preProcessor(Query.replace(String, " "))
    if any(Q not in InvertedIndexStruct for Q in Query):
        return []
    
    Q0, Q1 = Query[0], Query[1]
    ID1, ID2 = InvertedIndexStruct[Q0], InvertedIndexStruct[Q1]
    if ID2[-1] < ID1[0] or ID1[-1] < ID2[0]:
        return []

    PROX = []
    for ID in ID1:
        if ID in ID2:
            PROX.append(ID)

    Proximity = []
    for Element in PROX:
        File = open(listDocs[Element - 1], "r")
        Words = preProcessor(File.read())
        if abs(Words.index(Q0) - Words.index(Q1)) <= int(String[-2]):
            Proximity.append(Element)
        File.close()
    return sorted(Proximity)

def biGrams(String):
    lessLengthWC, First, Last = len(String) - 1, String[0], String[-1]
    if First != "*":
        gramList = [f"${First}"]
    else:
        gramList = []

    String = String.split("*")
    for Element in String:
        lengthElement = len(Element) - 1
        for Index in range(lengthElement):
            gramList.append(Element[Index : Index + 2])

    if Last != "*":
        gramList.append(f"{Last}$")

    return gramList

def Main(Query):
    Query = Query.split()
    for Index in [0, 2]:
        Word = Query[Index]
        if "*" in Word:
            setBigrams, listSimilars = set(biGrams(Word)), []
            for Vals in listVals:
                setVals = set(Vals)
                lengthSBV, lengthSVB, Boundary = len(setBigrams - setVals), len(setVals - setBigrams), len(Vals) // 2 + 1 #A hand-made good heuristic boundary to find out how similar the bigram index lists are.
                if all(Val in Word for Val in Vals) or all(Val in Vals for Val in Word) or any(length <= Boundary for length in [lengthSBV, lengthSVB]):
                    listSimilars.append(listKeys[listVals.index(Vals)])
    
            if len(listSimilars) > 1: #Just in Case! #Although a basic but good heuristic boundary has been defined, it's good to find the word with the least Levenshtein distance.
                listCounter = []
                for Key in listSimilars:
                    listCounter.append(distance(Word, Key))
                Query[Index] = listKeys[listCounter.index(min(listCounter))]
                    
            else:
                Query[Index] = listSimilars[0]
                    
            print(f"Hah, Gotcha! Why so nervous and neckless to type '{Query[Index]}' correctly?!")
            print()

        elif Word not in BGs:
            listCounter = []
            for Key in BGs:
                if len(Word) <= int(1.25 * len(Key)): #Another hand-made good heuristic boundary!
                    listCounter.append(distance(Word, Key))
                    
            if listCounter != []:
                Query[Index] = listKeys[listCounter.index(min(listCounter))]
                print(f"Did you mean:\033[1;3m {Query[Index]}\033[0m")
                
            else:
                print("ERROR 404! NOT FOUND")
                print()

    Query = " ".join(Query)
    if "and" in Query:
        return And(Query)
    
    elif "not" in Query:
        return Not(Query)
                
    elif "or" in Query:
        return Or(Query)
    
    else:
        return Proximity(Query) #The stop words are ignored.

#Globals!
listDocs, lengthDocs = [], 0
while True:
    try:
        while True:
            Document = input("Enter your text document: ")
            if ".txt" == Document[-4:].lower() and Document not in listDocs:
                break
        listDocs.append(Document)
        lengthDocs += 1
        
    except EOFError: #Enter Ctrl+d to exit
        print("START!")
        print()
        break
    
InvertedIndexStruct, BGs = dict(), dict()
for Index in range(lengthDocs):
    Lines, File = [], open(listDocs[Index], "r")
    for Line in File:
        if Line != "\n":
            Lines += preProcessor(Line)

    if Lines != []:
        Lines = sorted(Lines)
        for Term in Lines:
            I = Index + 1
            if Term in InvertedIndexStruct and I not in InvertedIndexStruct[Term]:
                InvertedIndexStruct[Term].append(I)
            else:
                InvertedIndexStruct[Term] = [I]
                
            if Term not in BGs:
                 BGs[Term] = biGrams(Term) 
    File.close()

InvertedIndexStruct, BGs, listKeys, listVals = dict(sorted(InvertedIndexStruct.items())), dict(sorted(BGs.items())), list(BGs.keys()), list(BGs.values())
print("Term-Document Inverted Index Structure:")
print()
print(InvertedIndexStruct)
print()
print("Bi-gram Index Structure:")
print()
print(BGs)
print()

while True:
    Query = input("What are you looking for? ").lower()
    BooList = [" not ", " and ", " or ", " near/", "*"] #As the default, promixity has the least priority. Star is added!
    while all(BOO not in Query for BOO in BooList):
        Query = input("What are you looking for? Boolean or proximity please. ").lower()

    print()
    print(Main(Query)) #Main is ready to be called.
    print()
    
    End = input("Wanna end this? <Y, N> ")
    while End not in ["Y", "y", "N", "n"]:
        End = input("DON'T WASTE MY TIME! You wanna end this? <Y, N> ")
    if End in "Yy":
        print("Good-bye")
        break
    else:
        print("Goodluck!")
        print()
