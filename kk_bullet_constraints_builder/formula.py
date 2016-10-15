##############################
# Bullet Constraints Builder #
##############################
#
# Written within the scope of Inachus FP7 Project (607522):
# "Technological and Methodological Solutions for Integrated
# Wide Area Situation Awareness and Survivor Localisation to
# Support Search and Rescue (USaR) Teams"
# This version is developed at the Laurea University of Applied Sciences, Finland
# Copyright (C) 2015-2017 Kai Kostack
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

################################################################################

import bpy
mem = bpy.app.driver_namespace

### Import submodules
from global_vars import *      # Contains global variables

###### SymPy detection and import code
### Try to import SymPy
try: import sympy
except:
    pythonLibsPaths = []
    if platform.system() == 'Windows':
        #pythonLibsPaths.append(r"c:\Python34\Lib\site-packages")
        ### Try to find most recent path in registry
        import winreg
        regPath = r"SOFTWARE\Python\PythonCore"
        searchKey = "InstallPath"
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        #reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        try: keyA = winreg.OpenKey(reg, regPath)
        except: pass
        else:
            pathFound = ""
            for i in range(1024):
                try: regPathA = winreg.EnumKey(keyA, i)
                except: pass
                else:
                    keyB = winreg.OpenKey(reg, regPath +"\\" +regPathA)
                    for j in range(1024):
                        try: regPathB = winreg.EnumKey(keyB, j)
                        except: pass
                        else:
                            keyC = winreg.OpenKey(reg, regPath +"\\" +regPathA +"\\" +regPathB)
                            if regPathB == searchKey:
                                try: val = winreg.QueryValueEx(keyC, "")
                                except: pass
                                else: pathFound = val[0]
            if len(pathFound):
                print("Python path found in registry:", pathFound)
                pythonLibsPaths.append(pathFound)                  
        # Add possible Python path(s) to known import paths
        for path in pythonLibsPaths:
            if path not in sys.path: sys.path.append(path)

    elif platform.system() == 'Linux':
        #pythonLibsPaths.append(r"/home/user/.local/lib/python3.4/site-packages")
        # Add possible Python path(s) to known import paths
        for path in pythonLibsPaths:
            if path not in sys.path: sys.path.append(path)

    else: print('Unknown platform detected, unable to guess path to Python:', platform.system())

### Try to import SymPy from paths
try: import sympy
except:
    ### If not found attempt using pip to automatically install SymPy module in Blender
    import subprocess, bpy
    def do(cmd, *arg):
        list = [bpy.app.binary_path_python, '-m', cmd]
        list.extend(arg)
        command = (list)       
        p = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1)
        for line in iter(p.stdout.readline, b''):
            print(line.decode())
        p.stdout.close()
        p.wait()
    #do('pip', '--version')
    do('ensurepip')
    do('pip', 'install', '--upgrade', 'pip')
    do('pip', 'install', 'sympy')

### Ultimate attempt to import SymPy
try: import sympy
except:
    #print("No SymPy module found, continuing without formula simplification feature...")
    qSymPy = 0
else:
    #print("SymPy module found.")
    qSymPy = 1

################################################################################

def convertFloatToStr(value, precision):
    
    global strOut  # For some reason this global construct is needed for exec() to have access to strOut
    exec("global strOut; strOut = (('%0.' +str(precision) +'f')%value).strip('0')")
    if '.' in strOut:
        # If digit count of the integer part is higher than precision then remove fractional part
        strOutInt = strOut.split('.')[0]
        if len(strOutInt) > precision: strOut = strOutInt
    strOut = strOut.rstrip('.')    # Remove ending decimal point if no fractional digits are present
    if strOut == '': strOut = '0'  # Replace a single left over decimal point with 0
    elif strOut[0] == '.': strOut = '0' +strOut  # Add a 0 before a leading decimal point (comment out to disable)
    return strOut

########################################

def splitAndApplyPrecisionToFormula(formulaIn):

    ### Split formula at predefined splitting strings and add spaces
    splitter = ['**', '+', '-', '*', '/', '(', ')', '[', ']', '!=', '>=', '<=', '==', '=']
    formulaOut = ""; charLast = ''; qSkipNext = 0
    for char in formulaIn:
        if qSkipNext:
            charLast = char; qSkipNext = 0; continue
        if charLast in splitter:
            if charLast +char not in splitter: formulaOut += ' ' +charLast +' '
            else: formulaOut += ' ' +charLast +char +' '; qSkipNext = 1
        else: formulaOut += charLast
        charLast = char
    if charLast in splitter: formulaOut += ' ' +charLast
    else: formulaOut += charLast
    formulaOut = formulaOut.replace('  ',' ')
    formulaOut = formulaOut.strip(' ')

    ### Apply precision to separated floats
    formulaToSplit = formulaOut; formulaOut = ''
    for term in formulaToSplit.split(' '):
        try: formulaOut += convertFloatToStr(float(term), 4) +' '
        except: formulaOut += term +' '
    formulaOut = formulaOut.replace('  ',' ')
    formulaOut = formulaOut.strip(' ')

    # Clear all spaces
    formulaOut = formulaOut.replace(' ','')

    return formulaOut

########################################

def combineExpressions():

    props = bpy.context.window_manager.bcb
    i = props.menu_selectedElemGrp
    elemGrps = mem["elemGrps"]
    asst = elemGrps[i][EGSidxAsst]
    
    ### Reinforced Concrete (Beams & Columns)
    if props.assistant_menu == "con_rei_beam":
        # Switch connection type to the recommended type
        elemGrps[i][EGSidxCTyp] = 16  # 7 x Generic
        # Prepare also a height and width swapped (90° rotated) formula for shear and moment thresholds
        for qHWswapped in range(2):
            if not qHWswapped:
                h = asst['h']
                w = asst['w']
            else:
                w = asst['h']
                h = asst['w']
            if h == 0: h = 'h'
            if w == 0: w = 'w'
            fc = asst['fc']
            fs = asst['fs']
            c = asst['c']
            s = asst['s']
            ds = asst['ds']
            dl = asst['dl']
            n = asst['n']
            k = asst['k']

            d = " (" +asst['Exp:d'] +") "
            e = " (" +asst['Exp:e'] +") "
            rho = " (" +asst['Exp:rho'] +") "
            y = " (" +asst['Exp:y'] +") "
            e1 = " (" +asst['Exp:e1'] +") "
            Nn = " (" +asst['Exp:N-'] +") "
            Np = " (" +asst['Exp:N+'] +") "
            Vpn = " (" +asst['Exp:V+/-'] +") "
            Mpn = " (" +asst['Exp:M+/-'] +") "
            
            ### Normalize result upon 1 mm^2, 'a' should be the only var left over
            a = 'a'
            Nn = "(" +Nn +")/(h*w)"
            Np = "(" +Np +")/(h*w)"
            Vpn = "(" +Vpn +")/(h*w)"
            Mpn = "(" +Mpn +")/(h*w)"

            ### Combine all available expressions with each other      
            symbols = ['rho','Vpn','Mpn','pi','fs','fc','ds','dl','e1','Nn','Np','c','s','n','k','h','w','d','e','y','a']  # sorted by length
            cnt = 0; cntLast = -1
            while cnt != cntLast:
                cntLast = cnt
                for symbol in symbols:
                    cnt -= len(d)
                    try:    d   = d.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: d   = d.replace(symbol, eval(symbol))
                    cnt += len(d)
                    cnt -= len(e)
                    try:    e   = e.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: e   = e.replace(symbol, eval(symbol))
                    cnt += len(e)
                    cnt -= len(rho)
                    try:    rho = rho.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: rho = rho.replace(symbol, eval(symbol))
                    cnt += len(rho)
                    cnt -= len(y)
                    try:    y   = y.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: y   = y.replace(symbol, eval(symbol))
                    cnt += len(y)
                    cnt -= len(e1)
                    try:    e1  = e1.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: e1  = e1.replace(symbol, eval(symbol))
                    cnt += len(e1)
                    cnt -= len(Nn)
                    try:    Nn  = Nn.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Nn  = Nn.replace(symbol, eval(symbol))
                    cnt += len(Nn)
                    cnt -= len(Np)
                    try:    Np  = Np.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Np  = Np.replace(symbol, eval(symbol))
                    cnt += len(Np)
                    cnt -= len(Vpn)
                    try:    Vpn = Vpn.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Vpn = Vpn.replace(symbol, eval(symbol))
                    cnt += len(Vpn)
                    cnt -= len(Mpn)
                    try:    Mpn = Mpn.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Mpn = Mpn.replace(symbol, eval(symbol))
                    cnt += len(Mpn)
            
            if qSymPy:
                # Simplify formulas when SymPy module is available
                Nn = str(sympy.simplify(Nn))
                Np = str(sympy.simplify(Np))
                Vpn = str(sympy.simplify(Vpn))
                Mpn = str(sympy.simplify(Mpn))

            if not qHWswapped:
                elemGrps[i][EGSidxBTC] = splitAndApplyPrecisionToFormula(Nn)
                elemGrps[i][EGSidxBTT] = splitAndApplyPrecisionToFormula(Np)
                elemGrps[i][EGSidxBTS] = splitAndApplyPrecisionToFormula(Vpn)
                elemGrps[i][EGSidxBTB] = splitAndApplyPrecisionToFormula(Mpn)
            else:
                Vpn9 = splitAndApplyPrecisionToFormula(Vpn)
                Mpn9 = splitAndApplyPrecisionToFormula(Mpn)
                Vpn = elemGrps[i][EGSidxBTS]
                Mpn = elemGrps[i][EGSidxBTB]
                if Vpn9 != Vpn: elemGrps[i][EGSidxBTS9] = splitAndApplyPrecisionToFormula(Vpn9)
                else:           elemGrps[i][EGSidxBTS9] = ""
                if Mpn9 != Mpn: elemGrps[i][EGSidxBTB9] = splitAndApplyPrecisionToFormula(Mpn9)
                else:           elemGrps[i][EGSidxBTS9] = ""
       
    ### Reinforced Concrete (Walls & Slabs)
    elif props.assistant_menu == "con_rei_wall":
        # Switch connection type to the recommended type
        elemGrps[i][EGSidxCTyp] = 16  # 7 x Generic
        # Prepare also a height and width swapped (90° rotated) formula for shear and moment thresholds
        for qHWswapped in range(2):
            if not qHWswapped:
                h = asst['h']
                w = asst['w']
            else:
                w = asst['h']
                h = asst['w']
            if h == 0: h = 'h'
            if w == 0: w = 'w'
            fc = asst['fc']
            fs = asst['fs']
            c = asst['c']
            s = asst['s']
            ds = asst['ds']
            dl = asst['dl']
            n = asst['n']
            k = asst['k']

            d = " (" +asst['Exp:d'] +") "
            e = " (" +asst['Exp:e'] +") "
            rho = " (" +asst['Exp:rho'] +") "
            y = " (" +asst['Exp:y'] +") "
            e1 = " (" +asst['Exp:e1'] +") "
            Nn = " (" +asst['Exp:N-'] +") "
            Np = " (" +asst['Exp:N+'] +") "
            Vpn = " (" +asst['Exp:V+/-'] +") "
            Mpn = " (" +asst['Exp:M+/-'] +") "
            
            ### Normalize result upon 1 mm^2, 'a' should be the only var left over
            a = 'a'
            Nn = "(" +Nn +")/(h*w)"
            Np = "(" +Np +")/(h*w)"
            Vpn = "(" +Vpn +")/(h*w)"
            Mpn = "(" +Mpn +")/(h*w)"

            ### Combine all available expressions with each other      
            symbols = ['rho','Vpn','Mpn','pi','fs','fc','ds','dl','e1','Nn','Np','c','s','n','k','h','w','d','e','y','a']  # sorted by length
            cnt = 0; cntLast = -1
            while cnt != cntLast:
                cntLast = cnt
                for symbol in symbols:
                    cnt -= len(d)
                    try:    d   = d.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: d   = d.replace(symbol, eval(symbol))
                    cnt += len(d)
                    cnt -= len(e)
                    try:    e   = e.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: e   = e.replace(symbol, eval(symbol))
                    cnt += len(e)
                    cnt -= len(rho)
                    try:    rho = rho.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: rho = rho.replace(symbol, eval(symbol))
                    cnt += len(rho)
                    cnt -= len(y)
                    try:    y   = y.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: y   = y.replace(symbol, eval(symbol))
                    cnt += len(y)
                    cnt -= len(e1)
                    try:    e1  = e1.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: e1  = e1.replace(symbol, eval(symbol))
                    cnt += len(e1)
                    cnt -= len(Nn)
                    try:    Nn  = Nn.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Nn  = Nn.replace(symbol, eval(symbol))
                    cnt += len(Nn)
                    cnt -= len(Np)
                    try:    Np  = Np.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Np  = Np.replace(symbol, eval(symbol))
                    cnt += len(Np)
                    cnt -= len(Vpn)
                    try:    Vpn = Vpn.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Vpn = Vpn.replace(symbol, eval(symbol))
                    cnt += len(Vpn)
                    cnt -= len(Mpn)
                    try:    Mpn = Mpn.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Mpn = Mpn.replace(symbol, eval(symbol))
                    cnt += len(Mpn)
            
            if qSymPy:
                # Simplify formulas when SymPy module is available
                Nn = str(sympy.simplify(Nn))
                Np = str(sympy.simplify(Np))
                Vpn = str(sympy.simplify(Vpn))
                Mpn = str(sympy.simplify(Mpn))

            if not qHWswapped:
                elemGrps[i][EGSidxBTC] = splitAndApplyPrecisionToFormula(Nn)
                elemGrps[i][EGSidxBTT] = splitAndApplyPrecisionToFormula(Np)
                elemGrps[i][EGSidxBTS] = splitAndApplyPrecisionToFormula(Vpn)
                elemGrps[i][EGSidxBTB] = splitAndApplyPrecisionToFormula(Mpn)
            else:
                Vpn9 = splitAndApplyPrecisionToFormula(Vpn)
                Mpn9 = splitAndApplyPrecisionToFormula(Mpn)
                Vpn = elemGrps[i][EGSidxBTS]
                Mpn = elemGrps[i][EGSidxBTB]
                if Vpn9 != Vpn: elemGrps[i][EGSidxBTS9] = splitAndApplyPrecisionToFormula(Vpn9)
                else:           elemGrps[i][EGSidxBTS9] = ""
                if Mpn9 != Mpn: elemGrps[i][EGSidxBTB9] = splitAndApplyPrecisionToFormula(Mpn9)
                else:           elemGrps[i][EGSidxBTS9] = ""
                
################################################################################
