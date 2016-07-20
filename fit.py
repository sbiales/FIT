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
        if (current.find("//") != -1) :
            current = current[:current.find("//")] #ignore anything after '//'
            continue
        #note: need to check for/skip block comments
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
        if (current.find("//") != -1) :
            current = current[:current.find("//")]
            continue
        #note: need to check for/skip block comments
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
                    #print("line: ", cur)
                    loc += 3 #move 'pointer' to account for '+= '
                    front = cur[:loc]
                    back = cur[loc:-2] #strip the ;\n
                    perturbed = front + 'inject(' + back + ');\n'
                    lines[l] = perturbed
                    print("Perturbed line ", l+1)
                    print(lines[l][:-1])
                          
#create and write output file line by line
def output(lines) :
    with open(outname, 'w') as out :
        for line in lines :
            out.write(line)

#Add the necessary functions/code to the code from the original file
#Takes in parsed error code file and readlines from original file
def merge(parsed, lines) :
    stdlib = 0
    floatlib = 0
    newlines = []
    incl = parsed['incl']
    decl = parsed['decl']
    func = parsed['func']
    last = []
    #first the includes. avoid duplicates
    for item in incl :
        if (lines.count(item) != 0) :
            incl.remove(item)
    for num, line in enumerate(lines) :
        #if we see an include statement, note the line number
        if (line.find("#include") != -1) :
            last.append(num)
        newlines.append(line)
    #insert declarations after the last '#include' statement
    for d in range(len(decl)) :
        final = max(last) #should be the last '#include' statement
        newlines.insert(final+1+d, decl[d])
    #insert includes at the top
    for i in range(len(incl)) :
        newlines.insert(i, incl[i])
    #insert functions at the bottom
    for f in func :
        newlines.append(f)
    return newlines    

#Parses the error file
#identifies functions by looking for '//function' on the preceding line
#Returns dict{includes; declarations; functions}
def parsefile(ename) :       
    with open(ename, 'r') as file :
        result = {"incl":[], "decl":[], "func":[]}
        lines = file.readlines()
        numlines = len(lines)
        end = 0
        for line in range(numlines) :
            cur = lines[line]
            if (line < end) :
                continue #we are inside a function
            if (cur.find("#include") != -1) :
                result['incl'].append(cur)
            elif (cur.find(";") != -1) :
                result['decl'].append(cur)
            elif (cur.find("//function") != -1) :
                start = line+1
                end = boundaries(lines, start)
                for l in lines[start:end+1] :
                    result['func'].append(l)
        return result

    
#MAIN PROGRAM

filename = input("File to read: ")
#outname = input("Output file name: ")
outname = "output.cc" #comment this out if user chooses output filename
#errorname = input("Error code file: ")
errorname = "i.cc" #comment this out if user specifies error file
function = input("Function to perturb: ")
#rate = input("Error rate: ")
rate = 0 #comment this out if user specifies error rate

with open(filename, 'r') as file :
    lines = file.readlines()
    parsed = parsefile(errorname)
    lines = merge(parsed, lines)
    numlines = len(lines)

    for line in range(numlines) :
        current = lines[line]
        if(current.count(function) != 0) :
            print("Found instance at line ", line+1)
            if(current.find(";") == -1) :
                print("DEFINED at line ", line+1)
                start = line
                print("Finding function boundaries...\n")
                end = boundaries(lines, start) #finds end of function (given start)
                print("Boundaries found. Perturbing function...\n")
                perturb(lines, start, end)
                output(lines)
                parsed = parsefile(errorname)


