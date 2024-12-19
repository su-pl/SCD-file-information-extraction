import json
import yaml


def mms(scd_path):
    mms_obj = {}
    with open('report/yaml/' + scd_path + '.yaml', 'r') as file:
        yaml_data = yaml.safe_load(file.read())

    with open('OptFields.yaml', 'r') as file:
        OptFields_yaml_data = yaml.safe_load(file.read())

    with open('report/json/' + scd_path + '.json', 'r') as file:
        json_data = json.loads(file.read())
        for item in json_data:

            if 'fcda' in item and len(item['fcda']) > 0:
                print()
                print('MMS')
                print(' IEDName:', item['IEDName'])
                if item['IEDName'] not in mms_obj:
                    mms_obj[item['IEDName']] = []
                obj = {}
                total = 0

                if 'ReportControl' in item:
                    if 'RptEnabled' in item['ReportControl'] and 'ClientLN' in item['ReportControl'][
                        'RptEnabled']:
                        aa_a = []
                        if type(item['ReportControl']['RptEnabled']['ClientLN']) == list:
                            for aaa in item['ReportControl']['RptEnabled']['ClientLN']:
                                if 'iedName' in aaa:
                                    aa_a.append(aaa['iedName'])

                            print(' ClientLN:', ','.join(aa_a))
                            obj['ClientLN'] = ','.join(aa_a)
                        else:
                            if 'iedName' in item['ReportControl']['RptEnabled']['ClientLN']:
                                print(' ClientLN:', item['ReportControl']['RptEnabled']['ClientLN']['iedName'])
                                obj['ClientLN'] = item['ReportControl']['RptEnabled']['ClientLN']['iedName']
                    if 'intgPd' in item['ReportControl']:
                        print(' intgPd:', item['ReportControl']['intgPd'])
                        obj['intgPd'] = item['ReportControl']['intgPd']
                    if 'rptID' in item['ReportControl']:
                        total += len(item['ReportControl']['rptID']) + 2

                    # 直接加 5
                    total += 5

                    if 'OptFields' in item['ReportControl']:

                        for opt in item['ReportControl']['OptFields']:
                            if item['ReportControl']['OptFields'][opt] == 'true':
                                if opt in OptFields_yaml_data:
                                    total += OptFields_yaml_data[opt]

                for fa in item['fcda']:
                    # print(fd)
                    for ff in fa:
                        for fa1 in ff.split(','):
                            ft = fa1.replace('Struct(', '').replace(')', '')
                            if ft in yaml_data:
                                total += yaml_data[ft] + 2
                    total += 2
                total += 5
                total += 6
                total += 4
                total += 4
                # between MMS and TCP
                total += 15
                total += 2
                total += 2
                total += 3
                total += 4
                print(' sendBytes:', total)
                obj['sendBytes'] = total
                mms_obj[item['IEDName']].append(obj)

    # print(mms_obj)

    return mms_obj


# scd_arr = ['Microgrid_20241015_Reference Scenario.scd']
#
# for i in scd_arr:
#     mms(i)
