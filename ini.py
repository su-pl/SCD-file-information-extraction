import json


# Hexadecimal addition
def hex_addition(hex_num1):
    hex_2 = f'{hex(int(hex_num1, 16) + int("0x01", 16))[2:]}'.upper()
    if len(hex_2) == 1:
        hex_2 = '0' + hex_2
    return hex_2


def ini_scd(scd):
    go1_n1 = '00'

    go1_n2 = '00'

    go_n1 = '00'

    go_n2 = '00'

    arr = []

    js = {}

    ap = {}
    app1 = {}

    moc = {}

    with open(scd+'.json', 'r') as f:
        data = json.loads(f.read())
        for ii in data:
            for gk, go in enumerate(data[ii]['goose']):
                for re in go["Receiver"].split(','):
                    if re not in js:
                        js[re] = {}

                    if ii not in js[re]:
                        js[re][ii] = []

                        js[re][ii].append(f'"01 0C CD 01 {go1_n1} {go1_n2}"')

            if go1_n2 == 'FF':
                go1_n1 = hex_addition(go1_n1)
                go1_n2 = '00'
            else:
                go1_n2 = hex_addition(go1_n2)

            for mk, mo in enumerate(data[ii]['mms']):

                if mo['ClientLN'] not in ap:
                    ap[mo['ClientLN']] = []
                ap[mo['ClientLN']].append('')

    with open(scd+'.json', 'r') as f:
        data = json.loads(f.read())

        for ii in data:
            # print(data[ii]['goose'])
            arr.append('#' + ii)
            if ii in js:
                ad = []
                for ij in js[ii]:
                    ad = ad + js[ii][ij]
                for ik, ijj in enumerate(ad):
                    arr.append(f'**.{ii}.eth.mac.multiCastGroupAddr{ik} = {ijj}')

            for gk, go in enumerate(data[ii]['goose']):
                arr.append(f'**.{ii}.goMod[{gk + 1}].destAddress = "01 0C CD 01 {go_n1} {go_n2}"')

                arr.append(f'**.{ii}.goMod[{gk + 1}].startTime = 10000s')
                arr.append(f'**.{ii}.goMod[{gk + 1}].minsendInterval = {int(go["MinTime"]) / 1000}s')
                arr.append(f'**.{ii}.goMod[{gk + 1}].maxsendInterval = {(int(go["MaxTime"]) / 1000)}s')
                arr.append(f'**.{ii}.goMod[{gk + 1}].APPID = {go["APPID"]}')
                arr.append(f'**.{ii}.goMod[{gk + 1}].cbRef = "{go["goosePdu"]["gocbRef"]}"')
                arr.append(f'**.{ii}.goMod[{gk + 1}].dataSetRef = "{go["goosePdu"]["datSet"]}"')
                arr.append(f'**.{ii}.goMod[{gk + 1}].goID = "{go["goosePdu"]["goID"]}"')
                arr.append(f'**.{ii}.goMod[{gk + 1}].confRev = {go["goosePdu"]["confRev"]}')
                arr.append(f'**.{ii}.goMod[{gk + 1}].numDataSet = {go["goosePdu"]["numDatSetEntries"]}')
                arr.append(f'**.{ii}.goMod[{gk + 1}].totalDataLength = {go["goosePdu"]["allData"]}')
            if go_n2 == 'FF':
                go_n1 = hex_addition(go_n1)
                go_n2 = '00'
            else:
                go_n2 = hex_addition(go_n2)
            arr.append('')

            if ii in ap:
                arr.append(f'**.{ii}.numTcpApps = {len(data[ii]["mms"]) + len(ap[ii])}')

            else:
                arr.append(f'**.{ii}.numTcpApps = {len(data[ii]["mms"])}')

            for mk, mo in enumerate(data[ii]['mms']):
                arr.append(f'**.{ii}.tcpApp[{mk}].typename = "TCPmms"')
                arr.append(f'**.{ii}.tcpApp[{mk}].connectAddress = "{mo["ClientLN"]}"')

                if mo['ClientLN'] not in moc:
                    moc[mo['ClientLN']] = 0

                arr.append(f'**.{ii}.tcpApp[{mk}].connectPort = {moc[mo["ClientLN"]]} ')
                moc[mo['ClientLN']] = moc[mo['ClientLN']] + 1

                arr.append(f'**.{ii}.tcpApp[{mk}].tOpen = 9999s')
                arr.append(f'**.{ii}.tcpApp[{mk}].tSend = 10000s')
                if 'intgPd' in mo:
                    arr.append(f'**.{ii}.tcpApp[{mk}].sendInterval = {int(mo["intgPd"]) / 1000}s')
                else:
                    arr.append(f'**.{ii}.tcpApp[{mk}].sendInterval = 3s')

                arr.append(f'**.{ii}.tcpApp[{mk}].sendBytes = {mo["sendBytes"]}B')
                arr.append(f'**.{ii}.tcpApp[{mk}].tClose = 999999s')

            if ii in ap:
                if ii not in app1:
                    app1[ii] = 0

                for mk, mo in enumerate(ap[ii]):
                    arr.append(f'**.{ii}.tcpApp[{mk + len(data[ii]["mms"])}].typename =  "TCPSinkApp"')
                    arr.append(f'**.{ii}.tcpApp[{mk + len(data[ii]["mms"])}].localPort =  {app1[ii]}')
                    app1[ii] = app1[ii] + 1

    # print('\n'.join(arr))
    with open(scd + '.ini', 'w') as f:
        f.write("""[General]
    network = grid
    sim-time-limit = 999999s
    **.arp.globalARP = true
    *.configurator.config = xml("<config> \\
                                    <interface hosts='PCCCtrl' names='eth' address='10.0.0.1'/> \\
                                    <interface hosts='MVPCCProt' names='eth' address='10.0.0.2'/> \\
                                    <interface hosts='ESS1Ctrl' names='eth' address='10.0.1.1'/> \\
                                    <interface hosts='MVCBESS1' names='eth' address='10.0.1.2'/> \\
                                    <interface hosts='ESS2Ctrl' names='eth' address='10.0.2.1'/> \\
                                    <interface hosts='MVCBESS2' names='eth' address='10.0.2.2'/> \\
                                    <interface hosts='eRTU{1-6}' address='10.0.3.x'/> \\
                                    <interface hosts='ESS1Ctrl' towards='RTU' address='10.0.1.x'/> \\
                                    <interface hosts='RTU' towards='ESS1Ctrl' address='10.0.1.x'/> \\
                                 </config>")
    **.PCCCtrl.eth.mac.address = "B8 89 B9 20 02 01"
    **.MVPCCProt.eth.mac.address = "B8 89 B9 20 02 02"
    **.ESS1Ctrl.eth.mac.address = "B8 89 B9 20 02 03"
    **.MVCBESS1.eth.mac.address = "B8 89 B9 20 02 04"
    **.ESS2Ctrl.eth.mac.address = "B8 89 B9 20 02 05"
    **.MVCBESS2.eth.mac.address = "B8 89 B9 20 02 06"
    **.eRTU1.eth.mac.address = "B8 89 B9 20 02 11"
    **.eRTU2.eth.mac.address = "B8 89 B9 20 02 12"
    **.eRTU3.eth.mac.address = "B8 89 B9 20 02 13"
    **.eRTU4.eth.mac.address = "B8 89 B9 20 02 14"
    **.eRTU5.eth.mac.address = "B8 89 B9 20 02 15"
    **.eRTU6.eth.mac.address = "B8 89 B9 20 02 16"
    #Switch mac address table
    **.Switch1.macTable.addressTableFile = "G:\\\\iec\\\\workspace\\\\zzz\\\\simulations\\\\gridswitch1.txt"
    **.Switch2.macTable.addressTableFile = "G:\\\\iec\\\\workspace\\\\zzz\\\\simulations\\\\gridswitch2.txt"
    **.Switch3.macTable.addressTableFile = "G:\\\\iec\\\\workspace\\\\zzz\\\\simulations\\\\gridswitch3.txt"
    **.Switch4.macTable.addressTableFile = "G:\\\\iec\\\\workspace\\\\zzz\\\\simulations\\\\gridswitch4.txt"
    
    #STP protocol
    **.Switch*.spanningTreeProtocol = "STP"
    **.Switch*.l2NodeConfigurator.l2ConfiguratorModule = ""
    **.Switch*.stp.helloTime = 2s
    **.Switch1.stp.forwardDelay = 10s
    **.Switch2.stp.forwardDelay = 10s
    **.Switch3.stp.forwardDelay = 10s
    **.Switch4.stp.forwardDelay = 8s
    **.Switch1.stp.maxAge = 20s
    **.Switch2.stp.maxAge = 20s
    **.Switch3.stp.maxAge = 20s
    **.Switch4.stp.maxAge = 18s
    **.Switch1.stp.bridgePriority = 8192
    **.Switch2.stp.bridgePriority = 12288
    **.Switch3.stp.bridgePriority = 16384
    **.Switch4.stp.bridgePriority = 4096
    
    **.**.eth.mac.txQueueLimit = 1000000
    **.Switch*.eth[*].mac.txQueueLimit = 1000000
    **.Switch*.eth[*].queue.queue*.frameCapacity = 1000000
    
    #MMS Maximum Segment Size
    **.tcpType = "TCP"
    **.**.tcp.mss = 1021
    **.**.tcpApp[*].dataTransferMode = "object"
    """ + "\n".join(arr))


# ini_scd('Reference_Scenario')