from mcp.server.fastmcp import FastMCP

from bs4 import BeautifulSoup, Tag
from pathlib import Path
from bs4 import XMLParsedAsHTMLWarning
import warnings

import os
from pathlib import Path

from pydantic import Field

from datas.report import SingleJavaFileReport, MissCover, BaseReport, SingleJavaFileBranchReport, MutationMissCover, MyList

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

mcp = FastMCP('TestReport')

def list2json(list : list[SingleJavaFileReport]):
    json = '['
    for item in list:
        json += str(item.__dict__())
        json += ','
    json = json[:-1]
    json += ']'
    return json

def readFile(path : str, type : str) -> BeautifulSoup:
    content = ''
    with open(path, 'r') as file:
        content = file.read()
    
    mode = 'lxml' if type == 'xml' else 'html.parser'
    return BeautifulSoup(content, mode)

def findPitestDir(path : str) -> str:
    dirs = [item for item in os.listdir(path + (Path('target') / 'pit-reports'))]
    dirs.sort()
    return dirs[-1]

def getProjectName(path : str) -> str:
    return path.split('\\')[-1]

@mcp.tool('getTestReportOverview')
def overview(path : str = Field(..., description="The absolute path of the project's root directory")) -> str:

    '''
        Show test report overview

        Returns:
            A string containing the analysis results, including mutation coverage and branch coverage
            (If you want to see the detailed results, please use the "getBranchTestReport" or "getMutationTestReport" tool)
    '''
    
    try:
        #Path('target') / 'pit-reports' / f'{findPitestDir(path)}' / 'index.html'
        pitestSoup = readFile(path + r'\target\pit-reports\{}\index.html'.format(findPitestDir(path)), 'html')
        jacocoSoup = readFile(path + r'\target\site\jacoco\jacoco.xml', 'xml')
    except FileNotFoundError:
        return 'No pitest or jacoco report found'
    except Exception as e:
        return 'error: {}'.format(e)
    
    branch = jacocoSoup.select_one('report > counter[type="BRANCH"]')
    branchMiss = int(branch.attrs['missed'])
    branchCoverd = int(branch.attrs['covered'])
    branchTotal = branchMiss + branchCoverd

    mutation = pitestSoup.select_one('h1 + h3 + table > tbody > tr > td:last-child > div > div[class="coverage_ledgend"]')
    mutationCovered, mutationTotal= [int(i) for i in mutation.text.split('/')]
    mutationMissed = mutationTotal - mutationCovered

    result = f'''{getProjectName(path)}: {'{'}
    branch coverage: {branchCoverd / branchTotal if branchTotal != 0 else 1:.2%},
    total branches: {branchTotal},
    branch covered: {branchCoverd},
    branch missed: {branchMiss},

    mutation coverage: {mutationCovered / mutationTotal if mutationTotal != 0 else 1:.2%},
    total mutations: {mutationTotal}
    mutation covered: {mutationCovered},
    mutation missed: {mutationMissed}
{'}'}'''

    return result

    

@mcp.tool('getMutationTestReport')
def mutationTestReport(path : str = Field(..., description="The absolute path of the project's root directory"), 
                       className : str = Field(..., description="The name of the class(without package)")):

    '''
        Show test report for mutation test

        Returns:
            A string containing the analysis results, including mutation coverage,total number of mutations and at which line what mutators were applied in missed mutations.

    '''

    targetDir = findPitestDir(path)

    try:
        pitestSoup = readFile(f'{path}\\target\\pit-reports\\{targetDir}\\net.mooctest\\index.html', 'html')
    except FileNotFoundError:
        return 'No pitest report found'
    except Exception:
        return 'Error when parsing pitest report'

    trs = pitestSoup.select('table tbody')[-1].select('tr')
    tr_target = None
    for each in trs:
        if each.select_one('td > a').text == f'{className}.java':
            tr_target = each
            break
    
    cover, total = [int(i) for i in tr_target.select('div.coverage_ledgend')[-1].text.split('/')]


    pitestSoup = readFile(f'{path}\\target\\pit-reports\\{targetDir}\\net.mooctest\\{className}.java.html', 'html')
    survived_mutations = pitestSoup.select('table tr:has(td:last-child:-soup-contains("Mutations")) ~ tr')
    survived_mutations = [each for each in survived_mutations if each.find('p', {'class': 'SURVIVED'})] + [each for each in survived_mutations if each.find('p', {'class': 'NO_COVERAGE'})]
    
    miss_covers = MyList(switchLines=1, switchTable=2)
    for tr in survived_mutations:
        tds = tr.select('td')
        spans = tds[-1].select('p.SURVIVED > span.pop,p.NO_COVERAGE > span.pop')
        line = int(tds[0].find('a', recursive=False).text)
        miss_covers.append(MutationMissCover(line, [span.next_sibling.text for span in spans]))

    result = f'''{className}.java: {'{'}
    mutation coverage: {cover / total if total != 0 else 1:.2%},
    total mutation: {total},
    mutation missed:{miss_covers}\n{'}'}'''
    
    return result

@mcp.tool('getBranchTestReport')
def branchTestReport(path : str = Field(..., description="The absolute path of the project's root directory"), 
                     className : str = Field(..., description="The name of the class(without package)")):

    '''
        Show test report for branch test

        Returns:
            A string containing the analysis results, including branch coverage,total number of branches and at which line the branch is.

    '''
    
    try:
        jacocoSoup = readFile(path + r'\target\site\jacoco\jacoco.xml', 'xml')
    except FileNotFoundError:
        return 'No jacoco report found'
    except Exception:
        return 'Error when parsing jacoco report'

    packageName = jacocoSoup.find('package').get('name')
    
    sourcefile = jacocoSoup.find('sourcefile', {'name': f'{className}.java'})
    counter= sourcefile.find('counter', {'type': 'BRANCH'})

    covered = int(counter.get('covered'))
    missed = int(counter.get('missed'))
    total = covered + missed

    lines = sourcefile.find_all('line')

    missed_branch_lines = ''
    for line in lines:
        if line.get('mb') != '0':
            mb = int(line.get('mb'))
            cb = int(line.get('cb'))
            missed_branch_lines += f'At line {line.get("nr")}: {mb} of {mb + cb} branches missed;'
    missed_branch_lines = missed_branch_lines[:-1]

    result = f'''{className}.java: {'{'}
    branch coverage: {covered / total if total != 0 else 1:.2%},
    total branch: {total},
    branch missed:[
        {missed_branch_lines}
    ]\n{'}'}'''

    return result


def main():
    mcp.run(transport='stdio')

    

if __name__ == '__main__':
    main()