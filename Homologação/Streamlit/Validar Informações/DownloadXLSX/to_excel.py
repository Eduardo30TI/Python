import streamlit as st
import pandas as pd
from io import BytesIO


class ExcelDW:

    def DownloadXLSX(excel):

        output=BytesIO()
        with pd.ExcelWriter(output,engine='xlsxwriter') as writer:  
            excel.to_excel(writer,index=False)

            pass

        return output.getvalue()

        pass

    pass
    