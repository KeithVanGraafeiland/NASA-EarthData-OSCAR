import requests
import os
from earthdata_credentials import EDusername, EDpassword
from datetime import date, timedelta
# get the requsts library from https://github.com/requests/requests
# overriding requests.Session.rebuild_auth to maintain headers when redirected

class SessionWithHeaderRedirection(requests.Session):
    AUTH_HOST = 'urs.earthdata.nasa.gov'
    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

   # Overrides from the library to keep headers when redirected to or from
   # the NASA auth host.
    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)
            if (original_parsed.hostname != redirect_parsed.hostname) and redirect_parsed.hostname != self.AUTH_HOST and original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']
        return

# create session with the user credentials that will be used to authenticate access to the data
username = EDusername #TODO replace with your Username
password= EDpassword #TODO Replace with your password
session = SessionWithHeaderRedirection(username, password)
# the url of the file we wish to retrieve

start_date = date(2022, 1, 15) #TODO replace with your Start Date
end_date = date(2022, 2, 15) #TODO replace with your End Date
delta = end_date - start_date   # returns timedelta
date_list = []

for i in range(delta.days + 1):
    day = start_date + timedelta(days=i)
    date = day.strftime("%Y%m%d")
    # print(date)
    date_list.append(date)
# print(date_list)

d_list = date_list #TODO Load list of dates to iterate through
output_path = "C:/temp/oscar/" #TODO Replace with the path on your computer to write the data to

for d in d_list:
    #url = "https://opendap.earthdata.nasa.gov/collections/C2098858642-POCLOUD/granules/oscar_currents_final_{date_string}.dap.nc4?dap4.ce=/lon[0:1:1439];/time[0:1:0];/vg[0:1:0][0:1:1439][0:1:718];/u[0:1:0][0:1:1439][0:1:718];/lat[0:1:718];/ug[0:1:0][0:1:1439][0:1:718];/v[0:1:0][0:1:1439][0:1:718]".format(date_string=d)
    #url = "https://opendap.earthdata.nasa.gov/collections/C2098858642-POCLOUD/granules/oscar_currents_final_{date_string}.dap.nc4".format(date_string=d)
    url = "https://archive.podaac.earthdata.nasa.gov/podaac-ops-cumulus-protected/OSCAR_L4_OC_NRT_V2.0/oscar_currents_nrt_{date_string}.nc".format(date_string=d)
    # extract the filename from the url to be used when saving the file
    filename = url[url.rfind('/')+1:]
    if os.path.exists(output_path + filename):
        print(filename + " already exists - skipping.....")
        continue
    # print(filename)

    try:
        # submit the request using the session
        response = session.get(url, stream=True)
        # print(response.status_code)
        # raise an exception in case of http errors
        response.raise_for_status()
        # save the file
        with open(output_path + filename, "wb") as file:
            print('Downloading ' + filename + '.....')
            file.write(response.content)
            print('Sucessfully downloaded ' + filename + '.....')
    except requests.exceptions.HTTPError as e:
        # handle any errors here
        print(e)