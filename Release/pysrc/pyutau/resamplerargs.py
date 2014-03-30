from base64pb import UtauBase64PitchBend
from midikey import MidiKey
import sys

class UtauResamplerArguments:
    def __init__(self,args=["","","C5","100","","0","0","0","0","100","0"]):
        if (not isinstance(args,list)) or (len(args) != 13 and len(args) != 11):
            raise Exception("bad utau resampler arguments (len=%d)" % len(args))
        self.arg = {}
        arg_name = ["in_wav","out_wav","dest_key","cons_spd","flags",
                  "head_offset","dest_dur","cons_len","tail_offset",
                  "vol","mod"]
        args[2]=MidiKey(args[2])
        for i in [3] + range(5,10+1):
            args[i] = eval(args[i])
        for i in range(11):
            self.arg[arg_name[i]] = args[i]
        self.orig_len = len(args)
        if len(args) > 11:
            self.arg["tempo"] = float(args[-2][1:])
            self.arg["base64_pb"] = args[-1]
        else:
            self.arg["tempo"] = 120.0
            self.arg["base64_pb"] = "AA"
        self.arg["pb"] = UtauBase64PitchBend(args[-1])
    def __getitem__(self, index):
        if not self.arg.has_key(index):
            return ""
        return self.arg[index]

def _test():
    arg = UtauResamplerArguments()
    print arg.arg

if __name__ == '__main__':
    _test(sys.argv)
