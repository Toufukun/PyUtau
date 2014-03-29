#include <Python.h>
#include <Windows.h>
#include <cstdlib>
#include <cstdio>
#include <string>
using namespace std;

const char moduleName[] = "pyutauplus",
functionName[] = "resampler";
int main(int argc, char * argv[]){
	// 得到当前可执行文件所在的目录
	char szPath[10240];
	char szCmd[10240];
	GetModuleFileName(NULL, szPath, sizeof(szPath));
	char* p = strrchr(szPath, '\\');
	if (p == NULL){
		printf("Get module file name error!\n");
		return -1;
	}
	*p = 0;

	// 设定运行时的PATH
	sprintf(szCmd, "PATH=%s\\dlls;%%PATH%%", szPath);
	_putenv(szCmd);

	string argList = "[";
	for (int i = 0; i < argc; i++){
		argList += "r'" + string(argv[i]) + "'";
		if (i != argc - 1)
			argList += ",";
	}
	argList += "]";

	// 把sys.path设定为['.', '自己的源代码zip文件', '标准库zip文件', 'dll目录']
	// 然后调用main模块
	sprintf(szCmd,
		"import sys\n"
		"sys.path=['.', r'%s\\pysrc', r'%s\\pythonlib.zip', r'%s\\DLLs']\n"
		"import %s\n"
		"%s.%s(%s)\n",
		szPath, szPath, szPath, moduleName, moduleName, functionName, argList.c_str());

	Py_NoSiteFlag = 1;
	Py_Initialize();
	PyRun_SimpleString(szCmd);
	return 0;
}
