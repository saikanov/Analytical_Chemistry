#Import library
import streamlit as st 
import pandas as pd 
import numpy as np 
import scipy 
import matplotlib.pyplot as plt 
from PIL import Image
from sympy import symbols, Eq, latex , simplify , N


#set title image
img = Image.open('logo.jpg')

st.set_page_config(page_title='novatomic', page_icon = img)

#set config
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """

st.markdown(hide_menu_style, unsafe_allow_html = True)


st.sidebar.title('Pilih Metode')
option = ['External Standard','Internal Standard','Standard Adisi']
choice = st.sidebar.selectbox('Pilih Metode Standard yg sesuai',option)



if choice == 'External Standard':

    ##### SPEKTROFOTOMETRI/EXTERNAL STANDARD

    #fungsi c terukur
    def c_terukur(abs,slope,intercept):
        ct = (abs-intercept)/slope
        return ct
    #fungsi sampel solid
    def sample_S(c_terukur,v_lt,FP,bobot_S):
        ss = (c_terukur*v_lt*FP*0.001)/(bobot_S*0.001)
        return ss
    #fungsi perhitungan sampel liquid
    def sampel_L(c_terukur,FP_l):
        sl = c_terukur*FP_l
        return sl
    #fungsi y topi
    def y_pred(x,slope,intercept):
        y = intercept+(slope*x)
        return y


    st.title('Perhitungan Spektrofotometri')
    st.markdown("---")

    df_d = None
    df_s = None
    # masukin abs dan cons
    st.subheader('Input Deret')
    col1,col2 = st.columns([2,2])
    with col1:
        data_x = st.text_input("Masukkan Deret Konsentrasi (Pisahkan dengan (/)):")
    with col2:
        data_y = st.text_input("Masukkan Deret Absorbansi (Pisahkan dengan (/)):")

    valid_input = True
    # Cek apakah input kosong atau tidak
    if data_x.strip() and data_y.strip():
        try:
            data_x = list(map(float, data_x.split('/')))
            data_y = list(map(float, data_y.split('/')))
            if not all(isinstance(i, (int, float)) for i in data_x) or not all(isinstance(i, (int, float)) for i in data_y):
                valid_input = False
        except ValueError:
            # st.write('Tolong Masukkan dengan format yang benar! Input harus Angka dan dipisahkan dengan koma (,) bukan titik (.)')
            valid_input = False
    else:
        data_x = []
        data_y = []

    if valid_input:
        data = {'Konsentrasi': data_x, 'Absorbansi': data_y}
        df_d = pd.DataFrame(data)


    if df_d is None:
        st.write('Error:Tolong Masukkan dengan format yang benar! Input harus Angka dan dipisahkan dengan koma (,) bukan titik (.)')

    st.markdown("---")


    st.subheader('Input Sample')
    # masukkan jumlah sampel
    col3,col4 = st.columns([3,2])

    with col3:
        data_s = st.text_input("Masukkan Absorbansi dari sampel (pisahkan dengan koma): ")

    validd_input = True
    if data_s.strip():
        try:
            data_s = list(map(float, data_s.split(',')))
            if not all(isinstance(i, (int, float)) for i in data_s):
                validd_input = False
        except ValueError:
            # print('Tolong Masukkan dengan format yang benar! Input harus Angka dan dipisahkan dengan koma (,) bukan titik (.)')
            validd_input = False
        
    else:
        data_s = []

    if validd_input:
        data = {'Absorbansi Sample': data_s}
        df_s = pd.DataFrame(data)

    if df_s is None:
        st.write('Error:Tolong Masukkan dengan format yang benar! Input harus Angka dan dipisahkan dengan koma (,) bukan titik (.)')

    #mengambil nilai dari dataframe
    if df_d is not None:
        X = df_d.iloc[:,0]
        y = df_d.iloc[:,1]
    elif df_d is None:
        X = None
        y = None

    if df_s is not None:
        abs  = df_s.iloc[:,0]
        abs = abs.astype(float)

    with col4:
        sampel_type = st.selectbox('Pilih Tipe Sampel',('Pilih Tipenya','Liquid','Solid'))

    intercept = None
    slope = None
    r_value = None
    y_topi = None
    #Menggunakan nested if karena variabel tersebut harus diisi terlebih dahulu oleh pengguna, kalo pake cara biasa error jir
    if X is not None and y is not None:
        if not X.empty and not y.empty:
            #Linear Regression
            linreg = scipy.stats.linregress(X, y)
            r_value = linreg.rvalue
            slope = linreg.slope
            intercept = linreg.intercept
            #Mencari y_topi
            if slope is not None and intercept is not None:
                x = df_d['Konsentrasi']
                y_topi = y_pred(x, slope, intercept)
                df_d['y pred / y topi'] = y_topi

            #Mengubah abs sampel menjadi c terukur
            for i in range(len(df_s['Absorbansi Sample'])):
                abs  = df_s.iloc[i,0]
                cTerukur = c_terukur(abs, slope, intercept)
                df_s.loc[i, 'Konsentrasi Terukur (mg/Kg)'] = round(cTerukur, 2)
            if 'Konsentrasi Terukur (mg/Kg)' in df_s.columns:
                c_terukur = df_s['Konsentrasi Terukur (mg/Kg)']
            else:
                print("Konsentrasi Terukur tidak ada ")

            #menghitung konsentrasi sampel
            if sampel_type == 'Solid': 
                col5,col6,col7 = st.columns([2,2,2])
                with col5:
                    FP = st.number_input('Masukkan FP:',min_value=1,value=1,step=1)
                with col6:
                    v_lt = st.number_input('Masukkan volume Labu Takar(mL):')
                with col7:
                    bobot_S = st.number_input('Masukkan Bobot Sample(gram):',step=0.0001,format="%.4f")
                cons = sample_S(c_terukur, v_lt, FP, bobot_S)
                df_s['Konsentrasi Sebenarnya'] = cons
            elif sampel_type == "Liquid":
                col8,col9 = st.columns([2,2])
                with col8:
                    FP_l = st.number_input('Masukkan FP:',min_value=1,value=1,step=1)
                cons = sampel_L(c_terukur, FP_l)
                df_s['Konsentrasi Sebenarnya'] = cons
            else:
                st.write('Tolong masukkan jenis sampel dengan benar!')
            
    st.markdown("---")


    tab1,tab2,tab3 = st.tabs(['Hasil Deret','Hasil Sampel','Kurva Linearitas dan Kalibrasi'])

    with tab1:
        if df_d is not None:
            df_d = df_d.applymap(lambda x: '{0:.2f}'.format(x) if isinstance(x, (int, float)) else x)
            st.markdown(df_d.style.hide(axis="index").to_html(), unsafe_allow_html=True)


        
        if intercept is not None and slope is not None and r_value is not None:
            col0,col10 = st.columns(2)
            with col0:
                st.text(f'Intercept = {intercept}')
                st.text(f'Slope = {slope}')
                st.text(f'r = {r_value}')
    with tab2:
        if df_s is not None:
            df_s = df_s.applymap(lambda x: '{0:.4f}'.format(x) if isinstance(x, (int, float)) else x)
            st.markdown(df_s.style.hide(axis="index").to_html(), unsafe_allow_html=True)
    with tab3:
        if y_topi is not None:
            #Print Kurva linear regresi dan kalibrasi
            fig = plt.figure(figsize=(10,10))
            plt.plot(X,y , color ='black' , label = "Linearitas")
            plt.plot(X,y_topi,color = 'red', label = "Kalibrasi")
            plt.title('Kurva Linearitas dan Kalibrasi')
            plt.ylabel('Absorbansi')
            plt.xlabel('Konsentrasi')
            plt.legend()

            st.pyplot(fig)



if choice == 'Internal Standard':


    st.title('Internal Standard')
    st.markdown('------')
    
    def calc_IRF(Ais_irf,Cis_irf,As_irf,Cs_irf):
        IRF = (Ais_irf*Cs_irf)/(Cis_irf*As_irf)
        return IRF

    def calc_Cs(Cis_c,As_c,Ais_c,IRF):
        Cs = (Cis_c*As_c*IRF)/Ais_c
        return Cs

    col1,col2 = st.columns([2,2])

    A_is = None
    C_is = None
    A_s = None
    C_s = None

    C_C_is = None
    A_sample = None
    A_C_is = None


    with col1:
        st.subheader('Input mencari IRF')

        # ask user for data pair 
        IRF_is = st.text_input('Masukkan Konsentrasi dan Area dari Internal Standard (Pisahkan dengan (/))')
        if IRF_is != '':
            try:
                C_is, A_is = IRF_is.split("/")  # split the pair into two values
                C_is = float(C_is.strip())  # remove any whitespace and convert to float
                A_is = float(A_is.strip())  # remove any whitespace and convert to float
            except ValueError:
                st.write("Input tidak valid, silakan coba lagi.")

        # ask user for data pair 
        IRF_s  = st.text_input('Konsentrasi dan Area dari Analyte (Pisahkan dengan (/))')

        if IRF_s != '':
            try:
                C_s, A_s = IRF_s.split("/")  # split the pair into two values
                C_s = float(C_s.strip())  # remove any whitespace and convert to float
                A_s = float(A_s.strip())  # remove any whitespace and convert to float
            except ValueError:
                st.write("Input tidak valid, silakan coba lagi.")


    with col2:
        st.subheader('Input mencari konsentrasi ')

        pair = st.text_input('Masukkan Konsentrasi dan Area dari Internal Standard Sample (Pisahkan dengan (/))')

        if pair != '':
            try:
                # pair = st.text_input('Masukkan Konsentrasi dan Area dari Internal Standard Sample (Pisahkan dengan (/))')
                C_C_is, A_C_is = pair.split("/")  # split the pair into two values
                C_C_is = float(C_C_is.strip())  # remove any whitespace and convert to float
                A_C_is= float(A_C_is.strip())  # remove any whitespace and convert to float
            except ValueError:
                st.write("Input tidak valid, silakan coba lagi.")

        try:
            A_sample = st.number_input('Masukkan Area dari Sample:',format="%.4f")
        except ValueError:
            st.write("Input tidak valid, silakan coba lagi.")

        
    st.markdown('------')
    st.subheader('Hasil:')

    if A_is is not None and C_is is not None and A_s is not None and C_s is not None and C_C_is is not None and A_sample is not None and A_C_is is not None:

        with st.container():

            IRF = calc_IRF(A_is,C_is,A_s,C_s)

            if IRF is not None and isinstance(IRF, float):
                IRF = round(IRF,4)
                IRFs = str(IRF)
                st.write('IRF=',IRFs)
            else:
                st.write("IRF tidak dapat dihitung.")

            with st.expander("Buka Rumus"):
                Ais_sy, Cs_sy, Cis_sy, As_sy , IRF_sy= symbols('Ais Cs Cis As IRF')
                equation = Eq(IRF_sy,Ais_sy * Cs_sy / (Cis_sy * As_sy))
                st.latex(latex(equation))


            st.markdown('------')

            C_sample = calc_Cs(C_C_is,A_sample,A_C_is,IRF)

            if C_sample is not None and isinstance(C_sample, float):
                C_sample = round(C_sample,2)       
                C_samples = str(C_sample)
                st.write('Konsentrasi Sample = ',C_samples)
            else:
                st.write("Konsentrasi Sample tidak dapat dihitung.")
            
            with st.expander("Buka Rumus"):
                Ais, Cs, Cis, As , IRF= symbols('Ais Cs Cis As IRF')
                equation = Eq(Cs,(Cis * As * IRF )/Ais)
                st.latex(latex(equation))


# if choice == "Standard Adisi":
