#include "pystandalone.h"
using namespace std;
int main(int argc, char * argv[]){
	const char moduleName[] = "main", funcName[] = "main";
	runPython(argc, argv, moduleName, funcName);
	return 0;
}
