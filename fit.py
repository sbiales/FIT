#Fault Injection Tool
#Writes to output file 'output.cc'
#Consider: X~want to create new output file, not edit original
#           ~want to inject the inject() function into the output file
#           ~want to have choice to perturb more than 1 function
#Assumed: ~function to perturb provided
#         ~perturb a single += computation in a for loop
#         ~inject() func is already in the c program
#         ~type of z is double (for min/max in inject func)

#takes the result of readlines() and first line of a function
#returns last line of the function
def boundaries(lines, sline) :
    numlines = len(lines)
    count = 0
    for line in range(sline,numlines) :
        current = lines[line]
        #note: need to check for/skip comments
        if (current.count("{") != 0) :
            count += current.count("{")
            #print("{ at line ", line+1)
        if (current.count("}") != 0) :
            count -= current.count("}")
            #print("} at line ", line+1)
        if ((count == 0) & (line != sline)) :
            return line
        
#takes lines and boundaries of function, finds a += computation in a
#for loop and injects error into it by calling inject() function
def perturb(lines, start, end) :
    for line in range(start, end) :
        current = lines[line]
        #note: need to check for/skip comments
        #also need to account for things including 'for' in the name?
        if (current.count("for") != 0) :
            s = line
            e = boundaries(lines, s)
            for l in range(s, e) :
                cur = lines[l]
                #if not(cur.find("+=") == -1) :
                if (cur.count("+=") != 0) :
                    loc = cur.find("+=")
                    print("found += at line ", l+1, " and loc ", loc)
                    print("line: ", cur)
                    loc += 3 #move 'pointer' to account for '+= '
                    front = cur[:loc]
                    back = cur[loc:-2] #strip the ;\n
                    perturbed = front + 'inject(' + back + ');\n'
                    lines[l] = perturbed
                    print("Perturbed line ", l+1)
                    print(lines[l])
                          
#create and write output file line by line
def output(lines) :
    with open("output.cc", 'w') as out :
        for line in lines :
            out.write(line)
            


#MAIN PROGRAM

filename = input("File to read: ")
function = input("Function to perturb: ")

with open(filename, 'r') as file :
    lines = file.readlines()
    numlines = len(lines)

    for line in range(numlines) :
        current = lines[line]
        if(current.count(function) != 0) :
            print("Found instance at line ", line+1)
            if(current.find(";") == -1) :
                print("DEFINED at line ", line+1)
                start = line
                end = boundaries(lines, start) #finds end of function (given start)
                perturb(lines, start, end)
                output(lines)
                

