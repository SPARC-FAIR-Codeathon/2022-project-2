from serpapi import GoogleSearch
import os
import requests
from bs4 import BeautifulSoup


def serpapi_srape_cite_results(Authorization_API, title):
  params = {
    "api_key": Authorization_API,
    "engine": "google_scholar_cite",
    "q": title
  }

  search = GoogleSearch(params)
  results = search.get_dict()
  return results

def get_paperinfo(paper_url):

  #download the page
  response=requests.get(url,headers=headers)

  # check successful response
  if response.status_code != 200:
    print('Status code:', response.status_code)
    raise Exception('Failed to fetch web page ')

  #parse using beautiful soup
  paper_doc = BeautifulSoup(response.text,'html.parser')

  return paper_doc

  # this function for the extracting information of the tags
def get_tags(doc):
  paper_tag = doc.select('[data-lid]')
  cite_tag = doc.select('[title=Cite] + a')
  link_tag = doc.find_all('h3',{"class" : "gs_rt"})
  author_tag = doc.find_all("div", {"class": "gs_a"})

  return paper_tag,cite_tag,link_tag,author_tag

# it will return the title of the paper
def get_papertitle(paper_tag):
  
  paper_names = []
  
  for tag in paper_tag:
    paper_names.append(tag.select('h3')[0].get_text())

  return paper_names

# it will return the number of citation of the paper
def get_citecount(cite_tag):
  cite_count = []
  for i in cite_tag:
    cite = i.text
    if i is None or cite is None:  # if paper has no citatation then consider 0
      cite_count.append(0)
    else:
      tmp = re.search(r'\d+', cite) # its handle the None type object error and re use to remove the string " cited by " and return only integer value
      if tmp is None :
        cite_count.append(0)
      else :
        cite_count.append(int(tmp.group()))

  return cite_count

# function for the getting link information
def get_link(link_tag):

  links = []

  for i in range(len(link_tag)) :
    links.append(link_tag[i].a['href']) 

  return links 

# function for the getting autho , year and publication information
def get_author_year_publi_info(authors_tag):
  years = []
  publication = []
  authors = []
  for i in range(len(authors_tag)):
      authortag_text = (authors_tag[i].text).split()
      year = int(re.search(r'\d+', authors_tag[i].text).group())
      years.append(year)
      publication.append(authortag_text[-1])
      author = authortag_text[0] + ' ' + re.sub(',','', authortag_text[1])
      authors.append(author)
  
  return years , publication, authors

# creating final repository
paper_repos_dict = {
                    'Paper Title' : [],
                    'Year' : [],
                    'Author' : [],
                    'Citation' : [],
                    'Publication' : [],
                    'Url of paper' : [] }

# adding information in repository
def add_in_paper_repo(papername,year,author,cite,publi,link):
  paper_repos_dict['Paper Title'].extend(papername)
  paper_repos_dict['Year'].extend(year)
  paper_repos_dict['Author'].extend(author)
  paper_repos_dict['Citation'].extend(cite)
  paper_repos_dict['Publication'].extend(publi)
  paper_repos_dict['Url of paper'].extend(link)

  return pd.DataFrame(paper_repos_dict)
