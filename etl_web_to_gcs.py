from pathlib import Path
import pandas as pd
import requests
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from datetime import datetime, timedelta
import json

@task()
def refresh_token(token_info: json):
    """refresh API token"""

    # Read the values ​​from the JSON file
    with open('config.json', 'r') as file:
        token_info = json.load(file)

    url = 'https://api.mercadolibre.com/oauth/token'
    payload = {
        'grant_type': 'refresh_token',
        'client_id': token_info['user_id'],
        'client_secret': token_info['secret_key'],
        'refresh_token': token_info['refresh_token']
    }
    response = requests.post(url, data=payload, headers={'User-Agent': 'MLA-Trends/0.0.1'})

    if response.status_code == 200:
        data = response.json()
        now = datetime.now()
        expiration_time = now + timedelta(hours=6)
        
        new_token_info = {
            'access_token':data['access_token'],
            'token_type':data['token_type'],
            'expires_in':data['expires_in'],
            'scope':data['scope'],
            'user_id':token_info['user_id'],
            'refresh_token':data['refresh_token'],
            'expiration_time':expiration_time.isoformat(),
            'secret_key':token_info['secret_key']}
    else:
        raise Exception('Refresh Token Error:', response.content)

    # Save the dictionary to a JSON file
    with open('config.json', 'w') as file:
        json.dump(new_token_info, file)
    
    print(f'new_expiration_time: {expiration_time}')
    print(f'now: {now}')

@flow()
def read_api_data() -> str:
    """Read API information"""
    # Read the values ​​from the JSON file
    with open('config.json', 'r') as file:
        token_info = json.load(file)
    
    # Convert the value of expiration_time to a datetime object
    expiration_time = datetime.fromisoformat(token_info['expiration_time'])
    now = datetime.now()

    print(f'expiration_time: {expiration_time}')

    if expiration_time < now:
        refresh_token(token_info)
        with open('config.json', 'r') as file:
            token_info = json.load(file)

    token_type=token_info['token_type']
    access_token=token_info['access_token']
    token = f'{token_type} {access_token}'

    return token
    

@flow(retries=3)
def download_from_api(url: str) -> pd.DataFrame:
    """Download information from API"""

    token=read_api_data()

    headers = {'Authorization': token}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        return df
    else:
        raise Exception('API error:', response.status_code)

@task()
def subcategories_download(categories: pd.DataFrame) -> pd.DataFrame:
    """Download the information of each subcategory from API"""
    
    url = 'https://api.mercadolibre.com/categories/'

    # Create an empty list to hold the API responses
    api_responses = []

    # Loop through the DataFrame and make an API query for each ID
    for idx, row in categories.iterrows():
        id = row['id']
        name = row['name']

        response = requests.get(url + id)
        api_responses.append(response.json())

    #Convert to a pandas DataFrame
    api_df = pd.json_normalize(api_responses, 
                       record_path=['children_categories'], 
                       meta=['id', 'name', 'total_items_in_this_category', 'picture', 'permalink', 'path_from_root'],
                       meta_prefix='category_')
    return api_df

@flow()
def best_sellers_api(categories):
    """Download the information of the best sellers by category from API"""
    
    url = 'https://api.mercadolibre.com/highlights/MLA/category/'
    
    token=read_api_data()
    headers = {'Authorization': token}
    # Create an empty list to hold the API responses
    api_responses = []

    # Loop through the DataFrame and make an API query for each ID
    for idx, row in categories.iterrows():
        id = row['id']

        response = requests.get(url + id, headers=headers)
        
        if response.status_code == 200:
            data_sales_category = response.json()['content']
        
            # Convert the list of items to a DataFrame
            df_sales= pd.DataFrame(data_sales_category)
            df_sales['category']=id
            api_responses.append(df_sales)
        
    # joins all DataFrames in the list into a single DataFrame
    df_concatenado = pd.concat(api_responses)   
    return df_concatenado

@task()
def products_api(df: pd.DataFrame) -> pd.DataFrame:
    """Download product information"""


@task()
def write_local(df: pd.DataFrame, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet file"""

    path = Path(f"data/{dataset_file}.parquet")
    df.to_parquet(path, compression="gzip")
    return path

@task()
def write_gcs(path: Path) -> None:
    """Upload local parquet file to GCS"""

    gcs_block = GcsBucket.load("mla-bucket")
    gcs_block.upload_from_path(
        from_path=path, 
        to_path=path)
    return

@flow()
def etl_parent_flow():

    trends = download_from_api('https://api.mercadolibre.com/trends/MLA')
    path = write_local(trends, "trends")
    write_gcs(path)

    categories = download_from_api('https://api.mercadolibre.com/sites/MLA/categories')
    path = write_local(categories, "categories")
    write_gcs(path)

    subcategories = subcategories_download(categories)
    path = write_local(subcategories, "subcategories")
    write_gcs(path)

    best_sellers = best_sellers_api(categories)
    path = write_local(best_sellers, "best_sellers")
    write_gcs(path)

    products = products_api(best_sellers)
    path = write_local(products, "products")
    write_gcs(path)
    
if __name__ == "__main__":
    etl_parent_flow()