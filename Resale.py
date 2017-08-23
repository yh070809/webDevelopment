from bs4 import BeautifulSoup
import urllib.request
import csv
import zipfile
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# import seaborn as sns

root_url = "https://data.gov.sg"
resale2000_csv = "resale-flat-prices-based-on-approval-date-2000-feb-2012.csv"
resale2012_csv = "resale-flat-prices-based-on-registration-date-from-march-2012-onwards.csv"

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, 'data')
if not os.path.exists(DATA_DIR):
    os.mkdir(DATA_DIR)

#Crawl and save it as csv using the download link of the data on website
def crawl_download_link(url):
    #get the page content
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urllib.request.urlopen(req).read()
    soup_page = BeautifulSoup(page, 'lxml')

    #get the download link content
    download_tag = soup_page.find(class_='btn btn-primary')
    download_url = root_url + download_tag['href']
    print(download_url)

    #download and save the file
    req2 = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
    output = open("data.zip", "wb")
    output.write(urllib.request.urlopen(req2).read())
    output.close()

def merge_files(path):
    #get csv file list
    resale_file_names = [x for x in os.listdir(path) if x.startswith('resale') and x.endswith('.csv')]
    
    #output file path
    csv_write_path = os.path.join(path, 'resale.csv')

    with open(csv_write_path, 'w') as csv_write_file:
        csv_writer = csv.writer(csv_write_file)

        for file_index, resale_file_name in enumerate(resale_file_names):###枚举
            print('Collating %s' % resale_file_name)
            resale_file_path = os.path.join(path, resale_file_name)

            #keep track of read rows
            row_count = 0

            with open(resale_file_path, 'r') as read_file:
                csv_reader = csv.reader(read_file)
                header = next(csv_reader)

                if file_index == 0:
                    csv_writer.writerow(header)

                for row in csv_reader:
                    csv_writer.writerow(row)
                    row_count += 1

            print('Collated %s: %d rows read' % (resale_file_name, row_count))
            print()


def unpack_zipfile(filepath):
    zfile = zipfile.ZipFile(filepath, 'r')
    for f in zfile.namelist():
        data = zfile.read(f)
        outpath = os.path.join(DATA_DIR, f)
        file = open(outpath, 'w+b')
        file.write(data)
        file.close()
    
def handle_latest_year_data():
    read2012_path = os.path.join(DATA_DIR, resale2012_csv)
    df = pd.read_csv(read2012_path)
    df['month'] = pd.to_datetime(df['month'])
    mask = (df['month'] >= '2015-09') & (df['month'] <= '2016-09')
    df_latest = df.loc[mask]
    df_latest['month'] = df['month'].dt.strftime('%Y-%m')
    df_latest['sqm_price'] = df['resale_price'] / df['floor_area_sqm']
    
    df_latest_sales = df_latest['town'].value_counts()
    print(df_latest_sales)
    latest_sale_path = os.path.join(DATA_DIR, 'latest_sales.csv')
    df_latest_sales.to_csv(latest_sale_path, encoding='utf-8')
    plt.figure(1)
    (df_latest_sales.head(5)).plot(kind="bar",title="Popular Town",fontsize=8)

    df_latest_type = df_latest['flat_type'].value_counts()
    print(df_latest_type)
    latest_type_path = os.path.join(DATA_DIR, 'latest_type.csv')
    df_latest_type.to_csv(latest_type_path, encoding='utf-8')
    plt.figure(2)
    (df_latest_type.head(5)).plot(kind="bar",title="Popular Type",fontsize=8)

    df_latest_sqm = df_latest.groupby(['town']).mean()['sqm_price'].copy()
    df_latest_sqm.sort(['sqm_price'],ascending=False)
    print(df_latest_sqm)
    latest_sqm_path = os.path.join(DATA_DIR, 'latest_sqm.csv')
    df_latest_sqm.to_csv(latest_sqm_path, encoding='utf-8')
    plt.figure(3)
    (df_latest_sqm.head(5)).plot(kind="pie",title="Expensive Area",fontsize=8)
    
    mask = (df['town']=='CENTRAL AREA')
    df_latest_central = df_latest.loc[mask]
    print(df_latest_central)
    df_latest_central_avg = df_latest_central.groupby(['month']).mean()['sqm_price'].copy()
    #df_latest_central_avg.sort(['month'],ascending=False)
    print(df_latest_central_avg)
    plt.figure(4)
    df_latest_central_avg.plot(kind="line",title="Central Trend",fontsize=8)

    plt.show()
    
if __name__ == '__main__':

    crawl_download_link("https://data.gov.sg/dataset/resale-flat-prices")
    zipfile_path =  os.path.join(CURRENT_DIR, 'data.zip')
    unpack_zipfile(zipfile_path)
    #merge_files(DATA_DIR)
    handle_latest_year_data()



