from win32com import client
import time

ie = client.Dispatch("InternetExplorer.Application")


def printPDFDocument(filename):

    ie.Navigate(filename)

    if ie.Busy:
        time.sleep(1)

    ie.Document.printAll()
    time.sleep(2)


ie.Quit()

printPDFDocument("facture_a4.pdf")
