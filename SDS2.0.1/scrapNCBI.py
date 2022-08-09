
# API interaction to acquire data from NCBI utils

import time
import json
import requests
import urllib.parse as urlparser
from requests.structures import CaseInsensitiveDict

class NIH_NCBI:

    __NIH_timestamp = None 
    __NCBI_timestamp = None 


    def __maintainRequestFrequency (self, timestamp, request_per_second):
        seconds_per_request = 1 / request_per_second
        if (timestamp != None):
            dt = time.time() - timestamp
            if (dt < seconds_per_request):
                time.sleep(seconds_per_request - dt)
        return time.time()


    def _generateFundingDetailsPayload (self, project_no):
        data = {}
        data['criteria'] = {'project_nums': project_no}
        return json.dumps(data)
    
    def _generateNCBIpublicationRecord (self, jsonPub):
        data = {}

        data['title']  = jsonPub['title']
        data['journal'] = jsonPub['source']
        data['year']   = jsonPub['pubdate'].split(' ')[0]

        author_list = ''
        for author in jsonPub['authors']:
            author_list = author['name'] + ', '
        data['author_list'] = author_list

        for id in jsonPub['articleids']:
            data[id['idtype']] = id['value']

        return data


    def _getPublicationFromPubmed (self, pm_id):
        self.__NCBI_timestamp = self.__maintainRequestFrequency(self.__NCBI_timestamp, 1)
        resp = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&retmode=json&id=' + str(pm_id))

        record = {}
        if (resp.status_code == 200):
            jsonData = json.loads(resp.content)

            if (len(jsonData['result']['uids']) > 0):
                record = self._generateNCBIpublicationRecord(jsonData['result'][str(pm_id)])

        return record

    def _getPublicationFromPMC (self, pmc_id):
        self.__NCBI_timestamp = self.__maintainRequestFrequency(self.__NCBI_timestamp, 1)
        resp = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&retmode=json&id=' + str(pmc_id))
        
        record = {}
        if (resp.status_code == 200):
            jsonData = json.loads(resp.content)

            if (len(jsonData['result']['uids']) > 0):
                record = self._generateNCBIpublicationRecord(jsonData['result'][str(pmc_id)])
        
        return record
    
 


    def getCitedBy (self, id_type, id):
        urls = []
        if (id_type == 'pm_id'):
            urls.append('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pubmed_citedin&retmode=json&id=' + str(id))
            urls.append('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pubmed_pmc_refs&retmode=json&id=' + str(id))
        elif (id_type == 'pmc_id'):
            urls.append('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&linkname=pmc_pmc_citedby&retmode=json&id=' + str(id))

        record = {}
        
        for url in urls:
            self.__NCBI_timestamp = self.__maintainRequestFrequency(self.__NCBI_timestamp, 1)
            resp = requests.get(url)

            if (resp.status_code != 200):
                return {}
        
            jsonData = json.loads(resp.content)
            linksets = jsonData['linksets'][0]

            if ('linksetdbs' not in linksets):
                continue

            cited_by = linksets['linksetdbs'][0]

            for cited_id in cited_by['links']:
                pub = {}
                if (cited_by['dbto'] == 'pubmed'):
                    pub = self._getPublicationFromPubmed(cited_id)
                elif (cited_by['dbto'] == 'pmc'):
                    pub = self._getPublicationFromPMC(cited_id)

                # Ignore if the publication doesn't have a doi
                if 'doi' in pub:
                    record[pub['doi']] = pub

        return record
    
 
    def getProjectFundingDetails (self, project_no):
        self.__NIH_timestamp = self.__maintainRequestFrequency(self.__NIH_timestamp, 1)
        url = "https://api.reporter.nih.gov/v1/projects/Search/"
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"

        payload = self._generateFundingDetailsPayload(project_no)
        resp = requests.post(url, headers=headers, data=payload)
        
        if (resp.status_code == 200):
            return json.loads(resp.content)
        
        return {}

 

    def generateRecord (self, jsonData):
        record = {}

        for sub_project in jsonData['results']:
            data = {}
            data['appl_id']   = sub_project['appl_id']
            data['institute'] = sub_project['org_name']
            data['country']   = sub_project['org_country']
            data['amount']    = sub_project['award_amount']
            data['year']      = sub_project['fiscal_year']
            data['keywords']  = sub_project['terms']

            record[sub_project['project_num']] = data
        return record
    

    def getPublications (self, appl_id):
        self.__NIH_timestamp = self.__maintainRequestFrequency(self.__NIH_timestamp, 1)
        resp = requests.get('https://reporter.nih.gov/services/Projects/Publications?projectId=' + str(appl_id))
        
        record = {}
        if (resp.status_code == 200):
            jsonPub = json.loads(resp.content)
            
            for pub in jsonPub['results']:
                pubmed_data  = self._getPublicationFromPubmed(pub['pm_id'])

                data = {}
                data['title']       = pub['pub_title']
                data['journal']     = pub['journal_title']
                data['year']        = pub['pub_year']
                data['author_list'] = pub['author_list']
                data['url']         = pub['journal_title_link']['value']
                data['pm_id']       = pub['pm_id']

                # Ignore if the paper doesn't have a doi
                if ('doi' in pubmed_data):
                    data['doi']                = pubmed_data['doi']
                    record[pubmed_data['doi']] = data
        
        return record




    
