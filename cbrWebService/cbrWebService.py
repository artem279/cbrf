from zeep import Client
from lxml import etree, objectify
from datetime import datetime

def __Try_catchDecorator(myFunc):
    def wrapper(value):
        try:
            val = value.text
            return myFunc(val)
        except:
            val = ''
            return myFunc(val)

    return wrapper


@__Try_catchDecorator
def getValue(value):
    content = value.replace('\n', '').replace('\r', '').replace('\t', '').replace('|', '/').replace('"', '')
    return content


class CreditOrgInfo:
    def __init__(self, url=None):
        if url is None:
            self._url = 'http://www.cbr.ru/CreditInfoWebServ/CreditOrgInfo.asmx?WSDL'
        else:
            self._url = url
        self.client = Client(self._url)

    def saveXmlToFile(self, xml, filename):
        '''Сохраняет объект etree._Element в xml-файл'''
        if isinstance(xml, etree._Element):
            pass
        else:
            raise ValueError('Is not an etree._Element node')
        xmltree = etree.tostring(xml, encoding="utf-8", method="xml", pretty_print=True)
        etree.fromstring(xmltree).getroottree().write(filename, encoding='utf-8', pretty_print=True)

    def CleanNameSpaces(self, root):
        '''Чистит namespace'ы из xml'''
        for elem in root.getiterator():
            if not hasattr(elem.tag, 'find'):
                continue  # (1)
            i = elem.tag.find('}')
            if i >= 0:
                elem.tag = elem.tag[i + 1:]

        objectify.deannotate(root, cleanup_namespaces=True)

        return root

    def Form101IndicatorsEnumXML(self):
        '''Справочник индикаторов для формы 101 (как XMLDocument)'''
        return self.CleanNameSpaces(self.client.service.Form101IndicatorsEnumXML().getroottree().getroot())

    def Form102IndicatorsEnumXML(self):
        '''Справочник символов для формы 102 (как XMLDocument)'''
        return self.CleanNameSpaces(self.client.service.Form102IndicatorsEnumXML().getroottree().getroot())

    def BicToIntCode(self, bic):
        '''Bic код во внутренний код кред.орг.'''
        return int(self.client.service.BicToIntCode(str(bic)))

    def BicToRegNumber(self, bic):
        '''Bic код в регистрационный номер кред.орг.'''
        return int(self.client.service.BicToRegNumber(str(bic)))

    def IntCodeToRegNum(self, IntNumber):
        '''внутренний код кред.орг. в регистрационный номер КО.'''
        return int(self.client.service.IntCodeToRegNum(int(IntNumber)))

    def CreditInfoByIntCodeXML(self, InternalCode):
        '''Информация о кредитной орг. по вн.коду (как XMLDocument)'''
        root = self.client.service.CreditInfoByIntCodeXML(int(InternalCode)).getroottree().getroot()
        return self.CleanNameSpaces(root)

    def CreditInfoByIntCodeExXML(self, InternalCodes):
        '''Информация о кредитной орг. по вн.коду (как XML Document) ver- 26.02.2015'''
        if isinstance(InternalCodes, (list, tuple, set)):
            pass
        else:
            raise ValueError('InternalCodes must be tuple, list or set!')
        root = self.client.service.CreditInfoByIntCodeXML(InternalCodes).getroottree().getroot()
        return self.CleanNameSpaces(root)

    def CreditInfoByIntCodeList(self, InternalCodes):
        '''Информация о кредитной орг. по вн.коду (как list or dict)'''
        if isinstance(InternalCodes, (list, tuple, set)):
            pass
        else:
            InternalCodes = list(InternalCodes)
        datalist = []
        for ic in InternalCodes:
            data = self.CreditInfoByIntCodeXML(ic)
            for co in data.iter('CO'):
                creditorg = {}
                creditorg['InternalCode'] = str(ic)
                creditorg['RegNumber'] = getValue(co.find('RegNumber'))
                creditorg['BIC'] = getValue(co.find('BIC'))
                creditorg['OrgName'] = getValue(co.find('OrgName'))
                creditorg['OrgFullName'] = getValue(co.find('OrgFullName'))
                creditorg['phones'] = getValue(co.find('phones'))
                creditorg['DateKGRRegistration'] = getValue(co.find('DateKGRRegistration'))
                creditorg['MainRegNumber'] = getValue(co.find('MainRegNumber'))
                creditorg['MainDateReg'] = getValue(co.find('MainDateReg'))
                creditorg['UstavAdr'] = getValue(co.find('UstavAdr'))
                creditorg['FactAdr'] = getValue(co.find('FactAdr'))
                creditorg['Director'] = getValue(co.find('Director'))
                creditorg['UstMoney'] = getValue(co.find('UstMoney'))
                creditorg['OrgStatus'] = getValue(co.find('OrgStatus'))
                creditorg['RegCode'] = getValue(co.find('RegCode'))
                creditorg['SSV_Date'] = getValue(co.find('SSV_Date'))
                creditorg['Licenses'] = [{'LCode': getValue(row.find('LCode')),
                                          'LT': getValue(row.find('LT')),
                                          'LDate': getValue(row.find('LDate'))} for row in data.iter('LIC')]
                datalist.append(creditorg)

        return datalist

    def GetOfficesXML(self, IntCode):
        '''Информация по филиальной сети кредитной орг. по вн.коду (как XML)'''
        return self.CleanNameSpaces(self.client.service.GetOfficesXML(int(IntCode)).getroottree().getroot())

    def EnumBIC_XML(self):
        '''Данные по BIC кодам КО (как XMLDocument), без филиалов, ver: 04.07.2007'''
        return self.CleanNameSpaces(self.client.service.EnumBIC_XML().getroottree().getroot())

    def LastUpdate(self):
        '''Получение даты последнего обновления базы по КО (как datetime)'''
        return self.client.service.LastUpdate()

    def SearchByNameXML(self, namepart):
        '''Поиск кредитных орг. по названию (как XML)'''
        return self.CleanNameSpaces(self.client.service.SearchByNameXML(str(namepart)).getroottree().getroot())

    def GetDatesForF123(self, RegNum):
        '''Список дат для формы 123 (как list of datetime)'''
        return self.client.service.GetDatesForF123(int(RegNum))

    def Data123FormFullXML(self, RegNum, OnDate):
        '''Данные по форме 123 (как XML)'''
        if isinstance(OnDate, datetime):
            pass
        else:
            OnDate = datetime.strptime(OnDate, '%Y-%m-%d')
        return self.CleanNameSpaces(self.client.service.Data123FormFullXML(int(RegNum), OnDate).getroottree().getroot())

    def Data101FullExV2XML(self, CredOrgNumbers, IndCode, DateFrom, DateTo):
        '''Данные КО. формы 101, полностью (как XML) по нескольким КО ver 07.03.2017'''
        if isinstance(DateFrom, datetime):
            pass
        else:
            DateFrom = datetime.strptime(DateFrom, '%Y-%m-%d')

        if isinstance(DateTo, datetime):
            pass
        else:
            DateTo = datetime.strptime(DateTo, '%Y-%m-%d')
        if isinstance(CredOrgNumbers, list):
            pass
        else:
            CredOrgNumbers = list(CredOrgNumbers)
        return self.CleanNameSpaces(self.client.service.Data101FullExV2XML(CredOrgNumbers, str(IndCode), DateFrom,
                                                                           DateTo).getroottree().getroot())

    def Data101FullV2XML(self, CredOrgNumber, IndCode, DateFrom, DateTo):
        '''Данные КО. формы 101, полностью (как XML) mod 07.03.2017'''
        if isinstance(DateFrom, datetime):
            pass
        else:
            DateFrom = datetime.strptime(DateFrom, '%Y-%m-%d')

        if isinstance(DateTo, datetime):
            pass
        else:
            DateTo = datetime.strptime(DateTo, '%Y-%m-%d')
        return self.CleanNameSpaces(self.client.service.Data101FullV2XML(int(CredOrgNumber), str(IndCode), DateFrom,
                                                                         DateTo).getroottree().getroot())

    def Data102FormExXML(self, CredOrgNumbers, SymbCode, DateFrom, DateTo):
        '''Данные КО. формы 102, кратко (как XMLDocument) по нескольким КО.'''
        if isinstance(DateFrom, datetime):
            pass
        else:
            DateFrom = datetime.strptime(DateFrom, '%Y-%m-%d')

        if isinstance(DateTo, datetime):
            pass
        else:
            DateTo = datetime.strptime(DateTo, '%Y-%m-%d')
        if isinstance(CredOrgNumbers, list):
            pass
        else:
            CredOrgNumbers = list(CredOrgNumbers)
        return self.CleanNameSpaces(self.client.service.Data102FormExXML(CredOrgNumbers, int(SymbCode), DateFrom,
                                                                           DateTo).getroottree().getroot())

    def Data102FormXML(self, CredOrgNumber, SymbCode, DateFrom, DateTo):
        '''Данные КО. формы 102, кратко (как XMLDocument)'''
        if isinstance(DateFrom, datetime):
            pass
        else:
            DateFrom = datetime.strptime(DateFrom, '%Y-%m-%d')

        if isinstance(DateTo, datetime):
            pass
        else:
            DateTo = datetime.strptime(DateTo, '%Y-%m-%d')
        return self.CleanNameSpaces(self.client.service.Data102FormXML(int(CredOrgNumber), int(SymbCode), DateFrom,
                                                                         DateTo).getroottree().getroot())

    def Data101FullList(self, CredOrgNumbers, IndCode, DateFrom, DateTo):
        '''Данные КО. формы 101, полностью (как list of dict) по нескольким КО'''
        if isinstance(DateFrom, datetime):
            pass
        else:
            DateFrom = datetime.strptime(DateFrom, '%Y-%m-%d')

        if isinstance(DateTo, datetime):
            pass
        else:
            DateTo = datetime.strptime(DateTo, '%Y-%m-%d')
        if isinstance(CredOrgNumbers, list):
            pass
        else:
            CredOrgNumbers = list(CredOrgNumbers)
        datalist = []
        for rn in CredOrgNumbers:
            data = self.Data101FullV2XML(rn, IndCode, DateFrom, DateTo)
            for co in data.iter():
                if co.tag in ['FD', 'FDF']:
                    creditorg = {}
                    creditorg['RegNum'] = str(rn)
                    creditorg['IndCode'] = str(IndCode)
                    date = (
                    lambda x: getValue(x.find('DT')) if getValue(x.find('DT')) != '' else getValue(x.find('dt')))(co)
                    creditorg['Date'] = date
                    creditorg['value'] = getValue(co.find('val'))
                    creditorg['pln'] = getValue(co.find('pln'))
                    ap = (lambda x: getValue(x.find('AP')) if getValue(x.find('AP')) != '' else getValue(x.find('ap')))(
                        co)
                    creditorg['ap'] = ap
                    creditorg['vr'] = getValue(co.find('vr'))
                    creditorg['vv'] = getValue(co.find('vv'))
                    creditorg['vitg'] = getValue(co.find('vitg'))
                    creditorg['ora'] = getValue(co.find('ora'))
                    creditorg['ova'] = getValue(co.find('ova'))
                    creditorg['oitga'] = getValue(co.find('oitga'))
                    creditorg['orp'] = getValue(co.find('orp'))
                    creditorg['ovp'] = getValue(co.find('ovp'))
                    creditorg['oitgp'] = getValue(co.find('oitgp'))
                    creditorg['ir'] = getValue(co.find('ir'))
                    creditorg['iv'] = getValue(co.find('iv'))
                    creditorg['iitg'] = getValue(co.find('iitg'))
                    datalist.append(creditorg)

        return datalist

    def Data102FullList(self, CredOrgNumbers, SymbCode, DateFrom, DateTo):
        '''Данные КО. формы 102, кратко (как list of dict) по нескольким КО'''
        if isinstance(DateFrom, datetime):
            pass
        else:
            DateFrom = datetime.strptime(DateFrom, '%Y-%m-%d')

        if isinstance(DateTo, datetime):
            pass
        else:
            DateTo = datetime.strptime(DateTo, '%Y-%m-%d')
        if isinstance(CredOrgNumbers, list):
            pass
        else:
            CredOrgNumbers = list(CredOrgNumbers)

        datalist = []
        for rn in CredOrgNumbers:
            data = self.Data102FormXML(rn, SymbCode, DateFrom, DateTo)
            for co in data.iter():
                if co.tag in ['FD', 'FDF']:
                    creditorg = {}
                    creditorg['RegNum'] = str(rn)
                    creditorg['symbol'] = str(SymbCode)
                    creditorg['Date'] = getValue(co.find('DT'))
                    creditorg['value'] = getValue(co.find('val'))
                    datalist.append(creditorg)

        return datalist
