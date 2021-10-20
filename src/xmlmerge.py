#Объединение нескольких XML-файлов патча в единый
#для примера: IMAP01.XML,IMAP02.XML,IMAP03.XML объединятся в _IMAP.XML
#при этом версия карты в результирующем файле будет использована из файла с максимальным номером
#поддерживаются IMAP, DMAP, DVM

import sys, os, re   #os + regexp
import shutil   #copy/move files

print('\nSiebel Patch Utils: Merge multiple XML files into one, 31.01.2021, ZAS\n')

#проверка на наличие аргумента - путь к папке с XML
if len(sys.argv) < 2:
    print('\nUsage: ' + sys.argv[0] + ' <path>\n')
    exit()

#папка для отработанных файлов
srcPath  = sys.argv[1] + '\\'
dstPath  = srcPath + '_source\\'
resFilePrefix  = ''             #результирующий файл - префикс
resFilePostfix = '_merged.XML'  #результирующий файл - постфикс
#список поддерживаемых типов
nameList = ['DVM','DMAP','IMAP'] #имена типов
typeList = ['^dvm[0-9]*.xml$','^dmap[0-9]*.xml$','^imap[0-9]*.xml$'] #типы
patList  = ['(<FinsValidationRuleSet[\s\S]+?<Name[> \t\n]+([^\>]+)<\/Name[\s\S]+?<\/FinsValidationRuleSet[> \n]+)',
            '(<FinsDataMapObject[\s\S]+?<Name[> \t\n]+([^\>]+)<\/Name[\s\S]+?<\/FinsDataMapObject[> \n]+)',
            '(<EaiObjectMap[\s\S]+?<Name[> \t\n]+([^\>]+)<\/Name[\s\S]+?<\/EaiObjectMap[> \n]+)']

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

#проверяет наличие элемента в результате и добавляет, при необходимости
def checkAddItem(itemName, itemValue, itemFileName):
    if itemName not in resultItems:
        #print(' ++ ADD ++')
        resultItems.append(itemName)
        resultItemsVal.append(itemValue)
        resultItemsFile.append(itemFileName)

#проверяем наличие папки
def checkCreateFolder(path):
    if not os.path.exists(path):
        os.mkdir(path)

#сбор файлов из папки
fileList = next(os.walk(srcPath))[2]
#fileList = ['IMAP12.XML','IMAP13.XML','IMAP14.XML']
#fileList = ['DVM08.XML','DVM09.XML']
#print(fileList)

#обработка по типам
#for currType in typeList:
#for currTypeIdx, currType in enumerate(typeList):
for currNameIdx, currName in enumerate(nameList):
    #if currName != 'DMAP': # <<< только для тестов >>>
    #    continue    
    
    #очистка результата
    resultItems     = []
    resultItemsVal  = []
    resultItemsFile = []

    currType = typeList[currNameIdx]

    matchList = getMatchFileList(currType, fileList)
    #print(matchList)
    print('=== ' + currName + ' (' + str(len(matchList)) + ') ===')

    #если файл данного типа единственный, то переносим его в папку исходников
    #с откопированием в результирующую, иначе обрабатываем пачку и исходники переносим в исходную 
    if len(matchList) == 1:
        checkCreateFolder(dstPath)
        srcFullFile = srcPath + matchList[0]
        dstFullFile = dstPath + matchList[0]
        shutil.move(srcFullFile, dstFullFile)
        shutil.copy2(dstFullFile, srcPath + resFilePrefix + currName + resFilePostfix)

    elif len(matchList) > 1:
        #обратная сортировка: от последнего к первому
        matchList.sort(key = getNameIndex)
        matchList.reverse()
        #print(matchList)

        pattern = patList[currNameIdx]
        for currFileIdx, currFile in enumerate(matchList):

            #получение содержимого файла
            srcFullFile = srcPath + currFile
            dstFullFile = dstPath + currFile
            fh = open(srcFullFile, 'r', encoding='utf8')
            content = ''.join(fh.readlines())
            if currFileIdx == 0:
                contentZero = content #для результирующего файла
            fh.close()
            #print(currFile)

            #поиск секций в файле
            for tag in re.finditer(pattern, content):
                #print(currFile + ' - ' + tag.group(2)) #название элемента
                #print(tag.group(1)) #содержимое элемента
                checkAddItem(tag.group(2), tag.group(1), currFile)

            #перенос файла в папку исходным с откопированием в исходную
            checkCreateFolder(dstPath) #проверяем наличие папки
            shutil.move(srcFullFile, dstFullFile)

        #запись результирующего файла
        #1. открываем первый файл и удалем из него все элементы, остаётся шапка и подвал
        elPlaceName = '<ELEMENT_PLACE>'
        re.findall(pattern, contentZero)
        content = re.sub(pattern, lambda match: elPlaceName, contentZero)
        #print(content)

        #2. вставлем новые потроха
        content = content.replace(elPlaceName, ''.join(resultItemsVal), 1) #замена первого элемента на потроха
        content = content.replace(elPlaceName, '')                         #очистка возможно оставшихся тегов
        #print(content)

        #3. записываем на диск
        f = open(srcPath + resFilePrefix + nameList[currNameIdx] + resFilePostfix, 'wb')
        f.write(content.encode('utf8'))
        f.close()

    #вывод информации о картах и файлах
    #print('--- Summary ---')

    #for resultIdx, resultItemName in enumerate(resultItems):
    #    print(resultItemName + ' - ' + resultItemsFile[resultIdx])