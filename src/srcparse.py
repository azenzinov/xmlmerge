import os, re

resultItems = []

#проверяет наличие элемента в результате и добавляет, при необходимости
def checkAddItem(itemName):
    if itemName not in resultItems:
        resultItems.append(itemName)

fh = open('IMAP12.XML', 'r', encoding='utf8')
content = (''.join(fh.readlines())).replace('\r\n', '').replace('\r', '').replace('\n', '')
pattern = '\/DestinationObjectName[<> \t]+Name[<> \t]+([^\>]+)<\/Name[<> \t]+SourceObjectName'
pattern = '(<EaiObjectMap *>[\s\S]*?<\/EaiObjectMap *>)'
pattern = '(<EaiObjectMap *>[\s\S]*?\/DestinationObjectName[> \t]+<Name[> \t]+([^\>]+)<\/Name[<> \t]+<SourceObjectName[\s\S]*?<\/EaiObjectMap *>)'
#print(content)

re.findall(pattern, content)
#re.sub(pattern, lambda match: match.group(1).re, content)
content = re.sub(pattern, lambda match: '<ELEMENT_PLACE>', content)
print(content)
exit()



#поиск секций в файле
#print(re.findall(pattern, content))
for tag in re.finditer(pattern, content):
    #print(tag.group(2)) #название элемента
    #print(tag.group(1)) #содержимое элемента
    #print('-----')
    checkAddItem(tag.group(2))

for resultIdx, resultItemName in enumerate(resultItems):
    print(resultItemName)