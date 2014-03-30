def _isFlat(s):
    for c in s:
        if c == 'b' or c == '#':
            return False
    return True
class MidiKey:
    key = 96
    def __init__(self,k):
        if isinstance(k,int):
            self.key = k
        elif str.isdigit(k):
            self.key = int(k)
        else:
            Key = [9,11,0,2,4,5,7]
            if 'a' <= k[0] <= 'z':
                k[0]-=32
            if _isFlat(k):
                letter = k[0]
                octave = int(k[1:])
                self.key = (octave - 5) * 12 + 72 + Key[ord(letter) - ord('A')]
            else:
                letter = k[0]
                tone = k[1]
                octave = int(k[2:])
                self.key = (octave - 5) * 12 + 72 + Key[ord(letter) - ord('A')]
                if tone == '#':
                    self.key+=1
                else:
                    self.key-=1
    def to_midi_key(self):
        return self.key
    def to_letter_key(self):
        lKey = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
        octave = (self.key - 11) / 12
        return "%s%d" % (lKey[self.key % 12],octave)

def _test():
    while True:
        s = raw_input()
        k = MidiKey(s)
        print k.to_letter_key(), k.to_midi_key()

if __name__ == '__main__':
    _test()
