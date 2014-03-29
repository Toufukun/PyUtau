#include <Python.h>
#include <Windows.h>
#include <cstdlib>
#include <cstdio>
#include <string>
using namespace std;

const char moduleName[] = "pyutauplus",
functionName[] = "resampler";
int main(int argc, char * argv[]){
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
