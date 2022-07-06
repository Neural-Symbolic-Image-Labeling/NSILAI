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
    for dictionary in input_list:
        for image_num in range(len(dictionary)):
            for objects_num in range(len(dictionary[image_num]['object'])):
                name=dictionary[image_num]['object'][str(objects_num)]['name']
                if name not in total_object:
                    total_object.append(name)
    for dictionary in input_list:
        for image_num in range(len(dictionary)):
            image_list=[]
            string=dictionary[image_num]['type']+"(image"+str(image_number)+")"
            image_list.append(string)
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
                has=total_object[objects]+"(image"+str(image_number)+","+str(objects)+")"
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