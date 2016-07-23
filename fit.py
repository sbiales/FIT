#Fault Injection Tool
#Writes to output file 'output.cc' by default
#Consider: ~need to deal with block comments
#          ~make sure file doesnt contain functions by the names of those inserted
#Assumed: ~function to perturb provided
#         ~perturb all += computations in a for loop
#         ~inject() func exists (and works)
#         ~type of z is double (for min/max in inject func)
#         ~error rate is stored in error_rate function

#takes the result of readlines() and first line of a function
#returns last line of the function
def boundaries(lines, sline) :
    numlines = len(lines)
    seen = 0
    count = 0
    cend = 0
    for line in range(sline, numlines) :
        current = lines[line]
        if (line <= cend) :
            continue #we are inside a block comment
        if (current.find("/*") != -1) :
            cend = block(lines, line)
            current = current[:current.find("/*")]
        if (current.find("//") != -1) :
            current = current[:current.find("//")] #ignore anything after '//'
        if (current.count("{") != 0) :
            count += current.count("{")
            seen = 1 #want to make sure we have seen a { before giving up
        if (current.count("}") != 0) :
            count -= current.count("}")
        if ((count == 0) & (seen != 0)) :
            return line

#returns last line of a block comment (c code, so */)
def block(lines, sline) :
    numlines = len(lines)
    for line in range(sline, numlines) :
        current = lines[line]
        if (current.find("*/") != -1) :
            return line

#determine first line of innermost for loop
def innermost(lines, sline, eline) :
    #if we know there's def no more loops, don't waste time looking
    if (' '.join(lines[sline+1:eline]).split().count('for') == 0) :
        return sline
    cend = 0
    for line in range(sline+1, eline) :
        current = lines[line]
        if (line <= cend) :
            continue #we are inside a block comment
        if (current.find("/*") != -1) :
            cend = block(lines, line)
            current = current[:current.find("/*")]
        if (current.find("//") != -1) :
            current = current[:current.find("//")]
        if (current.split().count("for") != 0) :
            e = boundaries(lines, line)
            return innermost(lines, line, e)
    return sline
        
#takes lines and boundaries of function, finds a += computation in a
#for loop and injects error into it by calling inject() function
def perturb(lines, start, end) :
            s = innermost(lines, start, end)
            e = boundaries(lines, s)
            for l in range(s, e) :
                cur = lines[l]
                #if not(cur.find("+=") == -1) :
                if (cur.count("+=") != 0) :
                    loc = cur.find("+=")
                    print("found += at line ", l+1, " and loc ", loc)
                    loc += 2 #move 'pointer' to account for '+='
                    front = cur[:loc]
                    scol = cur.find(";")
                    back = cur[loc:scol] #strip the ;\n
                    perturbed = front + ' inject(' + back + ');\n'
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
    newlines.append('\n')
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
        end = 0
        for line, cur in enumerate(lines) :
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

#checks if instance of function is a definition or prototype
def checkdef(lines, sline) :
    current = lines[sline]
    while(current.find(")") ==-1) : #we are dealing with multiline
        current 
        if(current.find(";") == -1) :
           print("DEFINED at line ", line+1)
    
#MAIN PROGRAM

filename = input("File to read: ")
#outname = input("Output file name: ")
outname = "output.cc" #comment this out if user chooses output filename
#errorname = input("Error code file: ")
errorname = "i.cc" #comment this out if user specifies error file
functions = input("Functions to perturb (separate w/ spaces): ")
rate = input("Error rate: ")

with open(filename, 'r') as file :
    lines = file.readlines()
    parsed = parsefile(errorname)
    for num, d in enumerate(parsed['decl']) : #account for user specified rate
        if (d.find("error_rate") != -1) :
            loc = d.find("error_rate")
            loc += 10 #move 'pointer' past the word
            d = d[:loc] #truncate the line
            d = d + " = " + str(rate) + ";\n"
            parsed['decl'][num] = d            
    lines = merge(parsed, lines)
    functions = functions.split()

    cend = 0
    for function in functions :
        for line, current in enumerate(lines) :
            if (line <= cend) :
                continue #we are inside a block comment
            if (current.find("/*") != -1) :
                cend = block(lines, line)
                current = current[:current.find("/*")]
            if (current.find("//") != -1) :
                current = current[:current.find("//")] #ignore anything after '//'
            if(current.count(function) != 0) :
                print("Found ", function, " at line ", line+1)                    
                if(current.find(";") == -1) :
                    print("DEFINED at line ", line+1)
                    start = line
                    print("\nFinding function boundaries...")
                    end = boundaries(lines, start) #finds end of function (given start)
                    print("Boundaries found. Perturbing function...\n")
                    perturb(lines, start, end)
    output(lines)
