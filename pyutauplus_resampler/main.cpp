#include "..\pystandalone\pystandalone.h"
using namespace std;
int main(int argc, char * argv[]){
	const char moduleName[] = "pyutauplus", funcName[] = "resampler";
	runPython(argc, argv, moduleName, funcName);
	return 0;
}
