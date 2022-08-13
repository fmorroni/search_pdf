import PyPDF2
import search_pdf_module as spdf

def search_pdf_annots(filePaths, commands, searchTerm, searchTermRe, contextLength=30):
    for path in filePaths:
        try:
            data = PyPDF2.PdfFileReader(open(path, 'rb'), strict=False)
            foundMatch = False
        except:
            raise ValueError(f'File {path} not supported')

        for pageNumber, page in enumerate(data.pages):
            if '/Annots' in page.keys():
                for annotation in page['/Annots']:                    
                    if '/Contents' in annotation.getObject().keys():
                        annotType = annotation.getObject()['/Subtype'][1:]
                        if annotType == 'Text':
                            annotType = 'Note'
                        elif annotType == 'Square':
                            annotType = 'Square Highlight'
                        elif annotType == 'FreeText':
                            annotType = 'Inline Note'

                        content = annotation.getObject()['/Contents']
                        if type(content) != PyPDF2.generic.TextStringObject:
                            try:
                                content = content.decode("cp1252")
                            except:
                                print('The annotation has a weird encoding, try re-writting it.')

                        if searchTermRe.search(content):
                            foundMatch = True
                            spdf.printMatchMessage(pageNumber, path, commands, searchTerm, annotType)
                            spdf.printMatches(content, searchTermRe, contextLength)
            else:
                # there are no annotations on this page
                pass
        
        if not foundMatch:
            spdf.printNoMatchesFound(path, searchTerm)


if __name__ == '__main__':
    filePaths, commands, searchTerm, searchTermRe = spdf.main()
    search_pdf_annots(filePaths, commands, searchTerm, searchTermRe, contextLength=-1)