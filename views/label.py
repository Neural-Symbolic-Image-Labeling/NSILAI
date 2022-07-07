import re
def get_total_list1(dict_list):
    total_object=[]
    total_list=[]
    for image_num in range(len(dict_list)):
        for objects_num in range(len(dict_list[image_num]['object'])):
            name=dict_list[image_num]['object'][str(objects_num)]['name']
            if name not in total_object:
                total_object.append(name)
    for image_num in range(len(dict_list)):
        image_list=[]
        position_list=[]
        for objects_num in range(len(dict_list[image_num]['object'])):
            name=dict_list[image_num]['object'][str(objects_num)]['name']
            position=total_object.index(name)
            if position not in position_list:
                position_list.append(position)
        object_numbers=[0 for i in range(len(position_list))]
        for objects_num in range(len(dict_list[image_num]['object'])):
            name=dict_list[image_num]['object'][str(objects_num)]['name']
            position=total_object.index(name)
            object_numbers[position_list.index(position)]+=1
        for index,objects in enumerate(position_list):
            has=total_object[objects]+"(image"+str(dict_list[image_num]['imageId'])+","+str(objects)+")"
            num="num"+"("+str(objects)+","+str(object_numbers[index])+")"
            image_list.append(has)
            image_list.append(num)
        for objects_num in range(len(dict_list[image_num]['overlap'])):
            object1_name=dict_list[image_num]['object'][str(dict_list[image_num]['overlap'][str(objects_num)]["idA"])]['name']
            object2_name=dict_list[image_num]['object'][str(dict_list[image_num]['overlap'][str(objects_num)]["idB"])]['name']
            position1=total_object.index(object1_name)
            position2=total_object.index(object2_name)
            if position1<position2:
                overlap="overlap("+str(position1)+","+str(position2)+")"
            else:
                overlap="overlap("+str(position2)+","+str(position1)+")"
            if overlap not in image_list:
                image_list.append(overlap)
        total_list.append(image_list)
    return total_list

def get_total_list(total_list1):
    total_list=[]
    for image in total_list1:
        list=[]
        for clauses in image:
            a=re.split(r'[(|,|)]',clauses)
            if a[0]!='overlap' and a[0]!='num':
                sub=a[1]
                break
        for clauses in image:
            a=re.split(r'[(|,|)]',clauses)
            if a[1]==sub:
                a[1]="X"
                if len(a)==3:
                    result=a[0]+"("+a[1]+")"+a[2]
                else:
                    result=a[0]+"("+a[1]+","+a[2]+")"+a[3]
                list.append(result)
            else:
                result=a[0]+"("+a[1]+","+a[2]+")"+a[3]
                list.append(result)
        total_list.append(list)
    return total_list

def labeling(total_list,rules):
    labels=[]
    possible_labels=[]
    for possible_label in rules.keys():
        possible_labels.append(possible_label)
    for image in total_list:
        find=False
        for possible_label in possible_labels:
            rule_list=rules[possible_label]
            satisfy=["False" for i in range(len(rule_list))]
            for rule_num,rule in enumerate(rule_list):
                satisfy_list=["False" for i in range(len(rule))]
                object_in_rule=[]
                object_character=[]
                for position,clauses in enumerate(rule):
                    a=re.split(r'[(|,|)]',clauses)
                    if a[0]!='overlap' and a[0]!='num' and len(a)==4:
                        object_in_rule.append(a[0])
                        object_character.append(a[2])
                        for predicate in image:
                            b=re.split(r'[(|,|)]',predicate)
                            if b[0]==a[0]:
                                satisfy_list[position]="True"
                                break
                    elif a[0]=='overlap':
                        object_in_image=[]
                        object_number=[]
                        object1_in_rule=object_in_rule[object_character.index(a[1])]
                        object2_in_rule=object_in_rule[object_character.index(a[2])]
                        for predicate in image:
                            b=re.split(r'[(|,|)]',predicate)
                            if b[0]!='overlap' and b[0]!='num':
                                object_in_image.append(b[0])
                                object_number.append(b[2])
                            if b[0]==a[0]:
                                object1_in_image=object_in_image[object_number.index(b[1])]
                                object2_in_image=object_in_image[object_number.index(b[2])]
                                if object1_in_image==object1_in_rule and object2_in_image==object2_in_rule:
                                    satisfy_list[position]="True"
                                    break
                    elif a[0]=='num':
                        object_in_image=[]
                        object_number=[]
                        object1_in_rule=object_in_rule[object_character.index(a[1])]
                        for predicate in image:
                            b=re.split(r'[(|,|)]',predicate)
                            if b[0]!='overlap' and b[0]!='num':
                                object_in_image.append(b[0])
                                object_number.append(b[2])
                            if b[0]==a[0]:
                                object1_in_image=object_in_image[object_number.index(b[1])]
                                c=re.split(r'[<]',rule[position+1])
                                mini=int(c[0])
                                maxi=int(c[2])
                                if object1_in_image==object1_in_rule and mini<=int(b[2])<=maxi:
                                    satisfy_list[position]="True"
                                    break
                    else:
                        satisfy_list[position]="True"
                        break
                if "False" not in satisfy_list:
                    satisfy[rule_num]="True"
            if "True" in satisfy:
                labels.append(possible_label)
                find=True
                break
        if find==False:
            labels.append("None")
    return labels

def label(dict_list,rules):
    total_list1=get_total_list1(dict_list)
    total_list=get_total_list(total_list1)
    labels=labeling(total_list,rules)
    return labels

def main():
    dict_list=[{'imageId': 1, 'object': {'0': {'coordinate': [270.6976013183594, 0.5646281242370605, 434.23565673828125, 204.41815185546875], 'name': 'bicycle', 'prob': 0.8869708180427551}, '1': {'coordinate': [0.04711151123046875, 11.185171127319336, 226.09010314941406, 421.4281311035156], 'name': 'motorcycle', 'prob': 0.9987192153930664}, '2': {'coordinate': [231.62582397460938, 181.38723754882812, 639.4808959960938, 408.91851806640625], 'name': 'bicycle', 'prob': 0.8329761028289795}, '3': {'coordinate': [268.9730224609375, 8.304173469543457, 374.838623046875, 202.58261108398438], 'name': 'bicycle', 'prob': 0.7619864344596863}, '4': {'coordinate': [234.83212280273438, 293.1654357910156, 572.2698364257812, 415.2937927246094], 'name': 'bicycle', 'prob': 0.7877762913703918}, '5': {'coordinate': [235.27586364746094, 293.49542236328125, 512.690185546875, 408.3638916015625], 'name': 'bicycle', 'prob': 0.8721397519111633}, '6': {'coordinate': [309.86968994140625, 53.21726608276367, 618.6395263671875, 416.29742431640625], 'name': 'person', 'prob': 0.9995409250259399}}, 'overlap': {'0': {'idA': 0, 'idB': 2, 'area': 3766.430940250866}, '1': {'idA': 0, 'idB': 3, 'area': 20232.35499298756}, '2': {'idA': 0, 'idB': 6, 'area': 18804.24433966633}, '3': {'idA': 2, 'idB': 3, 'area': 2243.8609489426017}, '4': {'idA': 2, 'idB': 4, 'area': 39059.455427828245}, '5': {'idA': 2, 'idB': 5, 'area': 31866.158501361497}, '6': {'idA': 2, 'idB': 6, 'area': 70254.79626716115}, '7': {'idA': 3, 'idB': 6, 'area': 9704.107107659569}, '8': {'idA': 4, 'idB': 5, 'area': 31866.158501361497}, '9': {'idA': 4, 'idB': 6, 'area': 32046.498749271035}, '10': {'idA': 5, 'idB': 6, 'area': 23297.679860349745}}}, {'imageId': 2, 'object': {'0': {'coordinate': [186.47589111328125, 355.7585144042969, 220.93783569335938, 387.45086669921875], 'name': 'knife', 'prob': 0.863101601600647}, '1': {'coordinate': [117.00293731689453, 367.69219970703125, 190.04823303222656, 384.8884582519531], 'name': 'knife', 'prob': 0.9621061086654663}, '2': {'coordinate': [412.4399108886719, 492.0442199707031, 479.8027648925781, 608.02783203125], 'name': 'cup', 'prob': 0.9973136782646179}, '3': {'coordinate': [306.18792724609375, 312.7323303222656, 342.4439697265625, 356.02056884765625], 'name': 'cup', 'prob': 0.9567000269889832}, '4': {'coordinate': [-0.0018775463104248047, 416.8985595703125, 28.19085693359375, 505.46759033203125], 'name': 'bottle', 'prob': 0.788969099521637}, '5': {'coordinate': [420.2816162109375, 432.09844970703125, 479.8142395019531, 497.679443359375], 'name': 'cup', 'prob': 0.9966208934783936}, '6': {'coordinate': [354.57379150390625, 91.14698791503906, 477.8052062988281, 234.94302368164062], 'name': 'couch', 'prob': 0.9910711050033569}, '7': {'coordinate': [129.47836303710938, 355.35284423828125, 216.29458618164062, 420.32476806640625], 'name': 'bowl', 'prob': 0.9852918386459351}, '8': {'coordinate': [0.07976174354553223, 346.12158203125, 80.26863098144531, 428.945068359375], 'name': 'chair', 'prob': 0.9545845985412598}, '9': {'coordinate': [116.68373107910156, 361.88018798828125, 205.41314697265625, 385.85235595703125], 'name': 'knife', 'prob': 0.9220200777053833}, '10': {'coordinate': [116.4785385131836, 268.9111022949219, 195.97169494628906, 367.27838134765625], 'name': 'chair', 'prob': 0.9186678528785706}, '11': {'coordinate': [114.61260223388672, 240.8279266357422, 196.16488647460938, 368.9065856933594], 'name': 'chair', 'prob': 0.7910692095756531}, '12': {'coordinate': [0.3719902038574219, 14.250106811523438, 237.0241241455078, 436.22705078125], 'name': 'person', 'prob': 0.9984582662582397}, '13': {'coordinate': [0.11188030242919922, 285.721923828125, 479.9058837890625, 632.1168212890625], 'name': 'dining table', 'prob': 0.983228862285614}, '14': {'coordinate': [0.18196821212768555, 314.98919677734375, 122.68177795410156, 422.5535583496094], 'name': 'chair', 'prob': 0.8850402235984802}, '15': {'coordinate': [168.722900390625, 329.65447998046875, 183.58297729492188, 345.59027099609375], 'name': 'clock', 'prob': 0.7549286484718323}}, 'overlap': {'0': {'idA': 0, 'idB': 1, 'area': 61.43091524904594}, '1': {'idA': 0, 'idB': 7, 'area': 945.0245890812948}, '2': {'idA': 0, 'idB': 9, 'area': 453.96707832813263}, '3': {'idA': 0, 'idB': 10, 'area': 109.39039667649195}, '4': {'idA': 0, 'idB': 11, 'area': 127.39160173013806}, '5': {'idA': 0, 'idB': 12, 'area': 1092.1800883999094}, '6': {'idA': 0, 'idB': 13, 'area': 1092.1800883999094}, '7': {'idA': 1, 'idB': 7, 'area': 1041.575144468341}, '8': {'idA': 1, 'idB': 9, 'area': 1256.1057906111237}, '9': {'idA': 1, 'idB': 11, 'area': 88.70518348389305}, '10': {'idA': 1, 'idB': 12, 'area': 1256.1057906111237}, '11': {'idA': 1, 'idB': 13, 'area': 1256.1057906111237}, '12': {'idA': 1, 'idB': 14, 'area': 97.654811832821}, '13': {'idA': 2, 'idB': 5, 'area': 335.4149691713974}, '14': {'idA': 2, 'idB': 13, 'area': 7812.987126080319}, '15': {'idA': 3, 'idB': 13, 'area': 1569.4602148812264}, '16': {'idA': 4, 'idB': 8, 'area': 338.6405552770884}, '17': {'idA': 4, 'idB': 12, 'area': 537.6967210839503}, '18': {'idA': 4, 'idB': 13, 'area': 2486.927745003195}, '19': {'idA': 4, 'idB': 14, 'area': 158.3902315293526}, '20': {'idA': 5, 'idB': 13, 'area': 3904.2085901554674}, '21': {'idA': 7, 'idB': 9, 'area': 1820.3213951736689}, '22': {'idA': 7, 'idB': 10, 'area': 792.9686972089112}, '23': {'idA': 7, 'idB': 11, 'area': 903.8518972098827}, '24': {'idA': 7, 'idB': 12, 'area': 5640.617037191987}, '25': {'idA': 7, 'idB': 13, 'area': 5640.617037191987}, '26': {'idA': 8, 'idB': 12, 'area': 6617.318335105665}, '27': {'idA': 8, 'idB': 13, 'area': 6638.861543970415}, '28': {'idA': 8, 'idB': 14, 'area': 6121.181912200918}, '29': {'idA': 9, 'idB': 10, 'area': 428.0117600262165}, '30': {'idA': 9, 'idB': 11, 'area': 558.4662078679539}, '31': {'idA': 9, 'idB': 12, 'area': 2127.036461569369}, '32': {'idA': 9, 'idB': 13, 'area': 2127.036461569369}, '33': {'idA': 9, 'idB': 14, 'area': 143.78618717193604}, '34': {'idA': 10, 'idB': 11, 'area': 7819.525501637952}, '35': {'idA': 10, 'idB': 12, 'area': 7819.525501637952}, '36': {'idA': 10, 'idB': 13, 'area': 6483.1802357300185}, '37': {'idA': 10, 'idB': 14, 'area': 324.3623320600018}, '38': {'idA': 10, 'idB': 15, 'area': 236.8070800229907}, '39': {'idA': 11, 'idB': 12, 'area': 10445.107208637404}, '40': {'idA': 11, 'idB': 13, 'area': 6783.899188901996}, '41': {'idA': 11, 'idB': 14, 'area': 435.0688855384942}, '42': {'idA': 11, 'idB': 15, 'area': 236.8070800229907}, '43': {'idA': 12, 'idB': 13, 'area': 35617.359462616034}, '44': {'idA': 12, 'idB': 14, 'area': 13156.174233394326}, '45': {'idA': 12, 'idB': 15, 'area': 236.8070800229907}, '46': {'idA': 13, 'idB': 14, 'area': 13176.613827619425}, '47': {'idA': 13, 'idB': 15, 'area': 236.8070800229907}}}, {'imageId': 3, 'object': {'0': {'coordinate': [215.01585388183594, 441.1595458984375, 241.892333984375, 475.4443054199219], 'name': 'handbag', 'prob': 0.9809021949768066}, '1': {'coordinate': [167.105224609375, 481.199951171875, 179.00698852539062, 501.796630859375], 'name': 'handbag', 'prob': 0.7817053198814392}, '2': {'coordinate': [431.74945068359375, 462.5838623046875, 456.75909423828125, 528.0986328125], 'name': 'person', 'prob': 0.9965948462486267}, '3': {'coordinate': [411.4190368652344, 464.17401123046875, 431.469970703125, 523.3245239257812], 'name': 'person', 'prob': 0.9947890043258667}, '4': {'coordinate': [166.89613342285156, 456.74334716796875, 182.29916381835938, 508.70037841796875], 'name': 'person', 'prob': 0.992109477519989}, '5': {'coordinate': [0.002886056900024414, 472.95654296875, 25.15494728088379, 517.0625], 'name': 'car', 'prob': 0.9786995649337769}, '6': {'coordinate': [439.5792236328125, 478.81890869140625, 456.5301818847656, 503.6502685546875], 'name': 'handbag', 'prob': 0.9468593001365662}, '7': {'coordinate': [259.6690979003906, 210.1631317138672, 283.0189514160156, 257.0885009765625], 'name': 'traffic light', 'prob': 0.9970718622207642}, '8': {'coordinate': [181.03933715820312, 476.5258483886719, 222.37088012695312, 513.4207763671875], 'name': 'suitcase', 'prob': 0.8943426609039307}, '9': {'coordinate': [24.74919319152832, 451.5570068359375, 44.14604187011719, 500.6855773925781], 'name': 'person', 'prob': 0.9752901196479797}, '10': {'coordinate': [268.09417724609375, 478.8925476074219, 290.8290100097656, 516.4414672851562], 'name': 'bench', 'prob': 0.7876744270324707}, '11': {'coordinate': [323.8840026855469, 382.66607666015625, 338.22784423828125, 409.57525634765625], 'name': 'traffic light', 'prob': 0.9629154205322266}, '12': {'coordinate': [465.9528503417969, 469.9328918457031, 479.683837890625, 515.5655517578125], 'name': 'person', 'prob': 0.9485933184623718}, '13': {'coordinate': [211.14134216308594, 393.16192626953125, 276.5450744628906, 574.33984375], 'name': 'person', 'prob': 0.9997686743736267}, '14': {'coordinate': [347.603515625, 469.4003601074219, 361.7298583984375, 501.9714050292969], 'name': 'person', 'prob': 0.9155468940734863}, '15': {'coordinate': [44.581275939941406, 452.2747497558594, 62.73636245727539, 500.3128356933594], 'name': 'person', 'prob': 0.9905517101287842}, '16': {'coordinate': [187.55050659179688, 458.75799560546875, 201.63046264648438, 472.6986083984375], 'name': 'person', 'prob': 0.9451029300689697}}, 'overlap': {'0': {'idA': 0, 'idB': 13, 'area': 921.4536570995115}, '1': {'idA': 1, 'idB': 4, 'area': 245.13681909441948}, '2': {'idA': 2, 'idB': 6, 'area': 420.9153443817049}, '3': {'idA': 4, 'idB': 8, 'area': 40.534330708906054}, '4': {'idA': 5, 'idB': 9, 'area': 11.251169111346826}, '5': {'idA': 8, 'idB': 13, 'area': 414.3129944088869}, '6': {'idA': 10, 'idB': 13, 'area': 317.32206079829484}}}]
    rules={'non-life(X)': [['bicycle(X,A)']], 'life(X)': [['knife(X,A)'], ['handbag(X,B)']]}
    print(label(dict_list,rules))

main()