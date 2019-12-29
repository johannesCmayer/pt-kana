import json

hiragana = json.load(open('hiragana.json'))
katakana = json.load(open('katakana.json'))

class Instance:
    def __init__(self, target, translation, frequency, correct, incorrect):
        self.target = target
        self.translation = translation
        self.frequency = frequency
        self.correct = correct
        self.incorrect = incorrect

l = []
for (hk, hv), (kk, kv) in zip(hiragana.items(), katakana.items()):
    l.append(Instance(hk, hv, 0, [], []).__dict__)
    l.append(Instance(kk,kv,0, [], []).__dict__)

print(f"generated file with {len(l)} entries")
tdump = json.dumps(l,indent=4)
with open("alternating_kana.json", 'w') as f:
    f.write(tdump)