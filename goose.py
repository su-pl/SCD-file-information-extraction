import json
import yaml


def goose(scd_path):
    goose_obj = {}
    with open('gse/yaml/' + scd_path + '.yaml', 'r') as file:
        yaml_data = yaml.safe_load(file.read())

    with open('gse/json/' + scd_path + '.json', 'r') as file:
        json_data = json.loads(file.read())

        for i in json_data:
            # print(yaml_data)
            gse_obj = i
            print('GOOSE')
            print('  IEDName：', gse_obj['IED Name'])
            obj = {}
            if 'Receiver' in gse_obj:
                print('  Receiver：', gse_obj['Receiver'])
                obj['Receiver'] = gse_obj['Receiver']
            if gse_obj['IED Name'] not in goose_obj:
                goose_obj[gse_obj['IED Name']] = []

            for cm in gse_obj['Communication']:
                if cm == 'APPID':
                    obj[cm.replace("-", "")] = '0x' + gse_obj['Communication'][cm].replace('-', '')
                    print(f'  {cm.replace("-", "")}：', '0x' + gse_obj['Communication'][cm].replace('-', ''))
                else:
                    obj[cm.replace("-", "")] = gse_obj['Communication'][cm].replace('-', '')
                    print(f'  {cm.replace("-", "")}：', gse_obj['Communication'][cm].replace('-', ''))

            print('  goosePdu：')
            obj['goosePdu'] = {}
            print('     gocbRef：',
                  gse_obj['IED Name'] + gse_obj['LDevice inst'] + '/LLN0$GO$' + gse_obj['GSEControl'][
                      'name'])
            obj['goosePdu']['gocbRef'] = gse_obj['IED Name'] + gse_obj['LDevice inst'] + '/LLN0$GO$' + \
                                         gse_obj['GSEControl']['name']
            if 'Communication' in gse_obj and 'MaxTime' in gse_obj['Communication']:
                print('     timeAllowedtoLive：', gse_obj['Communication']['MaxTime'])
                obj['goosePdu']['timeAllowedtoLive'] = gse_obj['Communication']['MaxTime']
            else:
                print('     timeAllowedtoLive：', '')
                obj['goosePdu']['timeAllowedtoLive'] = ''

            print('     datSet：', gse_obj['GSEControl']['datSet'])
            obj['goosePdu']['datSet'] = gse_obj['GSEControl']['datSet']

            print('     goID：', gse_obj['GSEControl']['appID'])
            obj['goosePdu']['goID'] = gse_obj['GSEControl']['appID']
            print('     confRev：', gse_obj['GSEControl']['confRev'])
            obj['goosePdu']['confRev'] = gse_obj['GSEControl']['confRev']

            print('     numDatSetEntries：', gse_obj['numDatSetEntries'])
            obj['goosePdu']['numDatSetEntries'] = gse_obj['numDatSetEntries']
            fcda_num = 0
            for fa in gse_obj['fcda']:
                for i in fa:
                    # print(i)
                    for fa1 in i.split(','):
                        ft = fa1.replace('Struct(', '').replace(')', '')
                        if ft in yaml_data:
                            fcda_num += yaml_data[ft] + 2
                fcda_num += 2
            print('     allData：', fcda_num)
            obj['goosePdu']['allData'] = fcda_num
            # print(i)
            goose_obj[gse_obj['IED Name']].append(obj)

    # print(goose_obj)
    return goose_obj


# scd_arr = ['Microgrid_20241015_Reference Scenario.scd']
# for scd in scd_arr:
#     print(scd)
#     goose(scd)
