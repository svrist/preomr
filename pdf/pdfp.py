

def pdf_pages(filename):
    from pyPdf import PdfFileReader
    input = PdfFileReader(file(filename,"rb"))

    print "%d pages in %s."%(input.getNumPages(),filename)



