import numpy as np
from pandas import DataFrame, Series
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as s
import json
from . import cbrWebService


class Metrics:
    def __init__(self):
        self.__cbr = cbrWebService.CreditOrgInfo()
        self.__banks = [
            {'bic': cbrWebService.getValue(bank.find('BIC')), 'name': cbrWebService.getValue(bank.find('NM')),
             'RegNum': cbrWebService.getValue(bank.find('RN')),
             'intCode': cbrWebService.getValue(bank.find('intCode'))} for bank in
            self.__cbr.EnumBIC_XML().iter('BIC')
            if bank.text is None]

    def get_other_assets(self, regnums=None, DateFrom=None, DateTo=None):
        '''Прочие активы'''
        banks = self.__banks
        if regnums is not None:
            banks = [b for b in banks if b['RegNum'] in regnums]
        if DateFrom is None or DateTo is None:
            DateFrom = '2017-07-01'
            DateTo = DateFrom
        bankframe = pd.DataFrame(data=banks)
        bankframe = bankframe.apply(pd.to_numeric, errors='ignore')
        codes = ['20311', '20312', '44101', '44102', '44103', '44104', '44105', '44106', '44107', '44108', '44109',
                 '44201', '44202', '44203', '44204', '44205', '44206', '44207', '44208', '44209', '44210', '44301',
                 '44302',
                 '44303', '44304', '44305', '44306', '44307', '44308', '44309', '44310', '44401', '44402', '44403',
                 '44404',
                 '44405', '44406', '44407', '44408', '44409', '44410', '46001', '46002', '46003', '46004', '46005',
                 '46006',
                 '46007', '46101', '46102', '46103', '46104', '46105', '46106', '46107', '46201', '46202', '46203',
                 '46204',
                 '46205', '46206', '46207', '46301', '46302', '46303', '46304', '46305', '46306', '46307', '47801',
                 '47802',
                 '47803', '47901', '47402', '47410', '47701', '60315', '45801', '45802', '45803', '45804', '20317',
                 '20318',
                 '45901', '45902', '45903', '45904', '45905', '45906', '45907', '45908', '45909', '45910', '45911',
                 '45912',
                 '45913', '45914', '45915', '45916', '45917', '32501', '32502', '20319', '20320', '40311', '30202',
                 '30204',
                 '30211', '30228', '40308', '40310', '30215', '30602', '30605', '40313', '40908', '47404', '47406',
                 '47408',
                 '47413', '47415', '47417', '47420', '47423', '30235', '47431', '52601', '30221', '30222', '30233',
                 '30232',
                 '30302', '30304', '30306', '30301', '30303', '30305', '30413', '30416', '30417', '30418', '30419',
                 '30424',
                 '30425', '30427', '30420', '30421', '30422', '30423', '40109', '40108', '40111', '40110']

        speccodes = ['30221', '30222', '30233', '30232', '30302', '30304', '30306', '30301', '30303', '30305', '30413',
                     '30416',
                     '30417', '30418', '30419', '30424', '30425', '30427', '30420', '30421', '30422', '30423', '40109',
                     '40108',
                     '40111', '40110']

        data = [list(self.__cbr.Data101FullList(regnums, code, DateFrom, DateTo)) for code in codes]
        data = [i for e in data for i in e]
        frame = DataFrame(data)
        frame = frame.apply(pd.to_numeric, errors='ignore')
        frame.value = frame.value.fillna(frame.iitg)
        grouped = frame[~frame.IndCode.astype(str).isin(speccodes)].groupby(['RegNum', 'Date']).value.sum().astype(
            np.int64)
        pt = frame.pivot_table('value', index=['RegNum', 'Date'], columns='IndCode')
        pt[pt.columns.values] = pt[pt.columns.values].fillna(0).astype(np.int64)
        for x in speccodes:
            if int(x) not in pt.columns:
                pt[int(x)] = 0

        pt['other_assets'] = (np.where((pt[30221] - pt[30222]) > 0, (pt[30221] - pt[30222]), 0) +
                              np.where((pt[30233] - pt[30232]) > 0, (pt[30233] - pt[30232]), 0) +
                              np.where((pt[30302] + pt[30304] + pt[30306] - pt[30301] - pt[30303] - pt[30305]) > 0,
                                       (pt[30302] + pt[30304] + pt[30306] - pt[30301] - pt[30303] - pt[30305]), 0) +
                              np.where(
                                  (pt[30413] + pt[30416] + pt[30417] + pt[30418] + pt[30419] + pt[30424] + pt[30425] +
                                   pt[30427] - pt[30420] - pt[30421] - pt[30422] - pt[30423]) > 0,
                                  (pt[30413] + pt[30416] + pt[30417] + pt[30418] + pt[30419] + pt[30424] + pt[30425] +
                                   pt[30427] - pt[30420] - pt[30421] - pt[30422] - pt[30423]), 0) +
                              np.where((pt[40109] - pt[40108]) > 0, (pt[40109] - pt[40108]), 0) +
                              np.where((pt[40111] - pt[40110]) > 0, (pt[40111] - pt[40110]), 0)
                              ) + grouped

        pt = pt[['other_assets']]
        pt = pt.stack().reset_index(name='value')

        return pd.merge(pt, bankframe, on='RegNum')

    def highly_liquid_assets(self, regnums=None, DateFrom=None, DateTo=None):
        '''Высоколиквидные активы'''
        banks = self.__banks
        if regnums is not None:
            banks = [b for b in banks if b['RegNum'] in regnums]
        if DateFrom is None or DateTo is None:
            DateFrom = '2017-07-01'
            DateTo = DateFrom
        bankframe = pd.DataFrame(data=banks)
        bankframe = bankframe.apply(pd.to_numeric, errors='ignore')
        codes = ['20202', '20203', '20206', '20207', '20208', '20209', '20210', '30210',
                 '30102', '30104', '30106', '20302', '20303', '20305', '20308', '20401',
                 '20402', '20403', '30110', '30118', '30119', '30125', '30213', '30114']
        data = [list(self.__cbr.Data101FullList(regnums, code, DateFrom, DateTo)) for code in codes]
        data = [i for e in data for i in e]
        frame = DataFrame(data)
        frame = frame.apply(pd.to_numeric, errors='ignore')
        frame.value = frame.value.fillna(frame.iitg)
        grouped = frame.groupby(by=['RegNum', 'Date']).value.sum().unstack().stack().reset_index(name='value')
        grouped['IndCode'] = 'highly_liquid_assets'
        grouped['value'] = grouped['value'].astype(np.int64)

        return pd.merge(grouped, bankframe, on='RegNum')

    def interbank_loan(self, regnums=None, DateFrom=None, DateTo=None):
        '''Выданные МБК'''
        banks = self.__banks
        if regnums is not None:
            banks = [b for b in banks if b['RegNum'] in regnums]
        if DateFrom is None or DateTo is None:
            DateFrom = '2017-07-01'
            DateTo = DateFrom
        bankframe = pd.DataFrame(data=banks)
        bankframe = bankframe.apply(pd.to_numeric, errors='ignore')
        codes = ['20315', '20316', '32001', '32002', '32003', '32004', '32005', '32006', '32007', '32008', '32009',
                 '32010', '32201', '32202', '32203', '32204', '32205', '32206', '32207', '32208', '32209', '32101',
                 '32102', '32103', '32104', '32105', '32106', '32107', '32108', '32109', '32110', '32301', '32302',
                 '32303', '32304', '32305', '32306', '32307', '32308', '32309', '32401', '32402', '32902', '30224',
                 '30208', '31908', '31907', '31909', '31906', '31905', '31904', '31901', '31902', '31903']
        data = [list(self.__cbr.Data101FullList(regnums, code, DateFrom, DateTo)) for code in codes]
        data = [i for e in data for i in e]
        frame = DataFrame(data)
        frame = frame.apply(pd.to_numeric, errors='ignore')
        frame.value = frame.value.fillna(frame.iitg)
        grouped = frame.groupby(by=['RegNum', 'Date']).value.sum().unstack().stack().reset_index(name='value')
        grouped['IndCode'] = 'highly_liquid_assets'
        grouped['value'] = grouped['value'].astype(np.int64)

        return pd.merge(grouped, bankframe, on='RegNum')

    def investments_in_shares(self, regnums=None, DateFrom=None, DateTo=None):
        '''Вложения в акции'''
        banks = self.__banks
        if regnums is not None:
            banks = [b for b in banks if b['RegNum'] in regnums]
        if DateFrom is None or DateTo is None:
            DateFrom = '2017-07-01'
            DateTo = DateFrom
        bankframe = pd.DataFrame(data=banks)
        bankframe = bankframe.apply(pd.to_numeric, errors='ignore')
        codes = ['50605', '50606', '50607', '50608', '50618', '50620', '50621',
                 '50705', '50706', '50707', '50708', '50718', '50720', '50721', '50709']
        data = [list(self.__cbr.Data101FullList(regnums, code, DateFrom, DateTo)) for code in codes]
        data = [i for e in data for i in e]
        frame = DataFrame(data)
        frame = frame.apply(pd.to_numeric, errors='ignore')
        frame.value = frame.value.fillna(frame.iitg)
        grouped = frame[~frame.IndCode.astype(str).isin(['50620', '50720'])].groupby(
            ['RegNum', 'Date']).value.sum().astype(np.int64)
        pt = frame.pivot_table('value', index=['RegNum', 'Date'], columns='IndCode')
        pt[pt.columns.values] = pt[pt.columns.values].fillna(0).astype(np.int64)
        for x in ['50620', '50720']:
            if int(x) not in pt.columns:
                pt[int(x)] = 0
        pt['investments_in_shares'] = grouped - pt[50620] - pt[50720]
        pt = pt[['investments_in_shares']]
        pt = pt.stack().reset_index(name='value')

        return pd.merge(pt, bankframe, on='RegNum')

    def investments_in_bonds(self, regnums=None, DateFrom=None, DateTo=None):
        '''Вложения в облигации'''
        banks = self.__banks
        if regnums is not None:
            banks = [b for b in banks if b['RegNum'] in regnums]
        if DateFrom is None or DateTo is None:
            DateFrom = '2017-07-01'
            DateTo = DateFrom
        bankframe = pd.DataFrame(data=banks)
        bankframe = bankframe.apply(pd.to_numeric, errors='ignore')
        codes = ['50104', '50105', '50106', '50107', '50108', '50109', '50110', '50116', '50118',
                 '50120', '50121', '50205', '50206', '50207', '50208', '50209', '50210', '50211',
                 '50214', '50218', '50220', '50221', '50305', '50306', '50307', '50308', '50309',
                 '50310', '50311', '50313', '50318', '50505']
        data = [list(self.__cbr.Data101FullList(regnums, code, DateFrom, DateTo)) for code in codes]
        data = [i for e in data for i in e]
        frame = DataFrame(data)
        frame = frame.apply(pd.to_numeric, errors='ignore')
        frame.value = frame.value.fillna(frame.iitg)
        grouped = frame[~frame.IndCode.astype(str).isin(['50120', '50220'])].groupby(
            ['RegNum', 'Date']).value.sum().astype(np.int64)
        pt = frame.pivot_table('value', index=['RegNum', 'Date'], columns='IndCode')
        pt[pt.columns.values] = pt[pt.columns.values].fillna(0).astype(np.int64)
        for x in ['50120', '50220']:
            if int(x) not in pt.columns:
                pt[int(x)] = 0
        pt['investments_in_bonds'] = grouped - pt[50120] - pt[50220]
        pt = pt[['investments_in_bonds']]
        pt = pt.stack().reset_index(name='value')

        return pd.merge(pt, bankframe, on='RegNum')

    def investments_in_promissory_notes(self, regnums=None, DateFrom=None, DateTo=None):
        '''Вложения в векселя'''
        banks = self.__banks
        if regnums is not None:
            banks = [b for b in banks if b['RegNum'] in regnums]
        if DateFrom is None or DateTo is None:
            DateFrom = '2017-07-01'
            DateTo = DateFrom
        bankframe = pd.DataFrame(data=banks)
        bankframe = bankframe.apply(pd.to_numeric, errors='ignore')
        codes = ['51201', '51202', '51203', '51204', '51205', '51206', '51207', '51208',
                 '51209', '51301', '51302', '51303', '51304', '51305', '51306', '51307',
                 '51308', '51309', '51401', '51402', '51403', '51404', '51405', '51406',
                 '51407', '51408', '51409', '51501', '51502', '51503', '51504', '51505',
                 '51506', '51507', '51508', '51509', '51601', '51602', '51603', '51604',
                 '51605', '51606', '51607', '51608', '51609', '51701', '51702', '51703',
                 '51704', '51705', '51706', '51707', '51708', '51709', '51801', '51802',
                 '51803', '51804', '51805', '51806', '51807', '51808', '51809', '51901',
                 '51902', '51903', '51904', '51905', '51906', '51907', '51908', '51909']
        data = [list(self.__cbr.Data101FullList(regnums, code, DateFrom, DateTo)) for code in codes]
        data = [i for e in data for i in e]
        frame = DataFrame(data)
        frame = frame.apply(pd.to_numeric, errors='ignore')
        frame.value = frame.value.fillna(frame.iitg)
        grouped = frame.groupby(by=['RegNum', 'Date']).value.sum().unstack().stack().reset_index(name='value')
        grouped['IndCode'] = 'investments_in_promissory_notes'
        grouped['value'] = grouped['value'].astype(np.int64)

        return pd.merge(grouped, bankframe, on='RegNum')

    def Investments_in_other_organizations(self, regnums=None, DateFrom=None, DateTo=None):
        '''Вложения в капиталы других организаций'''
        banks = self.__banks
        if regnums is not None:
            banks = [b for b in banks if b['RegNum'] in regnums]
        if DateFrom is None or DateTo is None:
            DateFrom = '2017-07-01'
            DateTo = DateFrom
        bankframe = pd.DataFrame(data=banks)
        bankframe = bankframe.apply(pd.to_numeric, errors='ignore')
        codes = ['60101', '60102', '60103', '60104', '60201', '60202', '60203', '60204', '60205', '60106']
        data = [list(self.__cbr.Data101FullList(regnums, code, DateFrom, DateTo)) for code in codes]
        data = [i for e in data for i in e]
        frame = DataFrame(data)
        frame = frame.apply(pd.to_numeric, errors='ignore')
        frame.value = frame.value.fillna(frame.iitg)
        grouped = frame.groupby(by=['RegNum', 'Date']).value.sum().unstack().stack().reset_index(name='value')
        grouped['IndCode'] = 'Investments_in_other_organizations'
        grouped['value'] = grouped['value'].astype(np.int64)

        return pd.merge(grouped, bankframe, on='RegNum')

    def loans_to_individuals(self, regnums=None, DateFrom=None, DateTo=None):
        '''Кредиты физическим лицам'''
        banks = self.__banks
        if regnums is not None:
            banks = [b for b in banks if b['RegNum'] in regnums]
        if DateFrom is None or DateTo is None:
            DateFrom = '2017-07-01'
            DateTo = DateFrom
        bankframe = pd.DataFrame(data=banks)
        bankframe = bankframe.apply(pd.to_numeric, errors='ignore')
        codes = ['45502', '45503', '45504', '45508', '45701',
                 '45702', '45703', '45707', '45505', '45704',
                 '45506', '45705', '45507', '45706', '45509',
                 '45708', '45510', '45709', '45815', '45817']
        data = [list(self.__cbr.Data101FullList(regnums, code, DateFrom, DateTo)) for code in codes]
        data = [i for e in data for i in e]
        frame = DataFrame(data)
        frame = frame.apply(pd.to_numeric, errors='ignore')
        frame.value = frame.value.fillna(frame.iitg)
        grouped = frame.groupby(by=['RegNum', 'Date']).value.sum().unstack().stack().reset_index(name='value')
        grouped['IndCode'] = 'Investments_in_other_organizations'
        grouped['value'] = grouped['value'].astype(np.int64)

        return pd.merge(grouped, bankframe, on='RegNum')

    def loans_to_businesses(self, regnums=None, DateFrom=None, DateTo=None):
        '''Кредиты предприятиям и организациям'''
        banks = self.__banks
        if regnums is not None:
            banks = [b for b in banks if b['RegNum'] in regnums]
        if DateFrom is None or DateTo is None:
            DateFrom = '2017-07-01'
            DateTo = DateFrom
        bankframe = pd.DataFrame(data=banks)
        bankframe = bankframe.apply(pd.to_numeric, errors='ignore')
        codes = ['45103', '45104', '45105', '45109', '45203', '45204', '45205', '45209', '45601', '45602',
                 '45603', '45607', '47001', '47002', '47003', '47004', '47101', '47102', '47103', '47104',
                 '47301', '47302', '47303', '47304', '44703', '44704', '44705', '44709', '45003', '45004',
                 '45005', '45009', '45303', '45304', '45305', '45309', '46601', '46602', '46603', '46604',
                 '46901', '46902', '46903', '46904', '47201', '47202', '47203', '47204', '44503', '44504',
                 '44505', '44509', '44603', '44604', '44605', '44609', '44803', '44804', '44805', '44809',
                 '44903', '44904', '44905', '44909', '46401', '46402', '46403', '46404', '46501', '46502',
                 '46503', '46504', '46701', '46702', '46703', '46704', '46801', '46802', '46803', '46804',
                 '45403', '45404', '45405', '45409', '45106', '45206', '45604', '47005', '47105', '47305',
                 '44706', '45006', '45306', '46605', '46905', '47205', '44506', '44606', '44806', '44906',
                 '46405', '46505', '46705', '46805', '45406', '45107', '45207', '45605', '47006', '47106',
                 '47306', '44707', '45007', '45307', '46606', '46906', '47206', '44507', '44607', '44807',
                 '44907', '46406', '46506', '46706', '46806', '45407', '45108', '45208', '45606', '47007',
                 '47107', '47307', '44708', '45008', '45308', '46607', '46907', '47207', '44508', '44608',
                 '44808', '44908', '46407', '46507', '46707', '46807', '45408', '44501', '44601', '44701',
                 '44801', '44901', '45001', '45101', '45201', '45301', '45608', '45401', '45410', '45805',
                 '45806', '45807', '45808', '45809', '45810', '45811', '45812', '45813', '45816', '45814']
        data = [list(self.__cbr.Data101FullList(regnums, code, DateFrom, DateTo)) for code in codes]
        data = [i for e in data for i in e]
        frame = DataFrame(data)
        frame = frame.apply(pd.to_numeric, errors='ignore')
        frame.value = frame.value.fillna(frame.iitg)
        grouped = frame.groupby(by=['RegNum', 'Date']).value.sum().unstack().stack().reset_index(name='value')
        grouped['IndCode'] = 'loans_to_businesses'
        grouped['value'] = grouped['value'].astype(np.int64)

        return pd.merge(grouped, bankframe, on='RegNum')

    def intangible_assets(self, regnums=None, DateFrom=None, DateTo=None):
        '''Основные средства и нематериальные активы'''
        banks = self.__banks
        if regnums is not None:
            banks = [b for b in banks if b['RegNum'] in regnums]
        if DateFrom is None or DateTo is None:
            DateFrom = '2017-07-01'
            DateTo = DateFrom
        bankframe = pd.DataFrame(data=banks)
        bankframe = bankframe.apply(pd.to_numeric, errors='ignore')
        codes = ['60401', '60404', '60415', '61901', '61902', '61903', '61904',
                 '61907', '61908', '61905', '61906', '61911', '60804', '60901',
                 '60905', '60906', '61002', '61008', '61009', '61010', '61909',
                 '61910', '60805', '60903', '60414', '61912']
        data = [list(self.__cbr.Data101FullList(regnums, code, DateFrom, DateTo)) for code in codes]
        data = [i for e in data for i in e]
        frame = DataFrame(data)
        frame = frame.apply(pd.to_numeric, errors='ignore')
        frame.value = frame.value.fillna(frame.iitg)
        grouped = frame[
            ~frame.IndCode.astype(str).isin(['61909', '61910', '60805', '60903', '60414', '61912'])].groupby(
            ['RegNum', 'Date']).value.sum().astype(np.int64)
        pt = frame.pivot_table('value', index=['RegNum', 'Date'], columns='IndCode')
        pt[pt.columns.values] = pt[pt.columns.values].fillna(0).astype(np.int64)
        for x in ['61909', '61910', '60805', '60903', '60414', '61912']:
            if int(x) not in pt.columns:
                pt[int(x)] = 0
        pt['intangible assets'] = grouped - pt[61909] - pt[61910] - pt[60805] - pt[60903] - pt[60414] - pt[61912]
        pt = pt[['intangible assets']]
        pt = pt.stack().reset_index(name='value')

        return pd.merge(pt, bankframe, on='RegNum')
