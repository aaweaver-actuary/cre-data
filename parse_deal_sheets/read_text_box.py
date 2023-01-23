import pyxlsb
import openpyxl
import pandas as pd
import zipfile as z


class Sheet(str):
    def __init__(self, str_path):
        if str_path.find('.xlsx') != -1:
            self.filetype = 'xlsx'
        elif str_path.find('.xlsb') != -1:
            self.filetype = 'xlsb'
        elif str_path.find('.xlsm') != -1:
            self.filetype = 'xlsm'
        else:
            if str_path.find('.xls') != -1:
                self.filetype = 'xls'
            else:
                print('Please pass an Excel file')
                self.filetype = None

    @property
    def shapes(this):
        s = z.ZipFile(this)
        xs = pd.Series(s.infolist())
        test = [s.infolist()[i].filename.find('drawing') != -1 for i in range(len(s.infolist()))]
        drawings = xs[test].tolist()
        all_drawings = [drawings[i].filename for i in range(len(drawings))]
        if this.filetype=='xlsx':
            p=all_drawings  # shapes path, *.xlsx default
        elif this.filetype=='xls':
            p='drs/shapexml.xml'  # shapes path, *.xls default
        else:
            p=all_drawings
            
        if type(p)==list:
            out = []
            for pth in p:
                out.append(XML(s.read(pth)))
        
        return(out)


class XML(object):
    def __init__(self, value):
        self.value = str(value)

    def __repr__(self):
        return repr(self.value)

    def __getitem__(self, i):
        return self.value[i]

    def tag_content(self, tag):
        return [XML(i) for i in self.value.split(tag)[1::2]]

    @property
    def text(self):
        t = self.tag_content('xdr:txBody')  # list of XML codes, each containing a seperate textboxes, messy (with extra xml that is)
        l = [i.tag_content('a:p>') for i in t]  # split into sublists by line breaks (inside the textbox), messy
        w = [[[h[1:-2] for h in i.tag_content('a:t')] if i else ['\n'] for i in j] for j in l]  # clean into sublists by cell-by-cell basis (and mind empty lines)
        l = [[''.join(i) for i in j] for j in w]  #  join lines overlapping multiple cells into one sublist
        return ['\n'.join(j) for j in l]  #  join sublists of lines into strings seperated by newline char

def read_text_box(filename):


    shps = pd.Series(Sheet(filename).shapes)

    out1 = [shps[i].text for i in range(shps.shape[0])][0][1]
    
    out=''
    for x in out1:
        out = out + x
        
        
    out = out.replace("\\t", "\t")
    out = out.strip()
        
    return(out)