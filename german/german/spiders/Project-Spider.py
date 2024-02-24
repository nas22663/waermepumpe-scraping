import scrapy
from scrapy.http import FormRequest

class FachpartnerSpider(scrapy.Spider):
    name = 'fachpartner'
    allowed_domains = ['www.german.de']
    base_url = 'https://www.waermepumpe.de/fachpartnersuche/fachpartner/?no_cache=1&tx_bwpfps_fachpartnersuche%5Bcontroller%5D=Fachpartnersuche&cHash=0338cabe8eab7b60c5133289bd35b497'

    def __init__(self):
        with open('zipcodes.txt', 'r') as file:
            self.zipcodes = [line.strip() for line in file]

    def start_requests(self):
        for zipcode in self.zipcodes:
            formdata = {
                'tx_bwpfps_fachpartnersuche[search]': '1',
                'tx_bwpfps_fachpartnersuche[select]': 'fp',
                'tx_bwpfps_fachpartnersuche[sector]': '4',
                'tx_bwpfps_fachpartnersuche[place]': zipcode,
                'tx_bwpfps_fachpartnersuche[fpsubmit]': 'Suchen',
            }
            yield FormRequest(url=self.base_url, method='POST', formdata=formdata, callback=self.parse_response, meta={'zipcode': zipcode})

    def parse_response(self, response):
        zipcode = response.meta['zipcode']
        for company in response.css('div.fpresult-row'):
            self.logger.debug(f"Processing company UID: {company.attrib.get('uid', 'Unknown UID')}")

            website = company.css('div.resultheader h3 a::attr(href)').get(default='Website not found')
            google_maps_link = company.css('div.infobox.address p a.gmap::attr(href)').get(default='').replace(' ', '')

            # Extracting telephone and fax as they appear on the page and removing any NBSP characters
            telephone = company.css('div.infobox.address p:contains("Telefon:")::text').get(default='Telephone not found').replace('\xa0', ' ').strip()
            fax = company.css('div.infobox.address p:contains("Fax:")::text').get(default='Fax not found').replace('\xa0', ' ').strip()

            email = company.css('div.infobox.address p a[href^="mailto:"]::text').get(default='Email not found')

            result_name = company.css('div.resultheader h3 a::text').get()
            if not result_name:
                result_name = company.css('div.resultheader h3::text').get(default='').strip()

            yield {
                'zipcode': zipcode,
                'result_name': result_name,
                'Google Map': google_maps_link,
                'website': website,
                'telephone': telephone,
                'fax': fax,
                'email': email,
            }
