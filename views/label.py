import re
def get_total_list1(dict_list):
    total_object=[]
    total_list=[]
    for dictionary in dict_list:
        for image_num in range(len(dictionary)):
            for objects_num in range(len(dictionary[image_num]['object'])):
                name=dictionary[image_num]['object'][str(objects_num)]['name']
                if name not in total_object:
                    total_object.append(name)
    for dictionary in dict_list:
        for image_num in range(len(dictionary)):
            image_list=[]
            position_list=[]
            for objects_num in range(len(dictionary[image_num]['object'])):
                name=dictionary[image_num]['object'][str(objects_num)]['name']
                position=total_object.index(name)
                if position not in position_list:
                    position_list.append(position)
            object_numbers=[0 for i in range(len(position_list))]
            for objects_num in range(len(dictionary[image_num]['object'])):
                name=dictionary[image_num]['object'][str(objects_num)]['name']
                position=total_object.index(name)
                object_numbers[position_list.index(position)]+=1
            for index,objects in enumerate(position_list):
                has=total_object[objects]+"(image"+str(dictionary[image_num]['imageId'])+","+str(objects)+")"
                num="num"+"("+str(objects)+","+str(object_numbers[index])+")"
                image_list.append(has)
                image_list.append(num)
            for objects_num in range(len(dictionary[image_num]['overlap'])):
                object1_name=dictionary[image_num]['object'][str(dictionary[image_num]['overlap'][str(objects_num)]["idA"])]['name']
                object2_name=dictionary[image_num]['object'][str(dictionary[image_num]['overlap'][str(objects_num)]["idB"])]['name']
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
