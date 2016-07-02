#include "clang"

Rewriter rewriter;
int numFunctions = 0;

int main(int argc, const char **argv) {
    // parse the command-line args passed to your code
    CommonOptionsParser op(argc, argv);
    // create a new Clang Tool instance (a LibTooling environment)
    ClangTool Tool(op.getCompilations(), op.getSourcePathList());
 
    // run the Clang Tool, creating a new FrontendAction (explained below)
    int result = Tool.run(newFrontendActionFactory<ExampleFrontendAction>());
 
    errs() << "\nFound " << numFunctions << " functions.\n\n";
    // print out the rewritten source code ("rewriter" is a global var.)
    rewriter.getEditBuffer(rewriter.getSourceMgr().getMainFileID()).write(errs());
    return result;
}