import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

senha='nmfkstwduzpyvipm'

class Mail:

    def Enviar(self,assunto: str,mensagem: str,info: dict):

        msg=MIMEMultipart()
        msg['Subject']=assunto
        msg['From']='netfeira2@gmail.com'

        for c in ['To','CC']:
        
            for t in info[c]:
            
                msg[c]=t

                pass

            pass

        for c in ['Anexo']:

            for a in info[c]:

                arq_name=os.path.basename(a)

                with open(a,'rb') as file:
                    
                    att=MIMEBase('application','octet-stream')
                    att.set_payload(file.read())
                    encoders.encode_base64(att)
                    
                    att.add_header('Content-Disposition',f'attachment; filename={arq_name}')

                    pass

                msg.attach(att)

                pass

            pass
        
        msg.attach(MIMEText(mensagem,'html'))

        #login na conta
        s=smtplib.SMTP('smtp.gmail.com:587')
        s.starttls()
        
        s.login(msg['From'],senha)
        s.sendmail(msg['From'],[msg['To'],msg['CC']],msg.as_string().encode('UTF-8'))

        pass


    pass