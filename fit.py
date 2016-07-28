#Fault Injection Tool
#Writes to output file 'filename-cfgfile.cc'
#Assumed: ~perturb all += computations in innermost for loop
#         ~type of z is double (for min/max in inject func)
#         ~File outputs results in format 

import configparser as cp
import os, re

#takes the result of readlines() and first line of a function
#returns last line of the function
def boundaries(lines, sline) :
    numlines = len(lines)
    seen = 0
    count = 0
    cend = -1
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
        if ((count <= 0) & (seen != 0)) :
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
    #if (' '.join(lines[sline+1:eline]).count('for') == 0) :
    #    return sline
    cend = -1
    for line in range(sline+1, eline) :
        current = lines[line]
        if (line <= cend) :
            continue #we are inside a block comment
        if (current.find("/*") != -1) :
            cend = block(lines, line)
            current = current[:current.find("/*")]
        if (current.find("//") != -1) :
            current = current[:current.find("//")]
        #if ((current.split().count("for") != 0) :
        if (current.find("for") != -1) :
            e = boundaries(lines, line)
            return innermost(lines, line, e)
    return sline
        
#takes lines and boundaries of function, finds a += computation in a
#for loop and injects error into it by calling inject() function
def perturb(lines, erate, start, end) :
            s = innermost(lines, start, end)
            e = boundaries(lines, s)
            #print(s, " : ", e, " Boundaries of for loop")
            for l in range(s, e) :
                cur = lines[l]
                if (cur.count("+=") != 0) :
                    loc = cur.find("+=")
                    print("found += at line ", l+1, " and loc ", loc)
                    loc += 2 #move 'pointer' to account for '+='
                    front = cur[:loc]
                    scol = cur.find(";")
                    back = cur[loc:scol] #strip the ;\n
                    perturbed = front + ' inject(' + erate + "," + back + ');\n'
                    lines[l] = perturbed
                    print("Perturbed line ", l+1)
                    print(lines[l][:-1])
                    
#create and write output file line by line
def output(lines) :
    with open(outname, 'w') as out :
        for line in lines :
            out.write(line)

#Includes the error file
def include(lines, ename) :
    newlines = lines
    incl = '#include "' + ename + '"\n'
    newlines.insert(0, incl)
    return newlines

#comments out all printf statements in the file
def psuppress(lines) :
    cend = -1
    for line, cur in enumerate(lines) :
        if (line <= cend) :
            continue #we are inside a block comment
        if (cur.find("/*") != -1) :
            cend = block(lines, line)
            cur = cur[:cur.find("/*")]
        if (cur.find("//") != -1) :
            cur = cur[:cur.find("//")]
        if (cur.find("print") != -1) :
            if (cur.find("fprint") == -1) :
                loc = cur.find("print")
                cur = cur[:loc] +'//' + cur[loc:]
                lines[line] = cur
    return lines
    

#edits the error file with the user specified rate
def errordef(ename, rate) :       
    with open(ename, 'r+') as file :
        lines = file.readlines()
        for line, cur in enumerate(lines) :
            if (cur.find("double error_rate") != -1) :
                loc = cur.find("error_rate")
                loc += 10 #move 'pointer' past the word
                cur = cur[:loc] #truncate the line
                cur = cur + " = " + str(rate) + ";\n"
                lines[line] = cur
    with open(ename, 'w') as file :
        file.writelines(lines)                

#gets rid of file extensions
def stripname(file) :
    if (file.find('.') != -1) :
        loc = file.find('.')
        file = file[:loc]
    return file

#assumes code is compiled; executes code and retrieves results
#returns percent correct
def getresults(ex) :
    results = os.popen(ex).readlines()
    regex = re.compile("(\d+)( : )(\d+)")
    results = [m.group(0) for l in results for m in [regex.search(l) ] if m]
    result = results[0]
    m = regex.search(result)
    num = int(m.group(1))
    den = int(m.group(3))
    return num/den*100
    

#checks if instance of function is a definition or prototype
#obviously incomplete still....
def checkdef(lines, sline) :
    current = lines[sline]
    
############################################################
#MAIN PROGRAM
    
cfg = input("Config file: ")

#set values from config file
config = cp.ConfigParser()
config.read(cfg)
filename = config.get('attributes', 'filename')
errorfile = config.get('attributes', 'errorfile')
functions = config.get('attributes', 'functions')
percents = config.get('attributes', 'percents')
rate = config.get('attributes', 'rate')
runs = int(config.get('attributes', 'runs'))
outname = stripname(filename) + '-' + stripname(cfg) + '.cc'
compargs = '' #by default, no extra arguments
cmdargs = ''
if (config.has_option('args', 'compile')) :
    compargs = ''.join(config.get('args', 'compile'))
if (config.has_option('args', 'execute')) :
    cmdargs = ''.join(config.get('args', 'execute'))

with open(filename, 'r') as file :
    lines = file.readlines()
    errordef(errorfile, rate)
    lines = include(lines, errorfile)
    #lines = psuppress(lines)
    functions = functions.split()
    percents = percents.split()

    for index, function in enumerate(functions) :
        cend = -1
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
                    print("\nFinding ",function," boundaries...")
                    end = boundaries(lines, start) #finds end of function (given start)
                    print("Boundaries found. Perturbing ",function,"...\n")
                    erate = percents[index]
                    print(function, " : ", erate, "%")
                    perturb(lines, erate, start, end)
    output(lines)
#compile and execute baseline
compiler = "g++ " + filename + " " + compargs
command = "./a.out " + cmdargs
os.system(compiler)
baseline = getresults(command)

#run analysis
compiler = "g++ " + outname + " " + compargs
command = "./a.out " + cmdargs
os.system(compiler)
results = []
for i in range(runs) :
    results.append(getresults(command))
print(results)
