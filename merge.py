import json

import xmltodict

from goose import goose
from mms import mms


# scd_arr = ['Microgrid_20241015_Reference Scenario.scd']

# for scd in scd_arr:
def merge_scd(scd):
    goose_obj = goose(scd)
    mms_obj = mms(scd)
    data_obj = {}
    print(scd)
    ied_name_arr = []
    with open(scd, encoding='utf8') as file:
        parser_data = xmltodict.parse(file.read())
        for ie_key, ied in enumerate(parser_data['SCL']['IED']):
            ied_name_arr.append(ied['@name'])

    for i in ied_name_arr:
        print()
        print('IED:', i)
        if i not in data_obj:
            data_obj[i] = {
                'goose': [],
                'mms': [],
            }

        if i in goose_obj:
            data_obj[i]['goose'] = goose_obj[i]

            for g in goose_obj[i]:

                print('  GOOSE')
                for gg in g:
                    if type(g[gg]) == dict:
                        print(f'    {gg}:')
                        for ggg in g[gg]:
                            print(f'       {ggg}:', g[gg][ggg])
                    else:
                        print(f'    {gg}:', g[gg])
        if i in mms_obj:
            data_obj[i]['mms'] = mms_obj[i]
            for m in mms_obj[i]:
                # print(m)

                print('  MMS')
                for mm in m:
                    print(f'    {mm}:', m[mm])

    with open(scd + '.json', "w") as json_file:
        json.dump(data_obj, json_file)
