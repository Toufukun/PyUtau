def _bib64_to_int(s):
    res = 0
    for c in s:
        res*=64
        if 'A' <= c <= 'Z':
            res+=ord(c) - ord('A')
        elif 'a' <= c <= 'z':
            res+=ord(c) - ord('a') + 26
        elif c == '/':
            res+=63
        elif c == '+':
            res+=62
        else:
            res+=ord(c) - ord('0') + 52
    if res & (1 << 11):
        res = (res - 1) ^ ((1 << 12) - 1)
        res = -res
    return res
def _int_to_bib64(x):
    s = ""
    if (x < 0):
        x = -x
        x = (x ^ ((1 << 12) - 1)) + 1
    a = [int(x / 64),x % 64]
    for p in a:
        if 0 <= p < 26:
            s+=chr(ord('A') + p)
        elif p < 52:
            s+=chr(ord('a') + p - 26)
        elif p == 63:
            s+='/'
        elif p == 62:
            s+='+'
        else:
            s+=chr(ord('0') + p - 52)
    return s
class UtauBase64PitchBend:
    def __init__(self,str=""):
        self.pba = []
        i = 0
        repetition_num = 0
        in_sharp = False
        buf = ""
        while i < len(str):
            if str[i] == '#':
                if in_sharp:
                    in_sharp = False
                    repetition_num-=1
                    while repetition_num >= 0:
                        self.pba.append(buf)
                        repetition_num-=1
                else:
                    in_sharp = True
                    repetition_num = 0
            else:
                if in_sharp:
                    repetition_num*=10
                    repetition_num+=ord(str[i]) - ord('0')
                else:
                    if isinstance(buf,int):
                        buf = ""
                    buf+=str[i]
                    if len(buf) == 2:
                        buf = _bib64_to_int(buf)
                        if i + 1 == len(str) or str[i + 1] != '#':
                            self.pba.append(buf)
            i+=1
    def __getitem__(self, index):
        return self.pba[index]
    def get_array(self):
        return self.pba[:]
    def get_base64(self):
        if len(self.pba) == 0:
            return ""
        str = ""
        prev = self.pba[0]
        cnt = 0
        for p in self.pba:
            if p != prev:
                str+=_int_to_bib64(prev)
                if cnt > 1:
                    str+="#%d#" % cnt
                cnt = 1
                prev = p
            else:
                cnt+=1
        str+=_int_to_bib64(prev)
        if cnt > 1:
            str+="#%d#" % cnt
        return str

def _test():
    while True:
        s = raw_input()
        p = UtauBase64PitchBend(s)
        print str(p.get_array()), str(p.get_base64())

if __name__ == '__main__':
    _test()
    