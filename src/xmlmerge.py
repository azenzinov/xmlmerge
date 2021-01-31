#Объединение нескольких XML-файлов патча в единый
#для примера: IMAP01.XML,IMAP02.XML,IMAP03.XML объединятся в _IMAP.XML
#при этом версия карты в результирующем файле будет использована из файлв с максимальным номером
#поддерживаются IMAP, DMAP, DVM

import os, re   #os + regexp
import shutil   #copy/move files
#import xml.etree.ElementTree as et #поддержка XML
#import copy                        #копирование элементов XML
#content = ''
#with open('IMAP.XML', 'r', encoding="utf8") as fh:
#    for line in fh:
#        #if not line.startswith("\n"):
#        content += line.rstrip("\n") #print(line, end = "")   # line.rstrip("\n") would also work

#возвращает массив с найденными названиями файлов, подходящими по маске
def getMatchFileList(currType, fileList):
    ret = []
    for currFile in fileList:
        x = re.search(currType, currFile, re.IGNORECASE)
        if x:
            ret.append(currFile)
            #print (currType, currFile, x.group())
    return ret
#для сортировки файлов по индексу в названии
def getNameIndex(name):
    ret = 0
    y = re.search('[0-9]+', name)
    if y:
        ret = int(y.group())
    return ret

# --- Вариант работы с файлом как с текстом --->
#проверяет наличие элемента в результате и добавляет, при необходимости
def checkAddItem(itemName, itemValue, itemFileName):
    if itemName not in resultItems:
        #print(' ++ ADD ++')
        resultItems.append(itemName)
        resultItemsVal.append(itemValue)
        resultItemsFile.append(itemFileName)
# --- Вариант работы с файлом как с текстом <---

#папка для отработанных файлов
dstPath  = '_source'
#список поддерживаемых типов
nameList = ['IMAP','DMAP','DVM'] #имена типов
typeList = ['^imap[0-9]*.xml$','^dmap[0-9]*.xml$','^dvm[0-9]*.xml$'] #типы
patList  = ['(<EaiObjectMap[\s\S]+?<Name[> \t\n]+([^\>]+)<\/Name[\s\S]+?<\/EaiObjectMap[> \n]+)',
            '(<FinsDataMapObject[\s\S]+?<Name[> \t\n]+([^\>]+)<\/Name[\s\S]+?<\/FinsDataMapObject[> \n]+)',
            '(<FinsValidationRuleSet[\s\S]+?<Name[> \t\n]+([^\>]+)<\/Name[\s\S]+?<\/FinsValidationRuleSet[> \n]+)']

#nameList = ['DVM'] #'IMAP','DMAP','DVM'] #имена типов
#typeList = ['^dvm[0-9]*.xml$'] #'^imap[0-9]*.xml$','^dmap[0-9]*.xml$','^dvm[0-9]*.xml$'] #типы
#patList  = ['(<FinsValidationRuleSet[\s\S]+?Group[\s\S]+?<Name[> \t\n]+([^\>]+)<\/Name[> \t\n]+<StartDate[\s\S]+?<\/FinsValidationRuleSet[> \n]+)']
            #['(<FinsValidationRuleSet *>[\s\S]*?Group[/> \t]+<Name[> \t]+([^\>]+)<\/Name[<> \t]+<StartDate[\s\S]*?<\/FinsValidationRuleSet *>)']
            #'(<FinsDataMapObject *>[\s\S]*?Inactive[/> \t]+<Name[> \t]+([^\>]+)<\/Name[<> \t]+<SrcBusObjName[\s\S]*?<\/FinsDataMapObject *>)']
            #'(<EaiObjectMap *>[\s\S]*?\/DestinationObjectName[> \t]+<Name[> \t]+([^\>]+)<\/Name[<> \t]+<SourceObjectName[\s\S]*?<\/EaiObjectMap *>)']
#elemList = [('ListOfEaiDataMap','EaiObjectMap')] # --- вариант работы через распарсивание XML

#сбор файлов из папки
fileList = next(os.walk("."))[2]
#fileList = ['IMAP12.XML','IMAP13.XML','IMAP14.XML']
#fileList = ['DVM08.XML','DVM09.XML']
#print(fileList)

#если файлы есть, то предварительно создаём подпапку для переноса в неё файлов
if len(fileList) > 0 and not os.path.exists(dstPath):
    os.mkdir(dstPath)

#обработка по типам
#for currType in typeList:
#for currTypeIdx, currType in enumerate(typeList):
for currNameIdx, currName in enumerate(nameList):
    #if currName != 'DMAP': #TODO <<< только для тестов >>>
    #    continue    
    #очистка результата
    resultItems     = []
    resultItemsVal  = []
    resultItemsFile = []

    currType = typeList[currNameIdx]

    matchList = getMatchFileList(currType, fileList)
    #print(matchList)
    print('===' + currName + ' (' + str(len(matchList)) + ') ===')

    #если файл данного типа единственный, то переносим его в папку исходников
    #с откопированием в результирующую, иначе обрабатываем пачку и исходники переносим в исходную 
    if len(matchList) == 1:
        currFile = matchList[0]
        dstFile = dstPath +'/' +currFile
        shutil.move(currFile, dstFile)
        shutil.copy2(dstFile, './_' + currName + '.XML')

    elif len(matchList) > 1:
        #обратная сортировка: от последнего к первому
        matchList.sort(key = getNameIndex)
        matchList.reverse()
        #print(matchList)

        # --- Вариант работы с файлом как с текстом --->
        pattern = patList[currNameIdx]
        for currFileIdx, currFile in enumerate(matchList):

            #получение содержимого файла
            fh = open(currFile, 'r', encoding='utf8')
            #линеаризация содержимого
            #content = (''.join(fh.readlines())).replace('\r\n', '').replace('\r', '').replace('\n', '')
            content = ''.join(fh.readlines())
            if currFileIdx == 0:
                contentZero = content
            fh.close()
            #print(currFile)
            #print(content)

            #поиск секций в файле
            ##print(re.findall(pattern, content))
            for tag in re.finditer(pattern, content):
                print(currFile + ' - ' + tag.group(2)) #название элемента
                #print(tag.group(1)) #содержимое элемента
                checkAddItem(tag.group(2), tag.group(1), currFile)

            #перенос файла в папку исходным с откопированием в исходную
            shutil.move(currFile, dstPath +'/' +currFile)

        #запись результирующего файла
        #1. открываем первый файл и удалем из него все элементы
        elPlaceName = '<ELEMENT_PLACE>'
        #fh = open(matchList[0], 'r', encoding='utf8')
        ##content = (''.join(fh.readlines())).replace('\r\n', '').replace('\r', '').replace('\n', '')
        #content = ''.join(fh.readlines())
        re.findall(pattern, contentZero)
        content = re.sub(pattern, lambda match: elPlaceName, contentZero)
        #print(content)

        #2. вставлем новые потроха
        content = content.replace(elPlaceName, ''.join(resultItemsVal), 1)
        content = content.replace(elPlaceName, '')
        #print(''.join(resultItemsVal))
        #print(content)


        #3. записываем
        f = open('_' + nameList[currNameIdx] + '.XML', 'wb')
        f.write(content.encode('utf8'))
        f.close()
        # --- Вариант работы с файлом как с текстом <---

        # --- вариант работы через распарсивание XML, не подошёл из-за перекодирования символов -->
        #tagList = elemList[currTypeIdx][0]
        #tagEl   = elemList[currTypeIdx][1]
        ##print('#'+tagList+" / "+tagEl)
        ##в нумераторе пропускаем первый элемент, он будет основой
        #newTree = et.parse(matchList[0])
        #newRoot = newTree.getroot()
        #newList = newRoot.find(tagList)
        ##зачитываем его содержимое
        #for newEl in newRoot.iter(tagEl):
        #    print('new:' + newEl.find('Name').text)
        #    print('new:' + newEl.find('Comments').text)
        #    resultItems.append(newEl.find('Name').text)
        #    resultItemsFile.append(matchList[0])
        ##перебор остальных файлов
        #for currFileIdx, currFile in enumerate(matchList[1:], start=1):
        #    print(str(currFileIdx)+'-----' + currFile + '-----')
        #    #перебор содержимого по элементам
        #    tree = et.parse(currFile)
        #    root = tree.getroot()
        #    for el in root.iter(tagEl):
        #        elName = el.find('Name').text
        #        #добавление элемента к результату, если такого ещё не было
        #        if elName not in resultItems:
        #            print('check' + elName + ' ADD ')
        #            elCopy = copy.deepcopy(el)
        #            newList.append(elCopy)
        #            resultItems.append(elName)
        #            resultItemsFile.append(currFile)
        #        else:
        #            print('check' + elName + ' SKIP ')
        ##запись результата
        #newTree.write('_IMAP.XML', 'utf-8', 1)
        # --- вариант работы через распарсивание XML <--



    #вывод информации о картах и файлах
    print('--- Summary ---')

    for resultIdx, resultItemName in enumerate(resultItems):
        print(resultItemName + ' - ' + resultItemsFile[resultIdx])
    

#os.path.join(dir, f) 
# if f.lower().endswith('.xml')