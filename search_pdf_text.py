import pdftotext
import search_pdf_module as spdf

def search_pdf_text(filePaths, commands, searchTerm, searchTermRe, contextLength=30):
    for path in filePaths:
        foundMatch = False
        with open(path, 'rb') as file:
            pdfText = pdftotext.PDF(file)
            for pageNumber, page in enumerate(pdfText):
                if searchTermRe.search(page):
                    foundMatch = True
                    spdf.printMatchMessage(pageNumber, path, commands, searchTerm)
                    spdf.printMatches(page, searchTermRe, contextLength)

        if not foundMatch:
            spdf.printNoMatchesFound(path, searchTerm)


if __name__ == '__main__':
    filePaths, commands, searchTerm, searchTermRe = spdf.main()
    search_pdf_text(filePaths, commands, searchTerm, searchTermRe, contextLength=50)