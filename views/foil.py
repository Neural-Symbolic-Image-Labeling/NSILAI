import math,re,copy,json,time

#This function is to calculate the information gain to make sure the best literal can be added into the final output
def foil_gain(pre_p,pre_n,now_p,now_n):
    if (pre_p==0 or now_p==0):
        return -99                        #There are some cases that the numerator may be 0. Set to -99 for not affecting the normal comparision among the multiple gains
    gain=now_p*(math.log2(now_p/(now_n+now_p))-math.log2(pre_p/(pre_p+pre_n)))        #now_p:new positive, pre_n: previous negative
    return gain
    
#This function is to get parameter(s), for example:only when you have "person" or "guitar", you can have overlap(person,guitar)
def get_parameter_list(result):
    parameter_list=[]
    for clause in result:
        a=re.split(r'[(|,|)]',clause)
        if a[0]!="overlap" and a[0]!="num":
            parameter_list.append(a[2])
    return parameter_list

'''This function is to get positive and negative list according to the target(such as "guitarist") and see if the image classified as "guitarist" has the clause,
if yes, it is positive, otherwise negative'''
def pos_neg_list(target,total_list):
    positive_list=[]
    negative_list=[]
    for image_number,image in enumerate(total_list):
        for i,clause in enumerate(image):
            if i==0:
                if clause==target:
                    positive_list.append(image_number)
                else:
                    negative_list.append(image_number)
    return positive_list,negative_list

"""This function is to get new possible list, such as we have a clause :has("person"), then next time we delete all the definition which does not has this clause.
return is a three dimentional list, for the second dimension, it is one-to-one correspond to the result_list (ie, [[has("person")],[has("guitar")]], then the inner
dimension has the correspond images which has the clause in the result_list"""
def get_new_total_list(result_list,total_list):
    del_number_hd=[]
    new_total=copy.deepcopy(total_list)
    for i in range(len(result_list)):
        if i!=len(result_list)-1:
            for image_number,image in enumerate(total_list):
                del_result=True
                for clause in result_list[i]:
                    if (clause not in image):        #remember the position of image that does not has special clause
                        del_result=False
                        break
                if del_result==True:
                    del_number_hd.append(image_number)
        else:
            for image_number,image in enumerate(total_list):
                for clause in result_list[i]:
                    if (clause not in image):
                        del_number_hd.append(image_number)
                        break
    del_number=list(set(del_number_hd))         #del_number has no duplicate
    del_number.sort()
    for i in range(len(del_number)):
        del new_total[del_number[len(del_number)-1-i]]               #the position is in positive sequence, first delete the back one
    return new_total   #two dimentional list, get the result which not has the positive that satisfy right side
    
def get_new_total_list1(result_list,total_list):        #use for outer loop
    del_number_hd=[]
    new_total=copy.deepcopy(total_list)           #use deepcopy for not changing the total_list
    for clauses_list in result_list:
        for image_number,image in enumerate(total_list):
            del_result=True
            for clause in clauses_list:
                if (clause not in image):        #remember the position of image that does not has special clause
                    del_result=False
                    break
            if del_result==True:
                del_number_hd.append(image_number)
    del_number=list(set(del_number_hd))         #del_number has no duplicate
    del_number.sort()
    for i in range(len(del_number)):
        del new_total[del_number[len(del_number)-1-i]]               #the position is in positive sequence, first delete the back one
    return new_total   #two dimentional list, get the result which not has the positive that satisfy right side

def get_possible_clause1(counting,total_list,result_list):
    if counting==0:
        new_total=get_new_total_list1(result_list,total_list)
        clause_total=[]
        for image in new_total:
            for i,clause in enumerate(image):
                if i!=0 and (clause not in clause_total):        # The first position of each image is classification, so clauses start from the second position
                    clause_total.append(clause)
    else:
        new_total=get_new_total_list(result_list,total_list)
        clause_total=[]
        for image in new_total:
            for i,clause in enumerate(image):
                if i!=0 and (clause not in result_list[len(result_list)-1]) and (clause not in clause_total):        # The first position of each image is classification, so clauses start from the second position
                    clause_total.append(clause)
    return clause_total
    
def rank_the_result(result_list):
    result=sorted(result_list,key=lambda i:len(i))
    return result

def get_total_list(total_list1):
    total_list=[]
    for image in total_list1:
        list=[]
        sub=re.split(r'[(|,|)]',image[0])[1]     #"campus(image1)",get "image1"
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

def get_int(elem):
    return int(elem)
    
def get_result_list(result_list):
    new_result_list=[]
    number=[]
    character=[]
    for image in result_list:
        for clauses in image:
            a=re.split(r'[(|,|)]',clauses)
            if a[0]!="overlap" and a[0]!="num":
                if a[2] not in number:
                    number.append(a[2])
            elif a[0]=="overlap":
                if a[2] not in number:
                    number.append(a[2])
                if a[1] not in number:
                    number.append(a[1])
            else:
                if a[1] not in number:
                    number.append(a[1])
    number.sort(key=get_int)
    for i in range(len(number)):
        if i<23:
            character.append(chr(i+65))
        else:
            character.append(chr(i+65+1))
    for image in result_list:
        result=[]
        for clauses in image:
            a=re.split(r'[(|,|)]',clauses)
            if a[0]!="overlap" and a[0]!='num':
                position=number.index(a[2])
                a[2]=character[position]
                clause=a[0]+"("+a[1]+","+a[2]+")"+a[3]
                result.append(clause)
            elif a[0]=="overlap":
                position1=number.index(a[1])
                position2=number.index(a[2])
                a[1]=character[position1]
                a[2]=character[position2]
                clause=a[0]+"("+a[1]+","+a[2]+")"+a[3]
                result.append(clause)
            else:
                position=number.index(a[1])
                a[1]=character[position]
                clause=a[0]+"("+a[1]+","+a[2]+")"+a[3]
                result.append(clause)
        new_result_list.append(result)
    return new_result_list
    
def get_total_list1(input_list):
    total_object=[]
    total_list=[]
    image_number=1
    for image_num in range(len(input_list)):
        for objects_num in range(len(input_list[image_num]['object'])):
            name=input_list[image_num]['object'][str(objects_num)]['name']
            if name not in total_object:
                total_object.append(name)
    for image_num in range(len(input_list)):
        image_list=[]
        string=input_list[image_num]['type']+"(image"+str(image_number)+")"
        image_list.append(string)
        position_list=[]
        for objects_num in range(len(input_list[image_num]['object'])):
            name=input_list[image_num]['object'][str(objects_num)]['name']
            position=total_object.index(name)
            if position not in position_list:
                position_list.append(position)
        object_numbers=[0 for i in range(len(position_list))]
        for objects_num in range(len(input_list[image_num]['object'])):
            name=input_list[image_num]['object'][str(objects_num)]['name']
            position=total_object.index(name)
            object_numbers[position_list.index(position)]+=1
        for index,objects in enumerate(position_list):
            has=total_object[objects]+"(image"+str(image_number)+","+str(objects)+")"
            num="num"+"("+str(objects)+","+str(object_numbers[index])+")"
            image_list.append(has)
            image_list.append(num)
        for objects_num in range(len(input_list[image_num]['overlap'])):
            object1_name=input_list[image_num]['object'][str(input_list[image_num]['overlap'][str(objects_num)]["idA"])]['name']
            object2_name=input_list[image_num]['object'][str(input_list[image_num]['overlap'][str(objects_num)]["idB"])]['name']
            position1=total_object.index(object1_name)
            position2=total_object.index(object2_name)
            if position1<position2:
                overlap="overlap("+str(position1)+","+str(position2)+")"
            else:
                overlap="overlap("+str(position2)+","+str(position1)+")"
            if overlap not in image_list:
                image_list.append(overlap)
        total_list.append(image_list)
        image_number+=1
    return total_list

def threshold(target,clause,total_list):
    positive_list=[]
    negative_list=[]
    for image in total_list:
        for clauses in image:
            a=re.split(r'[(|,|)]',clauses)
            a1=re.split(r'[(|,|)]',clause)
            if a[0]=='num' and a[1]==a1[1]:
                if image[0]==target:
                    positive_list.append(int(a[2]))
                else:
                    negative_list.append(int(a[2]))
    result=True
    for negative_num in negative_list:
        if negative_num<max(positive_list) and negative_num>min(positive_list):
            result=False
            break
    if result==False:
        return False
    else:
        return min(positive_list),max(positive_list)
                
def foil(target,total_list):
#target should be a string, such as "guitarist"
    result_list=[]     #two dimentional list
    new_total_list=copy.deepcopy(total_list)
    positive_list,negative_list=pos_neg_list(target,new_total_list)   #get the initial_positive_list,to help find out the result that can satisfy all the positives
    i=0   #make sure that all the result in the result list has been proved that fulfill our requirements(can satisfy all the positives and reject all the negatives)
    while (len(positive_list)!=0):
        counting=0
        while (len(negative_list)!=0):
            if len(result_list)==i:                #the result_list is empty at initial state
                result=[]
            else:
                result=result_list[i]
            pre_p=len(positive_list)
            pre_n=len(negative_list)
            foil_gain_list=[]
            possible_clause=get_possible_clause1(counting,total_list,result_list)
            for new_clause in possible_clause:           #calculate the new possible clause foil_gain
                now_p=now_n=0
                for image_number,image in enumerate(new_total_list):
                    for clause in image:
                        if clause==new_clause:
                            for positive_image_number in positive_list:
                                if image_number==positive_image_number:
                                    now_p+=1  
                            for negative_image_number in negative_list:
                                if image_number==negative_image_number:
                                    now_n+=1
                foil_gain_list.append(foil_gain(pre_p,pre_n,now_p,now_n))
            correct_clause=False              #first set false, if the correct one is found, jump out of the iteration
            parameter_list=get_parameter_list(result)
            while correct_clause == False:
                for clause_number,clause_gain in enumerate(foil_gain_list):
                    if clause_gain==max(foil_gain_list):
                        a=re.split(r'[(|,|)]',possible_clause[clause_number])
                        if a[0]=="overlap":
                            if (a[1] in parameter_list) and (a[2] in parameter_list):
                                new_result=copy.deepcopy(result)    #The following is to first add it to result, if it is a special case 
                                new_result.append(possible_clause[clause_number])       # such that only one positive has the clause and no negative has it, it may has the best gain.
                                result_list.append(new_result)
                                correct_clause=True
                                break
                            else:
                                foil_gain_list[clause_number]=-99
                                break
                        elif a[0]=="num":
                            if a[1] in parameter_list and threshold(target,possible_clause[clause_number],total_list)!=False:
                                new_result=copy.deepcopy(result)
                                new_result.append(possible_clause[clause_number])
                                result_list.append(new_result)
                                correct_clause=True
                                break
                            else:
                                foil_gain_list[clause_number]=-99
                                break 
                        else:
                            new_result=copy.deepcopy(result)
                            new_result.append(possible_clause[clause_number])
                            result_list.append(new_result)
                            correct_clause=True
                            break
            if counting!=0:          #Each time, because we add the updated version at the end of the list, so delete the old version
                del result_list[i]
            new_total_list=get_new_total_list(result_list,total_list)
            positive_list,negative_list=pos_neg_list(target,new_total_list)   # can use for next iteration when the answer is not perfect
            counting+=1           #just for the special case that at first the list is empty and we cannot delete the new added one. (Or we can say that we cannot delete the old empty version)
        new_total_list=get_new_total_list1(result_list,total_list)
        positive_list,negative_list=pos_neg_list(target,new_total_list)
        i+=1
    return result_list

def plural(word):
    if word=="person":
        return "people"
    elif word.endswith('y'):
        return word[:-1]+"ies"
    elif word[-1] in 'sx' or word[-2:] in ['sh','ch']:
        return word+'es'
    elif word.endswith('an'):
        return word[:-2]+'en'
    else:
        return word+'s'
    
def NL(result_list,target,total_list):
    result=[]
    for results in result_list:
        result_list=[]
        objects=[]
        characters=[]
        for i,clauses in enumerate(results):
            n=''
            a=re.split(r'[(|,|)]',clauses)
            if a[0]!='overlap' and a[0]!="num":
                n+='This image has '+a[0]
                objects.append(a[0])
                characters.append(a[2])
            elif a[0]=="overlap":
                index1=characters.index(a[1])
                index2=characters.index(a[2])
                n+=objects[index1]+' is overlapping with '+objects[index2]
            else:
                index=characters.index(a[1])
                object_name=objects[index]
                if int(a[2])>1:
                    object_name= plural(object_name)
                max,min=threshold(target,clauses,total_list)
                n+='The number of '+object_name+" is greater than "+min+", less than "+max
            result_list.append(n)
        result.append(result_list)
    return result

def FOIL(input_list):
    #start=time.time()
    dict_math={}
    dict_nl={}
    total_list1=get_total_list1(input_list)
    total_list=get_total_list(total_list1)
    target_list=[]
    for images in total_list:
        if images[0] not in target_list:
            target_list.append(images[0])
    #target_list.remove("residential(X)")
    for target in target_list:
        result_list=foil(target,total_list)
        math_format=get_result_list(result_list)
        natural_language=NL(math_format,target,result_list)
        dict_math[target]=math_format
        dict_nl[target]=natural_language
    #end=time.time()
    #print(end-start)
    return dict_math,dict_nl

def main():
    input_list= [{'imageId': 1, 'type': 'non-life', 'object': {'0': {'coordinate': [270.6976013183594, 0.5646281242370605, 434.23565673828125, 204.41815185546875], 'name': 'bicycle', 'prob': 0.8869708180427551}, '1': {'coordinate': [0.04711151123046875, 11.185171127319336, 226.09010314941406, 421.4281311035156], 'name': 'motorcycle', 'prob': 0.9987192153930664}, '2': {'coordinate': [231.62582397460938, 181.38723754882812, 639.4808959960938, 408.91851806640625], 'name': 'bicycle', 'prob': 0.8329761028289795}, '3': {'coordinate': [268.9730224609375, 8.304173469543457, 374.838623046875, 202.58261108398438], 'name': 'bicycle', 'prob': 0.7619864344596863}, '4': {'coordinate': [234.83212280273438, 293.1654357910156, 572.2698364257812, 415.2937927246094], 'name': 'bicycle', 'prob': 0.7877762913703918}, '5': {'coordinate': [235.27586364746094, 293.49542236328125, 512.690185546875, 408.3638916015625], 'name': 'bicycle', 'prob': 0.8721397519111633}, '6': {'coordinate': [309.86968994140625, 53.21726608276367, 618.6395263671875, 416.29742431640625], 'name': 'person', 'prob': 0.9995409250259399}}, 'overlap': {'0': {'idA': 0, 'idB': 2, 'area': 3766.430940250866}, '1': {'idA': 0, 'idB': 3, 'area': 20232.35499298756}, '2': {'idA': 0, 'idB': 6, 'area': 18804.24433966633}, '3': {'idA': 2, 'idB': 3, 'area': 2243.8609489426017}, '4': {'idA': 2, 'idB': 4, 'area': 39059.455427828245}, '5': {'idA': 2, 'idB': 5, 'area': 31866.158501361497}, '6': {'idA': 2, 'idB': 6, 'area': 70254.79626716115}, '7': {'idA': 3, 'idB': 6, 'area': 9704.107107659569}, '8': {'idA': 4, 'idB': 5, 'area': 31866.158501361497}, '9': {'idA': 4, 'idB': 6, 'area': 32046.498749271035}, '10': {'idA': 5, 'idB': 6, 'area': 23297.679860349745}}}, {'imageId': 2, 'type': 'life', 'object': {'0': {'coordinate': [186.47589111328125, 355.7585144042969, 220.93783569335938, 387.45086669921875], 'name': 'knife', 'prob': 0.863101601600647}, '1': {'coordinate': [117.00293731689453, 367.69219970703125, 190.04823303222656, 384.8884582519531], 'name': 'knife', 'prob': 0.9621061086654663}, '2': {'coordinate': [412.4399108886719, 492.0442199707031, 479.8027648925781, 608.02783203125], 'name': 'cup', 'prob': 0.9973136782646179}, '3': {'coordinate': [306.18792724609375, 312.7323303222656, 342.4439697265625, 356.02056884765625], 'name': 'cup', 'prob': 0.9567000269889832}, '4': {'coordinate': [-0.0018775463104248047, 416.8985595703125, 28.19085693359375, 505.46759033203125], 'name': 'bottle', 'prob': 0.788969099521637}, '5': {'coordinate': [420.2816162109375, 432.09844970703125, 479.8142395019531, 497.679443359375], 'name': 'cup', 'prob': 0.9966208934783936}, '6': {'coordinate': [354.57379150390625, 91.14698791503906, 477.8052062988281, 234.94302368164062], 'name': 'couch', 'prob': 0.9910711050033569}, '7': {'coordinate': [129.47836303710938, 355.35284423828125, 216.29458618164062, 420.32476806640625], 'name': 'bowl', 'prob': 0.9852918386459351}, '8': {'coordinate': [0.07976174354553223, 346.12158203125, 80.26863098144531, 428.945068359375], 'name': 'chair', 'prob': 0.9545845985412598}, '9': {'coordinate': [116.68373107910156, 361.88018798828125, 205.41314697265625, 385.85235595703125], 'name': 'knife', 'prob': 0.9220200777053833}, '10': {'coordinate': [116.4785385131836, 268.9111022949219, 195.97169494628906, 367.27838134765625], 'name': 'chair', 'prob': 0.9186678528785706}, '11': {'coordinate': [114.61260223388672, 240.8279266357422, 196.16488647460938, 368.9065856933594], 'name': 'chair', 'prob': 0.7910692095756531}, '12': {'coordinate': [0.3719902038574219, 14.250106811523438, 237.0241241455078, 436.22705078125], 'name': 'person', 'prob': 0.9984582662582397}, '13': {'coordinate': [0.11188030242919922, 285.721923828125, 479.9058837890625, 632.1168212890625], 'name': 'dining table', 'prob': 0.983228862285614}, '14': {'coordinate': [0.18196821212768555, 314.98919677734375, 122.68177795410156, 422.5535583496094], 'name': 'chair', 'prob': 0.8850402235984802}, '15': {'coordinate': [168.722900390625, 329.65447998046875, 183.58297729492188, 345.59027099609375], 'name': 'clock', 'prob': 0.7549286484718323}}, 'overlap': {'0': {'idA': 0, 'idB': 1, 'area': 61.43091524904594}, '1': {'idA': 0, 'idB': 7, 'area': 945.0245890812948}, '2': {'idA': 0, 'idB': 9, 'area': 453.96707832813263}, '3': {'idA': 0, 'idB': 10, 'area': 109.39039667649195}, '4': {'idA': 0, 'idB': 11, 'area': 127.39160173013806}, '5': {'idA': 0, 'idB': 12, 'area': 1092.1800883999094}, '6': {'idA': 0, 'idB': 13, 'area': 1092.1800883999094}, '7': {'idA': 1, 'idB': 7, 'area': 1041.575144468341}, '8': {'idA': 1, 'idB': 9, 'area': 1256.1057906111237}, '9': {'idA': 1, 'idB': 11, 'area': 88.70518348389305}, '10': {'idA': 1, 'idB': 12, 'area': 1256.1057906111237}, '11': {'idA': 1, 'idB': 13, 'area': 1256.1057906111237}, '12': {'idA': 1, 'idB': 14, 'area': 97.654811832821}, '13': {'idA': 2, 'idB': 5, 'area': 335.4149691713974}, '14': {'idA': 2, 'idB': 13, 'area': 7812.987126080319}, '15': {'idA': 3, 'idB': 13, 'area': 1569.4602148812264}, '16': {'idA': 4, 'idB': 8, 'area': 338.6405552770884}, '17': {'idA': 4, 'idB': 12, 'area': 537.6967210839503}, '18': {'idA': 4, 'idB': 13, 'area': 2486.927745003195}, '19': {'idA': 4, 'idB': 14, 'area': 158.3902315293526}, '20': {'idA': 5, 'idB': 13, 'area': 3904.2085901554674}, '21': {'idA': 7, 'idB': 9, 'area': 1820.3213951736689}, '22': {'idA': 7, 'idB': 10, 'area': 792.9686972089112}, '23': {'idA': 7, 'idB': 11, 'area': 903.8518972098827}, '24': {'idA': 7, 'idB': 12, 'area': 5640.617037191987}, '25': {'idA': 7, 'idB': 13, 'area': 5640.617037191987}, '26': {'idA': 8, 'idB': 12, 'area': 6617.318335105665}, '27': {'idA': 8, 'idB': 13, 'area': 6638.861543970415}, '28': {'idA': 8, 'idB': 14, 'area': 6121.181912200918}, '29': {'idA': 9, 'idB': 10, 'area': 428.0117600262165}, '30': {'idA': 9, 'idB': 11, 'area': 558.4662078679539}, '31': {'idA': 9, 'idB': 12, 'area': 2127.036461569369}, '32': {'idA': 9, 'idB': 13, 'area': 2127.036461569369}, '33': {'idA': 9, 'idB': 14, 'area': 143.78618717193604}, '34': {'idA': 10, 'idB': 11, 'area': 7819.525501637952}, '35': {'idA': 10, 'idB': 12, 'area': 7819.525501637952}, '36': {'idA': 10, 'idB': 13, 'area': 6483.1802357300185}, '37': {'idA': 10, 'idB': 14, 'area': 324.3623320600018}, '38': {'idA': 10, 'idB': 15, 'area': 236.8070800229907}, '39': {'idA': 11, 'idB': 12, 'area': 10445.107208637404}, '40': {'idA': 11, 'idB': 13, 'area': 6783.899188901996}, '41': {'idA': 11, 'idB': 14, 'area': 435.0688855384942}, '42': {'idA': 11, 'idB': 15, 'area': 236.8070800229907}, '43': {'idA': 12, 'idB': 13, 'area': 35617.359462616034}, '44': {'idA': 12, 'idB': 14, 'area': 13156.174233394326}, '45': {'idA': 12, 'idB': 15, 'area': 236.8070800229907}, '46': {'idA': 13, 'idB': 14, 'area': 13176.613827619425}, '47': {'idA': 13, 'idB': 15, 'area': 236.8070800229907}}}, {'imageId': 3, 'type': 'life', 'object': {'0': {'coordinate': [215.01585388183594, 441.1595458984375, 241.892333984375, 475.4443054199219], 'name': 'handbag', 'prob': 0.9809021949768066}, '1': {'coordinate': [167.105224609375, 481.199951171875, 179.00698852539062, 501.796630859375], 'name': 'handbag', 'prob': 0.7817053198814392}, '2': {'coordinate': [431.74945068359375, 462.5838623046875, 456.75909423828125, 528.0986328125], 'name': 'person', 'prob': 0.9965948462486267}, '3': {'coordinate': [411.4190368652344, 464.17401123046875, 431.469970703125, 523.3245239257812], 'name': 'person', 'prob': 0.9947890043258667}, '4': {'coordinate': [166.89613342285156, 456.74334716796875, 182.29916381835938, 508.70037841796875], 'name': 'person', 'prob': 0.992109477519989}, '5': {'coordinate': [0.002886056900024414, 472.95654296875, 25.15494728088379, 517.0625], 'name': 'car', 'prob': 0.9786995649337769}, '6': {'coordinate': [439.5792236328125, 478.81890869140625, 456.5301818847656, 503.6502685546875], 'name': 'handbag', 'prob': 0.9468593001365662}, '7': {'coordinate': [259.6690979003906, 210.1631317138672, 283.0189514160156, 257.0885009765625], 'name': 'traffic light', 'prob': 0.9970718622207642}, '8': {'coordinate': [181.03933715820312, 476.5258483886719, 222.37088012695312, 513.4207763671875], 'name': 'suitcase', 'prob': 0.8943426609039307}, '9': {'coordinate': [24.74919319152832, 451.5570068359375, 44.14604187011719, 500.6855773925781], 'name': 'person', 'prob': 0.9752901196479797}, '10': {'coordinate': [268.09417724609375, 478.8925476074219, 290.8290100097656, 516.4414672851562], 'name': 'bench', 'prob': 0.7876744270324707}, '11': {'coordinate': [323.8840026855469, 382.66607666015625, 338.22784423828125, 409.57525634765625], 'name': 'traffic light', 'prob': 0.9629154205322266}, '12': {'coordinate': [465.9528503417969, 469.9328918457031, 479.683837890625, 515.5655517578125], 'name': 'person', 'prob': 0.9485933184623718}, '13': {'coordinate': [211.14134216308594, 393.16192626953125, 276.5450744628906, 574.33984375], 'name': 'person', 'prob': 0.9997686743736267}, '14': {'coordinate': [347.603515625, 469.4003601074219, 361.7298583984375, 501.9714050292969], 'name': 'person', 'prob': 0.9155468940734863}, '15': {'coordinate': [44.581275939941406, 452.2747497558594, 62.73636245727539, 500.3128356933594], 'name': 'person', 'prob': 0.9905517101287842}, '16': {'coordinate': [187.55050659179688, 458.75799560546875, 201.63046264648438, 472.6986083984375], 'name': 'person', 'prob': 0.9451029300689697}}, 'overlap': {'0': {'idA': 0, 'idB': 13, 'area': 921.4536570995115}, '1': {'idA': 1, 'idB': 4, 'area': 245.13681909441948}, '2': {'idA': 2, 'idB': 6, 'area': 420.9153443817049}, '3': {'idA': 4, 'idB': 8, 'area': 40.534330708906054}, '4': {'idA': 5, 'idB': 9, 'area': 11.251169111346826}, '5': {'idA': 8, 'idB': 13, 'area': 414.3129944088869}, '6': {'idA': 10, 'idB': 13, 'area': 317.32206079829484}}}]
    print(FOIL(input_list))

main()
