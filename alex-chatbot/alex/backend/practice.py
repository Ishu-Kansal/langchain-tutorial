
def filltemplate(template: str, literal: bool, valuesDict: dict) -> str:
    values = [] # tuple of (starting idx, var name)
    
    i = 0
    while(i < len(template)):
        currSlice = template[i:]
        
        startingFound = currSlice.find('{{')
        endingFound = currSlice.find('}}')
        
        if(startingFound == -1 and endingFound == -1):
            break
        if(startingFound == -1 and endingFound != -1):
            return ValueError
        if(startingFound != -1 and endingFound == -1):
            return ValueError
        
        rawName = currSlice[startingFound:endingFound+2]
        values.append([i + startingFound, rawName])
        i += endingFound + 2

    newTemplate = ""
    prev = 0
    for i in range(len(values)):
        rawVal = values[i][1]
        val = rawVal[2:len(rawVal)-2].strip()
  
        newTemplate += template[prev:values[i][0]]
        prev = values[i][0] + len(values[i][1])
        if(val in valuesDict):
            newTemplate += valuesDict[val]
        else:
            if(literal):
                beginning = values[i][0]
                end = beginning + len(values[i][1])
                newTemplate += template[beginning:end]
            else:
                return KeyError
    
    if(prev < len(template)):
        newTemplate += template[prev]
        
    return newTemplate

inputStr = "Hi, my name is {{ name }} {{ and I am a {{ position }}"
print(filltemplate(inputStr, True, {"name": "Ishu",}))      
    
        