# PyUtauPlus
# Copyright 2014 Toufukun

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pyutau import *
import os,sys,subprocess

def resampler(argv):
    verbose=True

    resampler_list = ["resampler.exe","fresamp.exe","TIPS.exe","pyuppslink"]
    arg = UtauResamplerArguments(argv[1:])
    if verbose:
        print argv[0]
        for k,v in arg.arg.items():
            if k == "pit":
                print k,v.get_array()
            else:
                print k,v
    ptr_sel_st = max(arg["flags"].find("\\"),arg["flags"].find("/"))
    if ptr_sel_st == -1:
        resampler_num = 0
    else:
        ptr_sel_st+=1
        ptr_sel_ed = ptr_sel_st
        while ptr_sel_ed < len(arg["flags"]) and arg["flags"][ptr_sel_ed].isdigit():
            ptr_sel_ed+=1
        resampler_num = arg["flags"][ptr_sel_st:ptr_sel_ed]
        if resampler_num == "":
            resampler_num = 0
        else:
            resampler_num = int(resampler_num)

    if resampler_num > len(resampler_list):
        target = "resampler.exe"
    else:
        target = resampler_list[resampler_num]

    dirname,filename = os.path.split(os.path.abspath(argv[0]))
    if target.endswith("exe"):
        cmdarg = ""
        for x in argv[1:]:
            if str(x).find(" ") == -1:
                if x == "":
                    cmdarg+="0 "
                else:
                    cmdarg+=x + " "
            else:
                    cmdarg+='"' + x + '" '
        # print "%s\\%s %s" % (dirname,target,cmdarg)
        subprocess.call("%s\\%s %s" % (dirname,target,cmdarg))
    else:
        # print target,argv
        exec("import %s" % target)
        exec("%s.resample(%s)" % (target,argv))
