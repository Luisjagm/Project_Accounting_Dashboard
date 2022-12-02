
#-------------------------------------------------
#--- COLORES ---
#47669B
#B4BF1D
#2A3864
#6F6EFF
#698DF5

#--------------------------------------------------
#--- IMPORTS ---
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import numpy as np
import seaborn as sns
from datetime import date, time, datetime, timedelta
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid,AgGridTheme,GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

st.set_page_config(layout='wide', initial_sidebar_state='expanded')
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
#-------------------------------------------------
#--- LECTURA DE DATOS ---
trans=pd.read_csv('./data/Transaction_Final.csv')
cus=pd.read_csv('./data/CUSTOMERMASTER_NEW.csv',delimiter=',')
temp=pd.read_csv('./data/TEMPXMLFILEDATA.csv',delimiter=',')
merge=pd.read_csv('./data/mergefinal.csv')
merge=merge[merge['CUSTOMERID']==2]
cliente2=temp[temp['CUSTOMERID']==2]
cliente2['Fecha']=pd.to_datetime(cliente2['DATE'], format='%m/%d/%Y')
cliente2=cliente2.sort_values(by = 'Fecha', ascending = True)

#--------------------------------------------------
#--- DESARROLLO DEL MENÚ ---
selected = option_menu(
    menu_title=None,
    options=['Facturas','Impuestos','Modelos'],
    icons=['receipt-cutoff','cash-stack','box'],
    default_index=0,
    orientation='horizontal',
    styles={
        "container":{"padding":"0!important"},
        "icon": {"color": "#22AA33", "font-size": "25px"},
        "nav-link-selected": {"background-color": "#47669B"}
    }
)

if selected == 'Facturas':
    #--------------------------------------------------
    #--- SIDEBAR CONFIG ---
    st.sidebar.header('Dashboard `FACTURAS`')
    st.sidebar.subheader('FILTROS')
    merge['Fecha']=pd.to_datetime(merge['DATE']).dt.normalize()
    merge=merge.sort_values(by = 'Fecha', ascending = True)
    sidecol1,sidecol2=st.sidebar.columns(2)
    fecha_Fact1= sidecol1.text_input('Fecha inicial',value='2020-01-01')
    fecha_Fact2= sidecol2.text_input('Fecha final',value='2021-12-30')
    merge2= merge.loc[(merge['Fecha'] >=fecha_Fact1) & (merge['Fecha'] <= fecha_Fact2)]
    merge_pastel= merge.loc[(merge['Fecha'] >=fecha_Fact1) & (merge['Fecha'] <= fecha_Fact2)]

    
    # --- CONTENEDORES ---
    Mega_Tabla=st.container()
    Columna_Principal1,Columna_Principal2=st.columns(2)
    Graficos_de_mientras=st.container()
    ultimo=st.container()

    with Columna_Principal1:
        Graficas_Facturas =st.container()
        Facturas_por_pagar =st.container()
        with Graficas_Facturas:
            Barras, Cascada=st.tabs(['Barras','Cascada'])
            #with Pastel:
                #pastel=px.sunburst(merge2, values='RECIEVEDBY', 
                #path=['RECEIVEDBY','INVOICETYPE', 'ISPAYMENTPENDING'],
                #color='TOTALAFTERTAX',
                #color_continuous_scale=['#698DF5','#2A3864','#22AA33']) #hover_name='Fecha')
                #st.markdown("<h5 style= 'text-align: center;color:#47669B ;'>Pendiente de Pago</h5>", unsafe_allow_html=True)
                #st.write(pastel)
            with Barras:
                lista1=[]
                lista2=[]
                lista1.append((merge2['INVOICETYPE'].value_counts())[0])
                lista2.append((merge2['INVOICETYPE'].value_counts()).index[0])
                lista1.append((merge2['INVOICETYPE'].value_counts())[1])
                lista2.append((merge2['INVOICETYPE'].value_counts()).index[1])
                print(lista2)
                print(lista1)
                barra=pd.DataFrame()
                barra['Factura']=lista2
                barra['Total']=lista1
                fig=px.bar(barra,x='Factura',y='Total',color='Total',color_continuous_scale=['#22AA33','#6F6EFF','#2A3864'])
                fig.update_layout(title='Total Facturas')
                st.write(fig)
            with Cascada:
                valores=[merge2['TOTALBEFORTAX'].sum(),-(merge2['INCOMETAXAMT'].sum()),-(merge2['VATAMOUNT'].sum()),
                merge2['VATAMT'].sum(),merge2['TOTALAFTERTAX'].sum()]
                
                Casc=go.Figure(go.Waterfall(
                    measure = ["relative", "relative", "relative", "relative", "total"],
                    x=['TOTALBEFORTAX','INCOMETAXAMOUNT','VATAMOUNT','VATAMT','TOTALAFTERTAX'],
                    y=valores,
                    connector={"line":{"color":"rgb(63,63,63)"}},
                    decreasing={"marker":{"color":'#22AA33'}},
                    increasing={"marker":{"color":'#2A3864'}},
                    totals={"marker":{"color":"#698DF5"}}
                ))
                Casc.update_layout(
                    title='Antes y Después de Impuestos'
                )
                st.write(Casc)
        with Facturas_por_pagar:
            st.markdown("<h5 style= 'text-align: center;color:#47669B ;'>Facturas sin pagar</h5>", unsafe_allow_html=True)
            merge_tabla=pd.read_csv('./data/mergefinal.csv')
            merge_tabla['Fecha']=pd.to_datetime(merge_tabla['DATE']).dt.normalize()
            merge_tabla=merge_tabla.sort_values(by = 'Fecha', ascending = True)
            merge_tabla= merge_tabla.loc[(merge_tabla['Fecha'] >=fecha_Fact1) & (merge_tabla['Fecha'] <= fecha_Fact2)]
            #--- PPD ---
            merge_cliente=merge_tabla[merge_tabla['CUSTOMERID']==64]
            merge_NoPue=merge_cliente.loc[(merge_cliente['PAYMETHODCODE']!='PUE') & (merge_cliente['PAYMETHODCODE']!='0')]
            merge_NoPue=merge_NoPue.loc[(merge_NoPue['INVOICETYPE']!='P') & (merge_NoPue['INVOICETYPE']!='p') & (merge_NoPue['INVOICETYPE']!='pago')]
            Fact_No_Pagada=merge_NoPue['INVOICETYPE'].value_counts().sum()
            #-----------
            #--- PUE ---
            merge_Factpag=merge_cliente.loc[(merge_cliente['PAYMETHODCODE']=='PUE')]
            #--- PPD y 'P','p','pago'
            merge_PPD=merge_cliente.loc[(merge_cliente['PAYMETHODCODE']!='PUE') & (merge_cliente['PAYMETHODCODE']!='0')]
            merge_PPD=merge_PPD.loc[(merge_PPD['INVOICETYPE']=='P') & (merge_PPD['INVOICETYPE']=='p') & (merge_PPD['INVOICETYPE']=='pago')]
            Fact_Pagada=merge_Factpag['INVOICETYPE'].value_counts().sum()
            Fact_Pagada += merge_PPD['INVOICETYPE'].value_counts().sum()

            gb = GridOptionsBuilder.from_dataframe(merge_NoPue)
            gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
            gb.configure_side_bar() #Add a sidebar
            gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
            gridOptions = gb.build()

            grid_response = AgGrid(
                merge_NoPue,
                gridOptions=gridOptions,
                data_return_mode='AS_INPUT', 
                update_mode='MODEL_CHANGED', 
                fit_columns_on_grid_load=False,
                #THEMES: 'alpine', 'balham', 'material', 'streamlit'
                theme='material', #Add theme color to the table
                enable_enterprise_modules=True,
                height=425, 
                width='100%',
                reload_data=True
            )
            data = grid_response['data']
            selected = grid_response['selected_rows'] 
            df = pd.DataFrame(selected) #Pass the selected rows to a new dataframe df
    with Columna_Principal2:
        top_clientes=st.container()
        Perc_Fact=st.container()
        with top_clientes:
            top_cl=st.sidebar.slider("Top # Clients ",min_value=2,max_value=10,value=5)
            Prueba=merge2['RECEIVEDBY'].value_counts()
            cl=[]
            for i in range(top_cl):
                cl.append(Prueba[i])
            Clientes=merge2['RECEIVEDBY'].value_counts().index
            Facturas=merge2['RECEIVEDBY'].value_counts().values
            Top_clientes=pd.DataFrame()
            Top_clientes['Cliente']=Prueba.index[:top_cl]
            Top_clientes['#Facturas']=cl
            #Top_clientes['#Facturas']=Top_clientes['#Facturas'].sort_values(ascending=False)
            Top_clientes=Top_clientes.sort_values('#Facturas',ascending=True)
            fig2=px.bar(Top_clientes,x='#Facturas',y='Cliente',color='#Facturas',color_continuous_scale=['#698DF5','#2A3864','#22AA33'])
            fig2.update_layout(margin=dict(l=5,r=5,b=10,t=10))
            fig2.update(layout_coloraxis_showscale=False)
            st.markdown("<h4 style= 'text-align: center;color: #47669B;'>Top Clientes</h4>", unsafe_allow_html=True)
            st.write(fig2)
        with Perc_Fact:
            st.markdown("<h5 style= 'text-align:center ;color:#47669B ;'>Porcentaje de Facturas Pagadas</h5>", unsafe_allow_html=True)
            merge=pd.read_csv('./data/mergefinal.csv')
            merge9=merge[merge['CUSTOMERID']==64]
            merge9['Fecha']=pd.to_datetime(merge9['DATE']).dt.normalize()
            merge9=merge9.sort_values(by = 'Fecha', ascending = True)
            merge9= merge9.loc[(merge9['Fecha'] >=fecha_Fact1) & (merge9['Fecha'] <= fecha_Fact2)]
            merge3=merge9.loc[(merge9['PAYMETHODCODE']!='PUE') & (merge9['PAYMETHODCODE']!='0')]
            merge3=merge3.loc[(merge3['INVOICETYPE']!='P') & (merge3['INVOICETYPE']!='p') & (merge3['INVOICETYPE']!='pago')]
            Fact_No_Pagada=merge3['INVOICETYPE'].value_counts().sum()
            merge4=merge9.loc[(merge9['PAYMETHODCODE']=='PUE')] #& (merge2['PAYMETHODCODE']!='0')]
            #merge5=merge9.loc[(merge9['PAYMETHODCODE']!='PUE') & (merge9['PAYMETHODCODE']!='0')]
            #merge5=merge5.loc[(merge5['INVOICETYPE']=='P') & (merge5['INVOICETYPE']=='p') & (merge5['INVOICETYPE']=='pago')]
            Fact_Pagada=merge4['INVOICETYPE'].value_counts().sum()
            #Fact_Pagada += merge5['INVOICETYPE'].value_counts().sum()
            labels=['Pagada','No Pagada']
            values=[Fact_Pagada,Fact_No_Pagada]
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5,pull=[0,.1])])
            fig.update_layout(margin=dict(l=40,r=40,b=40,t=40))
            fig.update_traces(marker=dict(colors=['#2A3864','#22AA33']))
            st.write(fig)
    with Mega_Tabla:
        st.markdown('---')
        st.markdown("<h2 style= 'text-align:center ;color:#47669B ;'>Tabla Interactiva Facturas</h2>", unsafe_allow_html=True)
        merge3=merge2.drop(['Unnamed: 0', 'CUSTOMERID',
       'CURRENCYID', 'REGIME', 'XMLCOUNT', 'USERSTATUS',
       'AMOUNTPAID', 'ISPAYMENTPENDING', 'INVOICETYPE_INITIAL',
       'PAYMETHODCODE', 'INVOICETYPE_INITIAL_ORIGINAL', 'XMLIEPSTAX',
       'XMLCURRENCY','CREATEDBY_USER'],axis=1)
        gb = GridOptionsBuilder.from_dataframe(merge3)
        gb.configure_pagination(paginationAutoPageSize=True) #Add pagination
        gb.configure_side_bar() #Add a sidebar
        gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
        gridOptions = gb.build()

        grid_response = AgGrid(
            merge3,
            gridOptions=gridOptions,
            data_return_mode='AS_INPUT', 
            update_mode='MODEL_CHANGED', 
            fit_columns_on_grid_load=False,
            #THEMES: 'alpine', 'balham', 'material', 'streamlit'
            theme='material', #Add theme color to the table
            enable_enterprise_modules=True,
            height=400, 
            width='110%',
            reload_data=True
        )
        data = grid_response['data']
        selected = grid_response['selected_rows'] 
        df = pd.DataFrame(selected) #Pass the selected rows to a new dataframe df

if selected == 'Impuestos':
    #--------------------------------------------------
    #--- SIDEBAR CONFIG ---
    st.sidebar.header('Dashboard `IMPUESTOS`')
    st.sidebar.subheader('Columnas de la tabla')
    visst=st.sidebar.multiselect('Variables para Gráfica de Tiempo',['VATAMT','INCOMETAXAMT','TOTALTAX'],['VATAMT','INCOMETAXAMT','TOTALTAX'])
    st.sidebar.markdown('''
    ---
    Created By IMPORTEC
    ''')
    #-------------------------------------------------
    #--- CONTENEDORES ---
    header= st.container()
    Grafica_Serie_Tiempo= st.container()
    #--------------------------------------------------------------------------
    #--- IBRERÍA OPERATOR PARA CONVERTIR STRING A OPERADORES ---
    import operator
    ops = { 
        "<" : operator.lt,
        ">" : operator.gt,
        "<=" : operator.le,
        ">=" : operator.gt
    }
    #-------------------------------------------------
    #--- FUNCIONES ---
    resultados=[]
    def promedio2(selec):
        if selec == 'Promedio':
            resultados.append(round(cliente3['VATAMT'].mean(),3))
            resultados.append(round(cliente3['INCOMETAXAMT'].mean(),3))
            resultados.append(round(cliente3['TOTALTAX'].mean(),3))
        if selec == 'Total':
            resultados.append(round(cliente3['VATAMT'].sum(),3))
            resultados.append(round(cliente3['INCOMETAXAMT'].sum(),3))
            resultados.append(round(cliente3['TOTALTAX'].sum(),3))
        if selec == 'Cuenta':
            resultados.append(round(cliente3['VATAMT'].count(),3))
            resultados.append(round(cliente3['INCOMETAXAMT'].count(),3))
            resultados.append(round(cliente3['TOTALTAX'].count(),3))
    
    #--- PORCENTAJE DE INCREMENTOS ---
    cliente2['TOTALTAX']=cliente2['TOTALAFTERTAX']-cliente2['TOTALBEFORTAX']
    intervalos=['Jan-Feb','Feb-Mar','Mar-Apr','Apr-May','May-June','June-July','July-Ago','Ago-Sep','Sep-Oct','Oct-Nov','Nov-Dic']
    years=[2014,2015,2016,2017,2018,2019,2020,2021,2022]
    meses=[1,2,3,4,5,6,7,8,9,10,11,12]

    for año in years:
        for mes in meses:
            exec(f'Incremento{año}_{año+1}= []') #Crear listas de incrementos de 1 mes a lo largo de los años
            exec(f'Incremento{año}= []') #Crear listas de incrementos

    for año in years:
        exec(f'Tax_{año} = cliente2[cliente2["Fecha"].dt.year==año]')
        for mes in meses:
            exec(f'Tax_{año}_{mes} = Tax_{año}[Tax_{año}["Fecha"].dt.month == mes]')
            exec(f'TotalTax_{año}_{mes}=Tax_{año}_{mes}["TOTALTAX"].sum()')
        for mes in meses:
            if mes != meses[-1]:
                exec(f'Incremento{año}.append(round(((TotalTax_{año}_{mes+1}-TotalTax_{año}_{mes})/TotalTax_{año}_{mes})*100,2))')
        #if año != years[-1]:
    #INCREMENTOS MES EN DIFERENTES AÑOS
            #exec(f'Incremento{año}_{año+1}.append(round(((TotalTax_{año+1}_{mes}-TotalTax_{año}_{mes})/TotalTax_{año}_{mes})*100,2))')
    #INCREMENTOS EN UN AÑO
    #FORMULA DE PORCENTAJE DE AUMENTO : (incremento/original)*100
    incrementos=pd.DataFrame()
    incrementos['intervalos']=intervalos
    incrementos['2014']=Incremento2014
    incrementos['2015']=Incremento2015
    incrementos['2016']=Incremento2016
    incrementos['2017']=Incremento2017
    incrementos['2018']=Incremento2018
    incrementos['2019']=Incremento2019
    incrementos['2020']=Incremento2020
    incrementos['2021']=Incremento2021


    #--------------------------------------------------------------------------
    #--- GRÁFICA DE IMPUESTOS EN SERIE DE TIEMPO ---
    with Grafica_Serie_Tiempo:
        Todos, IVA, ISR = st.tabs(["Todos", "IVA", "ISR"])
        cliente2=temp[temp['CUSTOMERID']==2]
        cliente2['Fecha']=pd.to_datetime(cliente2['DATE'], format='%m/%d/%Y')
        cliente2=cliente2.sort_values(by = 'Fecha', ascending = True)
        cliente2['TOTALTAX']=cliente2['TOTALAFTERTAX']-cliente2['TOTALBEFORTAX']

        with Todos:

            #st.header('TOTAL DE IMPUESTOS')

            #graph= st.selectbox('Tipo de Gráfico',('Línea','Barras','Histograma','Pastel'))
            colum1,colum2= st.columns([7,1])
            prueba=st.container()
            metricas=st.container()
            rengl_metricas=st.container()
            porcentaje_aumento=st.container()

            with metricas:
                c1,c2=st.columns([6,1])
                #c2.header('Filtros')
                c2.markdown("<h3 style= 'color: #47669B;'>Filtros</h3>", unsafe_allow_html=True)
                fecha1= c2.text_input('Fecha inicial',value='2020-01-01')
                fecha2= c2.text_input('Fecha final',value='2021-12-30')
                cliente3= cliente2.loc[(cliente2['Fecha'] >=fecha1) & (cliente2['Fecha'] <= fecha2)]
                fig3 = go.Figure()
                colores=['#22AA33','#2A3864','#6F6EFF']
                for i in range(len(visst)):
                    fig3.add_trace(go.Scatter(x=cliente3['Fecha'], y=cliente3[visst[i]], name=visst[i], line=dict(color=colores[i], width=1.3)))
                c1.markdown("<h4 style= 'color:#47669B ;'>Serie de Tiempo Impuestos</h4>", unsafe_allow_html=True)
                fig3.update_traces(hovertemplate=None)
                fig3.update_layout(hovermode="x unified")
                c1.write(fig3)
                c2.markdown("<h4 style= 'color:#47669B ;'>Métricas</h4>", unsafe_allow_html=True)
                selec=c2.selectbox('Selección',('Total','Promedio','Cuenta'))
            with rengl_metricas:
                c1,c2,c3,c4,c5,c6=st.columns([1,3,3,3,1,1])
                promedio2(selec)
                c2.metric("IVA",resultados[0],"1.2")
                c3.metric("ISR",resultados[1],"3.5")
                c4.metric("TOTALTAX",resultados[2],"9.4")
            with porcentaje_aumento:
                c1,c2,c3=st.columns([6,3,1])
                sel_año=c3.selectbox('Año',('2018','2019','2020','2021'))
                fig = px.bar(incrementos, x='intervalos', y=sel_año,text_auto='.2s',color=sel_año,
                color_continuous_scale=['#22AA33','#6F6EFF','#2A3864'],
                hover_name='intervalos',hover_data={'intervalos':False})
                c1.markdown("<h4 style= 'text-align: center ;color: #47669B;'>Porcentaje de Incremento total de Impuestos</h4>", unsafe_allow_html=True)
                c1.write(fig)
                #--- PIE CHART ---
                df=pd.DataFrame()
                valores=[]
                tipo=['IVA','ISR']
                cliente2=cliente2[cliente2['Fecha'].dt.year==int(sel_año)]
                Iva=cliente2['VATAMT'].sum()
                Isr=cliente2['INCOMETAXAMT'].sum()
                valores.append(Iva)
                valores.append(Isr)
                df['TOTAL']=valores
                df['Impuesto']=tipo
                fig3=go.Figure(data=[go.Pie(labels=df['Impuesto'], values=df['TOTAL'], pull=[0,0.1],hole=.5,
                text=['IVA','ISR'],
                hovertemplate = "%{label}: <br><b>TOTAL:</b> %{value} </br> %{percent}")])
                fig3.update_layout(margin=dict(l=5,r=5,b=10,t=10))
                fig3.update_traces(marker=dict(colors=['#2A3864', '#22AA33']))
                c2.markdown("<h4 style= 'color: #47669B;'>Suma total de impuestos</h4>", unsafe_allow_html=True)
                c2.write(fig3)
                #fig2=px.pie(df,values='TOTAL',names='Impuesto',
                #hole=.5,
                #color_discrete_sequence=['#22AA33','#2A3864']
                #)
                #fig2.update_layout(margin=dict(l=5,r=5,b=10,t=10))
                #c2.write(fig2)
        with IVA:
            año=st.container()
            with año:
                col1,col2=st.columns([8,5])
                cliente2=temp[temp['CUSTOMERID']==2]
                cliente2['Fecha']=pd.to_datetime(cliente2['DATE'], format='%m/%d/%Y')
                cliente2=cliente2.sort_values(by = 'Fecha', ascending = True)
                sel_año2=col2.selectbox('Año',('2018','2019','2020','2021','2022'),key='IVA')
                cliente2=cliente2[cliente2['Fecha'].dt.year==int(sel_año2)]
                total=round(cliente2['VATAMT'].sum(),3)
                mees=['January','February','March','April','May','June','July','August','September','October','November','December']
                Iva=[]
                for i in range(len(mees)):
                    suma=cliente2[cliente2['Fecha'].dt.month==i+1]
                    Iva.append(suma['VATAMT'].sum())
                df1=pd.DataFrame()
                df1['Month']=mees
                df1['IVA']=Iva
                fig5=px.bar(df1,x='Month',y='IVA',color='IVA',color_continuous_scale=['#22AA33','#6F6EFF','#2A3864'])
                col1.write(fig5)

                #col2.markdown("<h2 style= 'color: #47669B;'>Total de IVA Pagado</h4>", unsafe_allow_html=True)
                col2.header('Total IVA pagado')
                col2.metric(sel_año2,total)

        with ISR:
            año=st.container()
            with año:
                col1,col2=st.columns([8,5])
                cliente2=temp[temp['CUSTOMERID']==2]
                cliente2['Fecha']=pd.to_datetime(cliente2['DATE'], format='%m/%d/%Y')
                cliente2=cliente2.sort_values(by = 'Fecha', ascending = True)
                sel_año2=col2.selectbox('Año',('2018','2019','2020','2021','2022'),key='ISR')
                cliente2=cliente2[cliente2['Fecha'].dt.year==int(sel_año2)]
                total=round(cliente2['INCOMETAXAMT'].sum(),3)
                mees=['January','February','March','April','May','June','July','August','September','October','November','December']
                Iva=[]
                for i in range(len(mees)):
                    suma=cliente2[cliente2['Fecha'].dt.month==i+1]
                    Iva.append(suma['INCOMETAXAMT'].sum())
                df1=pd.DataFrame()
                df1['Month']=mees
                df1['ISR']=Iva
                fig5=px.bar(df1,x='Month',y='ISR',color='ISR',color_continuous_scale=['#22AA33','#6F6EFF','#2A3864'])
                col1.write(fig5)

                col2.header('Total ISR pagado')
                col2.metric(sel_año2,total)

if selected == 'Modelos':
    #--------------------------------------------------
    #--- SIDEBAR CONFIG ---
    st.markdown("<h2 style= 'text-align: center;color:#47669B ;'>Facturas sin pagar</h2>", unsafe_allow_html=True)
    st.markdown("---")
    clientess=pd.read_csv('./data/CLIENTESIE2.csv')
    #id=st.selectbox('Selecciona tu cliente:',clientess['Company Name'].values)


    col1,col2=st.columns([6,8])
    with col1:
        #id=st.selectbox('Selecciona tu cliente:',clientess['Company Name'].values)
        st.markdown("<h4 style='text-align:center; color=#47669B';>¿Cómo definir el perfil del cliente?</h4>", unsafe_allow_html=True)
        st.markdown('''
        * Obtener ***ingresos*** y ***egresos*** del cliente.
        * De acuerdo al ***saldo generado***, se generan ***indicadores***.
        * Asignación del nivel de indicador según el ***saldo del cliente***.
        ---
        ''')
        id=st.selectbox('Selecciona tu cliente:',clientess['Company Name'].values)
        cliente=clientess[clientess['Company Name']==id]
        cat=cliente['Grupo'].value_counts().index
        st.markdown("*Se encuentra en Grupo de:*")
        if cat[0] == 'Libertad Financiera':
            st.markdown(f"## **{cat[0]}**")
            st.markdown('Abona más de lo que retira.')
        
        if cat[0] == 'Sustento Financiero':
            st.markdown(f"## **{cat[0]}**")
            st.markdown('Retira más de lo que abona.')

        if cat[0] == 'Sobrevivencia Financiera':
            st.markdown(f"## **{cat[0]}**")
            st.markdown('Retira más de lo que abona / Retira cantidades altas')

        if cat[0] == 'Abundancia Financiera':
            st.markdown(f"## **{cat[0]}**")
            st.markdown('Abona más de lo que retira.Abona grandes cantidades.')


    with col2:
        col2.markdown("<h3 style='text-align:center ; color=#47669B';>Agrupamiento de Clientes</h3>", unsafe_allow_html=True)
        fig2=px.scatter(clientess, y='EGRESOS', x='INGRESOS',hover_name='Company Name',
        color='Grupo',symbol="Grupo",color_discrete_sequence=['#2A3864','#698DF5','#22AA33','#47669B'])
        fig2.update_traces(marker_size=10)
        st.write(fig2)
