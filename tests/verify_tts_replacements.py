import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dictionary_manager import DictionaryManager
m=DictionaryManager.__new__(DictionaryManager)
m._words={'55@':'ฮ่าๆ','w@':'ขำ','5{4+}':'ฮา','{URL}':'ลิงก์','nvidia':'เอ็นวิเดีย'}
assert m.apply_replace('555555')=='ฮ่าๆ'
assert m.apply_replace('5')=='5'
assert m.apply_replace('WWW!')=='ขำ!'
assert m.apply_replace('NVIDIA')=='เอ็นวิเดีย'
assert m.apply_replace('https://example.com/test')=='ลิงก์'
m._words={'5{4+}':'ฮา'}
assert m.apply_replace('555')=='555' and m.apply_replace('555555')=='ฮา'
m._words={'555':'หัวเราะ'}
assert m.apply_replace('x555y')=='xหัวเราะy'
m._words={'55@':{'display':'','read':'ฮ่าๆ'}}
assert m.apply_replace('55555')=='ฮ่าๆ'
print('PASS legacy special repeat, URL and pronunciation rules')
