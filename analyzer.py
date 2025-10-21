from bs4 import BeautifulSoup, Tag


def fromTableFootGetInformation(table : Tag):

    pass

def analyzeJacocoReport(path : str):
    content = ''
    with open(path + r'\target\site\jacoco\index.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    cols = soup.find('table', {'class': 'coverage'}).find('tbody').find('tr').find_all('td')

    

    

if __name__ == '__main__':
    path = r'C:\Test\Java\FastestRoute'
    analyzeJacocoReport(path)
    print(analyzeJacocoReport(path).__dict__)