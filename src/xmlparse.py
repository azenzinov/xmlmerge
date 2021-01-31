import xml.etree.ElementTree as et
import copy

#первый (с конца) файл будет основным, в него добавляются отсутствующие карты из предыдущих файлов
newTree = et.parse('IMAP14.XML')
newRoot = newTree.getroot()
newList = newRoot.find('ListOfEaiDataMap')

#предыдущий файл
tree = et.parse('IMAP13.XML')
root = tree.getroot()

for el in root.iter('EaiObjectMap'):
     print(el.find('Name').text)
     elCopy = copy.deepcopy(el)
     newList.append(elCopy)
     newTree.write('_IMAP.XML')
#
#for x in myroot.findall('EaiObjectMap'):
    #print(x.find('Name').text)