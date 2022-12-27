from Interface import GUI
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd

command=GUI()

link='https://www.guiamais.com.br/'

link_base='https://www.guiamais.com.br'


def Main(link):

    command.Limpar()

    dados={

        'Segmento':'',

        'Cidade':''
    }

    for r in dados.keys():

        res=''

        while res=='':

            res=input(f'Informe o {r}: ').title()

            pass

        dados[r]=res

        pass

    pesquisa=dados['Segmento']

    cidade=dados['Cidade']

    print('Por favor não mexer até que o processo esteja finalizado!')

    service=Service(ChromeDriverManager().install())

    opcao=webdriver.ChromeOptions()

    opcao.add_argument('--headless')

    driver=webdriver.Chrome(service=service)

    driver.maximize_window()

    driver.get(link)

    contagem=0

    while contagem==0:

        contagem=driver.find_elements(By.ID,'what')
        time.sleep(1)

        pass

    campo=driver.find_element(By.ID,'what')
    campo.send_keys(pesquisa)
    time.sleep(1)

    contagem=0

    while contagem==0:

        contagem=driver.find_elements(By.ID,'where')
        time.sleep(1)

        pass

    campo=driver.find_element(By.ID,'where')
    campo.click()
    time.sleep(1)
    campo.send_keys(Keys.DELETE)
    time.sleep(1)
    campo.send_keys(cidade)
    time.sleep(1)

    contagem=0

    while contagem==0:

        contagem=driver.find_elements(By.CLASS_NAME,'searchButton')
        time.sleep(1)

        pass

    botao=driver.find_element(By.CLASS_NAME,'searchButton')
    botao.click()

    time.sleep(2)

    page_content=driver.page_source

    site=BeautifulSoup(page_content,'html.parser')
    
    paginas=site.find('nav',attrs={'class':'pagination'}).findAll('a')

    link_pag=str(paginas[1].get('href'))

    cont=len(link_pag)-1
    
    link_pag=link_pag[:cont]

    cont=0

    temp=[]

    while True:

        cont+=1

        contagem=len(driver.find_elements(By.CLASS_NAME,'nextPage'))

        botao=driver.find_element(By.CLASS_NAME,'nextPage')

        link=(f'{link_pag}{cont}')

        driver.switch_to.window(driver.window_handles[-1])
 
        page_content=driver.page_source

        site=BeautifulSoup(page_content,'html.parser')

        tags=site.find_all('h2',attrs={'class':'aTitle'})

        print(tags)

        botao.click()

        if(contagem==0):

            break
        

        break

        pass
   

    pass

def ExtrairDados(*args):

    df=pd.DataFrame()

    for i,link in enumerate(args[-1]):
 
        if(i==0):

            service=Service(ChromeDriverManager().install())

            opcao=webdriver.ChromeOptions()

            opcao.add_argument('--headless')

            driver=webdriver.Chrome(service=service)

            driver.maximize_window()

            driver.get(link)            

            pass

        else:

            driver.execute_script('window.open("");')
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(link)

            pass
        
        page_content=driver.page_source

        site=BeautifulSoup(page_content,'html.parser')

        tag_phone=[]

        cont=0

        while len(tag_phone)==0:

            tag_phone=driver.find_elements(By.CLASS_NAME,'advPhone')
            time.sleep(1)

            cont+=1

            if(cont>=1):

                break

            pass

        tag_end=[]

        cont=0

        while len(tag_end)==0:

            tag_end=driver.find_elements(By.CLASS_NAME,'advAddress')
            time.sleep(1)

            cont+=1

            if(cont>=1):

                break

            pass

        if(len(tag_phone)>=1 and len(tag_end)>=1):

            try:

                telefones=site.find('ul',attrs={'class':'advPhone'}).findAll('li')

                lista_tel=[str(telefone.get_text()).strip() for telefone in telefones]

                enderecos=site.find('address',attrs={'class':'advAddress'})
                    
                endereco=str(enderecos.find('span',attrs={'class':'tp-address'}).get_text()).split()

                endereco=' '.join([c for c in endereco])

                cidade=enderecos.find('span',attrs={'class':'tp-city'}).get_text().strip()

                estado=enderecos.find('span',attrs={'class':'tp-state'}).get_text().strip()

                cep=enderecos.find('span',attrs={'class':'tp-postalCode'}).get_text().strip()

                cep=cep if cep!='' else ''

                empresa=site.find('h1',attrs={'class':'tp-companyName'}).get_text().strip().upper()

                categoria=site.find('a',attrs={'class':'tp-category'}).get_text().strip().upper()

                logradouro=(f'{endereco} {cidade}, {estado} - CEP: {cep}').upper()

                row_end=[]

                row_tel=[]

                row_emp=[]

                row_linha=[]

                row_categ=[]
                    
                for i,tel in enumerate(lista_tel):

                    i+=1

                    row_emp.append(empresa)

                    row_end.append(logradouro)

                    row_tel.append(tel)

                    row_linha.append(i)

                    row_categ.append(categoria)

                    pass

                temp_dict={

                    'Empresa':row_emp,
                    'Categoria':row_categ,
                    'Endereço':row_end,
                    'Telefone':row_tel,
                    'Seq':row_linha

                }

                temp_df=pd.DataFrame(data=temp_dict)

                temp_df=temp_df.pivot(index=['Empresa','Categoria','Endereço'],columns='Seq',values='Telefone').reset_index()

                indice=[c for c in temp_df.columns if str(c).isnumeric()]

                col=[f'Telefone {c}' for c in temp_df.columns if str(c).isnumeric()]

                for i,c in enumerate(indice):

                    temp_df.rename(columns={c:col[i]},inplace=True)
                    
                    pass

                df=pd.concat([df,temp_df],axis=0,ignore_index=True)
                
                pass

            except:

                continue

            pass

        pass

    return df

    pass

if __name__=='__main__':
    
    Main(link)
    
    pass