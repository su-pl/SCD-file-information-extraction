import xmltodict
import json
import yaml
import os

from goose import goose
from ini import ini_scd
from merge import merge_scd
from mms import mms

_type_arr = []

fcda = []


def read_scd(scd_path, json_type):
    global _type_arr

    _type_arr = []

    with open(scd_path, encoding='utf8') as file:

        parser_data = xmltodict.parse(file.read())

        file.close()

        def da_val(_id, _type='DAType'):
            if _type == 'DAType':
                for _da in parser_data['SCL']['DataTypeTemplates'][_type]:
                    if _da['@id'] == _id:
                        if type(_da) != list:
                            if type(_da['BDA']) != list:
                                if _da['BDA']['@bType'] == 'Struct':
                                    return da_val(_da['BDA']['@type'], 'DAType')

                                elif _da['BDA']['@bType'] == 'Enum':
                                    return da_val(_da['BDA']['@type'], 'EnumType')

                                return _da['BDA']['@bType']

                            else:
                                ll = []
                                for bda in _da['BDA']:
                                    ll.append(da_val(bda['@type'], _type))
                                return ll
                        else:
                            print('+++++++++++++++')
                            return ''

            if _type == 'EnumType':
                for eType in parser_data['SCL']['DataTypeTemplates'][_type]:
                    if eType['@id'] == _id:
                        if len(eType['EnumVal']) > 256:
                            return 'Enum = 2byte'
                        else:
                            return 'Enum = 1byte'

        def do_val(parser_data, _id, _ke):

            for dot in parser_data['SCL']['DataTypeTemplates']['DOType']:

                if dot['@id'] == _id:
                    # print(dot)
                    ll = []
                    if 'DA' in dot:
                        arr = dot['DA']
                        if type(dot['DA']) != list:
                            arr = [dot['DA']]

                        for da in arr:
                            _ty = ''
                            _num = ''
                            if '@daName' in fa:
                                if '@name' in da:
                                    if da['@name'] == fa['@daName']:
                                        if da['@bType'] == 'Struct':
                                            _ty = da['@type']
                                        elif da['@bType'] == 'Enum':
                                            _num = da['@type']
                                        else:
                                            ll.append(da['@bType'])
                            elif '@fc' in fa:
                                if '@fc' in da:
                                    if da['@fc'] == fa['@fc']:
                                        if da['@bType'] == 'Struct':
                                            _ty = da['@type']
                                        elif da['@bType'] == 'Enum':
                                            _num = da['@type']
                                        else:
                                            ll.append(da['@bType'])

                            if _ty != '':
                                res = da_val(_ty, 'DAType')
                                if type(res) == list:
                                    for rr in res:
                                        ll.append('Struct(' + rr + ')')
                                else:
                                    ll.append('Struct(' + res + ')')

                            if _num != '':
                                ll.append(da_val(_num, 'EnumType'))

                    if len(ll) == 0:
                        if 'SDO' in dot:
                            sdo = [dot['SDO']]
                            if type(dot['SDO']) == list:
                                sdo = dot['SDO']
                            for sd in sdo:
                                # print(sd)
                                if '@type' in sd:
                                    # print(sd['@type'])
                                    ll.append(_format2(sd['@type'], fa))
                    global _type_arr
                    _type_arr = _type_arr + ll

                    global fcda
                    fcda.append(ll)

                    print('FCDA' + str(_ke) + ':', ','.join(ll))

        def _format3(parser_data, _id, name, _ke):
            for dot in parser_data['SCL']['DataTypeTemplates']['DOType']:

                if dot['@id'] == _id:

                    sdo = [dot['SDO']]
                    if type(dot['SDO']) == list:
                        sdo = dot['SDO']

                    for sd in sdo:
                        if sd['@name'] == name:
                            do_val(parser_data, sd['@type'], _ke)

        #
        def _format2(__type, fa):
            for dot in parser_data['SCL']['DataTypeTemplates']['DOType']:
                if dot['@id'] == __type:
                    if 'DA' in dot:
                        arr = dot['DA']
                        if type(dot['DA']) != list:
                            arr = [dot['DA']]
                        ll = []
                        for da in arr:
                            _ty = ''
                            _num = ''
                            if '@fc' in fa:
                                if '@fc' in da:
                                    if da['@fc'] == fa['@fc']:
                                        if da['@bType'] == 'Struct':
                                            _ty = da['@type']
                                        elif da['@bType'] == 'Enum':
                                            _num = da['@type']
                                        else:
                                            ll.append(da['@bType'])

                            if _ty != '':
                                ress = da_val(_ty, 'DAType')
                                if type(ress) == list:
                                    for rs in ress:
                                        ll.append('Struct(' + rs + ')')
                                else:
                                    ll.append('Struct(' + ress + ')')

                            if _num != '':
                                ll.append(da_val(_num, 'EnumType'))

                        return ','.join(ll)

        #
        def _format1(_ke, fa, data):

            for __ld in data:

                if __ld['@inst'] == fa['@ldInst']:
                    ln_data = []

                    if 'LN0' in __ld:
                        ln_data = ln_data + [__ld['LN0']]

                    if 'LN' in __ld:
                        ln_data = ln_data + __ld['LN']

                    for ln in ln_data:

                        flag = True
                        if '@prefix' in fa and '@prefix' in ln:
                            if fa['@prefix'] == ln['@prefix']:
                                flag = True
                            else:
                                flag = False

                        inst_flag = True
                        if '@lnInst' in fa and '@inst' in ln:
                            if fa['@lnInst'] == ln['@inst']:
                                inst_flag = True
                            else:
                                inst_flag = False

                        class_flag = True
                        if '@lnClass' in ln and '@lnClass' in fa:
                            if fa['@lnClass'] == ln['@lnClass']:
                                class_flag = True
                            else:
                                class_flag = False

                        if class_flag and inst_flag and flag:

                            stDoName = fa['@doName']
                            edDoName = ''

                            if '.' in fa['@doName']:
                                stDoName = fa['@doName'].split('.')[0]
                                edDoName = fa['@doName'].split('.')[1]

                            for lnt in parser_data['SCL']['DataTypeTemplates']['LNodeType']:

                                if ln['@lnType'] == lnt['@id']:
                                    doo = [lnt['DO']]
                                    if type(lnt['DO']) == list:
                                        doo = lnt['DO']

                                    for do in doo:
                                        if do['@name'] == stDoName:
                                            if edDoName == '':
                                                # print(do)
                                                do_val(parser_data, do['@type'], _ke)
                                            else:
                                                _format3(parser_data, do['@type'], edDoName, _ke)

        g_data = []
        re_data = []

        for ie_key, ied in enumerate(parser_data['SCL']['IED']):

            ld_data = [ied['AccessPoint']['Server']['LDevice']]
            if type(ied['AccessPoint']['Server']['LDevice']) == list:
                ld_data = ied['AccessPoint']['Server']['LDevice']

            for _k, _id in enumerate(ld_data):
                global fcda
                if 'ReportControl' in _id['LN0'] and json_type == 'report':
                    json_type = 'report'
                    if type(_id['LN0']['ReportControl']) == list:
                        data = _id['LN0']['ReportControl']
                    else:
                        data = [_id['LN0']['ReportControl']]

                    for r_key, report in enumerate(data):

                        report_json = {
                            'IEDName': ied['@name'],
                            'ReportControl': {},
                        }

                        fcda = []

                        # print('IED:', ie_key)
                        # print('ReportControl:', r_key)

                        # print(report)
                        print('---------------------------------')
                        print('IED Name:', ied['@name'])
                        print('AccessPoint name:', ied['AccessPoint']['@name'])
                        print('LDevice inst:', _id['@inst'])

                        print('<ReportControl>:')
                        for rp in report:
                            if '@' in rp:
                                print('  ' + rp.replace('@', '') + ':', report[rp])
                                report_json['ReportControl'][rp.replace('@', '')] = report[rp]
                            elif '#' in rp:
                                print('  ' + rp.replace('#', '') + ':', report[rp])
                            else:
                                if report[rp] is not None:
                                    print('  <' + rp + '>:')
                                    if rp == 'OptFields' or rp == 'RptEnabled':
                                        report_json['ReportControl'][rp] = {}

                                    for rpp in report[rp]:
                                        if '@' in rpp:
                                            if rp == 'OptFields' or rp == 'RptEnabled':
                                                report_json['ReportControl'][rp][rpp.replace('@', '')] = report[rp][rpp]
                                            print('    ' + rpp.replace('@', '') + ':', report[rp][rpp])
                                        elif '#' in rpp:
                                            print('    ' + rpp.replace('#', '') + ':', report[rp][rpp])
                                        else:

                                            if rp == 'OptFields' or rp == 'RptEnabled':
                                                report_json['ReportControl'][rp][rpp] = {}

                                            print('    <' + rpp + '>:')

                                            for rppp in report[rp][rpp]:
                                                if '@' in rppp:
                                                    if rp == 'OptFields' or rp == 'RptEnabled':
                                                        report_json['ReportControl'][rp][rpp][rppp.replace('@', '')] = \
                                                            report[rp][rpp][rppp]
                                                    print('      ' + rppp.replace('@', '') + ':', report[rp][rpp][rppp])
                                                elif '#' in rppp:
                                                    print('      ' + rppp.replace('#', '') + ':', report[rp][rpp][rppp])
                                                else:

                                                    # print(report[rp][rpp])

                                                    if type(rppp) == dict:
                                                        if rp == 'OptFields' or rp == 'RptEnabled':
                                                            if type(report_json['ReportControl'][rp][rpp]) != list:
                                                                report_json['ReportControl'][rp][rpp] = []
                                                        obj1 = {}
                                                        for ap in rppp:
                                                            if '@' in ap:
                                                                obj1[ap.replace('@', '')] = rppp[ap]
                                                                print('      ' + ap.replace('@', '') + ':', rppp[ap])
                                                            elif '#' in ap:
                                                                obj1[ap.replace('#', '')] = rppp[ap]
                                                                print('      ' + ap.replace('#', '') + ':', rppp[ap])
                                                        report_json['ReportControl'][rp][rpp].append(obj1)

                        if 'DataSet' in _id['LN0']:

                            if type(_id['LN0']['DataSet']) == list:
                                data = _id['LN0']['DataSet']
                            else:
                                data = [_id['LN0']['DataSet']]

                            for ds in data:

                                if '@datSet' in report and ds['@name'] == report['@datSet']:
                                    # print(report, '++++++++++')
                                    # print(ds, '++++++++++')
                                    # print(report)

                                    if 'FCDA' in ds:

                                        fda = [ds['FCDA']]
                                        if type(ds['FCDA']) == list:
                                            fda = ds['FCDA']

                                        print('numDatSetEntries:', len(fda))

                                        report_json['numDatSetEntries'] = len(fda)
                                        for ke, fa in enumerate(fda):
                                            # print(fa)
                                            # print(ke, 'ke+++++++++++++++++')
                                            # print(fa, 'ke+++++++++++++++++')
                                            _format1(ke, fa, ld_data)
                            report_json['fcda'] = fcda

                        re_data.append(report_json)
                if 'GSEControl' in _id['LN0'] and json_type == 'gse':
                    json_type = 'gse'
                    # print(_id['LN0']['GSEControl'])
                    # Communication
                    #
                    gse_data = [_id['LN0']['GSEControl']]
                    if type(_id['LN0']['GSEControl']) == list:
                        gse_data = _id['LN0']['GSEControl']

                    for k, gse in enumerate(gse_data):
                        print('---------------------------------')

                        fcda = []
                        # print(gse['@datSet'])
                        gse_obj = {
                            'IED Name': ied['@name'],
                            'LDevice inst': _id['@inst'],
                            'GSEControl': {},
                        }
                        print('IED Name:', ied['@name'])
                        print('AccessPoint Name:', ied['AccessPoint']['@name'])
                        print('LDevice inst:', _id['@inst'])
                        # print(gse)

                        # print(gse)
                        print('<GSEControl>:')

                        for ge in gse:
                            if '@' in ge:
                                gse_obj['GSEControl'][ge.replace('@', '')] = gse[ge]
                                print('  ' + ge.replace('@', '') + ':', gse[ge])
                            elif '#' in ge:

                                print('  ' + ge.replace('#', '') + ':', gse[ge])
                            else:
                                if gse[ge] is not None:
                                    print('  <' + ge + '>:')
                                    print(gse[ge])
                                    if ge == 'IEDName':
                                        gse_obj['Receiver'] = []
                                    if type(gse[ge]) == list:
                                        for gi in gse[ge]:
                                            for ggi in gi:

                                                if '@' in ggi:
                                                    print('    ' + ggi.replace('@', '') + ':', gi[ggi])
                                                elif '#' in ggi:
                                                    if ge == 'IEDName':
                                                        gse_obj['Receiver'].append(gi[ggi])
                                                    print('    ' + ggi.replace('#', '') + ':', gi[ggi])
                                    else:
                                        for gee in gse[ge]:

                                            if '@' in gee:
                                                print('    ' + gee.replace('@', '') + ':', gse[ge][gee])
                                            elif '#' in gee:
                                                if ge == 'IEDName':
                                                    gse_obj['Receiver'].append(gse[ge][gee])
                                                print('    ' + gee.replace('#', '') + ':', gse[ge][gee])
                                            else:

                                                if gse[ge][gee] is not None:
                                                    print('    <' + gee + '>:')
                                                    for gee1 in gse[ge][gee]:

                                                        if '@' in gee1:
                                                            print('      ' + gee1.replace('@', '') + ':',
                                                                  gse[ge][gee][gee1])
                                                        elif '#' in gee1:
                                                            print('      ' + gee1.replace('#', '') + ':',
                                                                  gse[ge][gee][gee1])
                                                        else:
                                                            if gse[ge][gee][gee1] is not None:
                                                                print('        <' + gee1 + '>:')
                                                                for gee2 in gse[ge][gee][gee1]:

                                                                    if '@' in gee2:
                                                                        print(
                                                                            '          ' + gee2.replace('@', '') + ':',
                                                                            gse[ge][gee][gee1][gee2])
                                                                    elif '#' in gee2:
                                                                        print(
                                                                            '          ' + gee2.replace('#', '') + ':',
                                                                            gse[ge][gee][gee1][gee2])
                                                                    else:
                                                                        if gse[ge][gee][gee1][gee2] is not None:
                                                                            print('          <' + gee2 + '>:')
                                                                            for gee3 in gse[ge][gee][gee1][gee2]:

                                                                                if '@' in gee3:
                                                                                    print(
                                                                                        '          ' + gee3.replace('@',
                                                                                                                    '') + ':',
                                                                                        gse[ge][gee][gee1][gee2][gee3])
                                                                                elif '#' in gee3:
                                                                                    print('            ' + gee3.replace(
                                                                                        '#',
                                                                                        '') + ':',
                                                                                          gse[ge][gee][gee1][gee2][
                                                                                              gee3])
                                                                                else:
                                                                                    if type(gee3) == dict:
                                                                                        if '@type' in gee3 and '#text' in gee3:
                                                                                            print('            ' + gee3[
                                                                                                '@type'] + ':' + gee3[
                                                                                                      '#text'])
                                    if ge == 'IEDName':
                                        gse_obj['Receiver'] = ','.join(gse_obj['Receiver'])
                        for com in parser_data['SCL']['Communication']['SubNetwork']['ConnectedAP']:
                            if 'GSE' in com and com['@iedName'] == ied['@name'] and com['@apName'] == \
                                    ied['AccessPoint'][
                                        '@name']:
                                gse_com = [com['GSE']]
                                if type(com['GSE']) == list:
                                    gse_com = com['GSE']
                                for gsm in gse_com:
                                    if gsm['@cbName'] == gse['@name'] and _id['@inst'] == gsm['@ldInst']:
                                        # print(gsm)
                                        if 'Address' in gsm:
                                            print('<Communication>:')
                                            gse_obj['Communication'] = {}
                                            for pp in gsm['Address']['P']:
                                                gse_obj['Communication'][pp['@type']] = pp['#text']
                                                print('  ' + pp['@type'] + ':', pp['#text'])
                                        if 'MinTime' in gsm:
                                            gse_obj['Communication']['MinTime'] = gsm['MinTime']['#text']
                                            print('  MinTime:',
                                                  gsm['MinTime']['#text'] + gsm['MinTime']['@multiplier'] +
                                                  gsm['MinTime'][
                                                      '@unit'])
                                        if 'MaxTime' in gsm:
                                            gse_obj['Communication']['MaxTime'] = gsm['MaxTime']['#text']
                                            print('  MaxTime:',
                                                  gsm['MaxTime']['#text'] + gsm['MaxTime']['@multiplier'] +
                                                  gsm['MaxTime'][
                                                      '@unit'])
                        if 'DataSet' in _id['LN0']:
                            dt = [_id['LN0']['DataSet']]
                            if type(_id['LN0']['DataSet']) == list:
                                dt = _id['LN0']['DataSet']
                            for ds in dt:
                                if ds['@name'] == gse['@datSet']:
                                    # print(ds)
                                    if 'FCDA' in ds:

                                        fda = [ds['FCDA']]
                                        if type(ds['FCDA']) == list:
                                            fda = ds['FCDA']
                                        print('numDatSetEntries:', len(fda))
                                        gse_obj['numDatSetEntries'] = len(fda)
                                        for ke, fa in enumerate(fda):
                                            _format1(ke, fa, ld_data)
                            gse_obj['fcda'] = fcda
                        # print(gse_obj)

                        # print('GOOSE信息如下==================')
                        # print('GOOSE')
                        # print('  APPID：', '0x' + gse_obj['Communication']['APPID'])
                        # print('  goosePdu：')
                        # print('     gocbRef：',
                        #       gse_obj['IED Name'] + gse_obj['LDevice inst'] + '/LLN0$GO$' + gse_obj['GSEControl'][
                        #           'name'])
                        # print('     timeAllowedtoLive：', gse_obj['Communication']['MaxTime'])
                        # print('     datSet：', gse_obj['GSEControl']['datSet'])
                        # print('     goID：', gse_obj['GSEControl']['appID'])
                        # print('     confRev：', gse_obj['GSEControl']['confRev'])
                        # print('     numDatSetEntries：', gse_obj['numDatSetEntries'])
                        # print('     allData：', 2580)
                        g_data.append(gse_obj)

                    print('====')

        os.makedirs(json_type + '/json', exist_ok=True)

        with open(json_type + '/json/' + scd_path + '.json', "w") as json_file:
            if json_type == 'gse':
                json.dump(g_data, json_file)
            else:
                json.dump(re_data, json_file)

        _type_arr = list(set(_type_arr))
        _type_obj = {}
        for tt in _type_arr:
            if ',' in tt:
                for a in tt.split(','):
                    if a.replace('Struct(', '').replace(')', '') not in _type_obj:
                        _type_obj[a] = 1
            else:
                if tt.replace('Struct(', '').replace(')', '') not in _type_obj:
                    _type_obj[tt.replace('Struct(', '').replace(')', '')] = 1

        os.makedirs(json_type + '/yaml', exist_ok=True)

        if not os.path.exists(json_type + '/yaml/' + scd_path + '.yaml'):
            with open(json_type + '/yaml/' + scd_path + '.yaml', "w") as yaml_file:
                yaml.dump(_type_obj, yaml_file)


scd_arr = ['Microgrid_FCkind_50.scd']
for scd_name in scd_arr:
    read_scd(scd_name, 'report')
    read_scd(scd_name, 'gse')
    goose(scd_name)
    mms(scd_name)
    merge_scd(scd_name)
    ini_scd(scd_name)

