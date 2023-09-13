import win32com.client as win32

class Email:

   
    def EnviarEmail(corpo,assunto,**kwargs):

        olApp = win32.Dispatch('Outlook.Application')
        olNS = olApp.GetNameSpace('MAPI')

        temp=dict()

        for key,word in kwargs['kwargs'].items():

            temp[key]=word

            pass        

        email_to=temp['To']

        email_cc=temp['CC']

        anexo=temp['Anexo']

        # construct email item object
        mailItem = olApp.CreateItem(0)
        mailItem.Subject = assunto
        mailItem.BodyFormat = 1
        #mailItem.Body = 'Teste'
        mailItem.HTMLBody=corpo
        mailItem.To = ';'.join(str(env).lower() for env in email_to)
        mailItem.Cc=';'.join(str(env).lower() for env in email_cc)
        mailItem.Sensitivity  = 2

        for arq in anexo:

            mailItem.Attachments.Add(arq)

            pass
        
        mailItem.Display()
        #mailItem.Send()

        pass

    pass