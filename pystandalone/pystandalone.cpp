#include <Python.h>
#include <Windows.h>
#include <cstdlib>
#include <cstdio>
#include <string>
#include "pystandalone.h"
using namespace std;

/*
	This code is a modified version on
	http://wiki.woodpecker.org.cn/moin/LeoJay/PyPackage
	
	Thanks to its author, Leo Jay, providing a very fast way
	to modify Python programs on Windows by just editing
	the .py script out of thr .exe.
*/

int runPython(int argc, char* argv[], const char* moduleName, const char* functionName){
	// �õ���ǰ��ִ���ļ����ڵ�Ŀ¼
	char szPath[10240];
	char szCmd[10240];
	GetModuleFileName(NULL, szPath, sizeof(szPath));
	char* p = strrchr(szPath, '\\');
	if (p == NULL){
		printf("Get module file name error!\n");
		return -1;
	}
	*p = 0;

	// �趨����ʱ��PATH
	sprintf(szCmd, "PATH=%s\\dlls;%%PATH%%", szPath);
	_putenv(szCmd);

	string argList = "[";
	for (int i = 0; i < argc; i++){
		argList += "r'" + string(argv[i]) + "'";
		if (i != argc - 1)
			argList += ",";
	}
	argList += "]";

	// ��sys.path�趨Ϊ['.', '�Լ���Դ����zip�ļ�', '��׼��zip�ļ�', 'dllĿ¼']
	// Ȼ�����mainģ��
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


