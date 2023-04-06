from pathlib import Path
import pandas as pd
import requests
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
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
                       meta=['id', 'name', 'total_items_in_this_category', 'picture', 'permalink'],
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
def item_format(item: json) -> dict:
    """Convert item json to dictionary"""

    item_dict = {
            'id': item['id'],
            #'site_id': item['site_id'],
            'title': item['title'],
            'subtitle': item['subtitle'],
            'seller_id': item['seller_id'],
            'category_id': item['category_id'],
            'official_store_id': item['official_store_id'],
            'price': item['price'],
            'base_price': item['base_price'],
            'original_price': item['original_price'],
            'currency_id': item['currency_id'],
            'initial_quantity': item['initial_quantity'],
            'available_quantity': item['available_quantity'],
            'sold_quantity': item['sold_quantity'],
            #'sale_terms': item['sale_terms'],
            'buying_mode': item['buying_mode'],
            'listing_type_id': item['listing_type_id'],
            'start_time': item['start_time'],
            'stop_time': item['stop_time'],
            'condition': item['condition'],
            'permalink': item['permalink'],
            'thumbnail_id': item['thumbnail_id'],
            'thumbnail': item['thumbnail'],
            'secure_thumbnail': item['secure_thumbnail'],
            #'pictures': item['pictures']
        }
    return item_dict

@task()
def product_format(product: json) -> dict:
    """Convert product json to dictionary"""
    
    id = product['id']
    name = product['name']
    status = product['status']
    sold_quantity = product['sold_quantity']
    domain_id = product['domain_id']
    permalink = product['permalink']
    if product['buy_box_winner'] is not None:
        buy_box_winner_price = product['buy_box_winner']['price']
        buy_box_winner_currency_id = product['buy_box_winner']['currency_id']
        category_id = product['buy_box_winner']['category_id']
        seller_id = product['buy_box_winner']['seller_id']
        seller_city = product['buy_box_winner']['seller_address']['city']['name']            
        seller_state = product['buy_box_winner']['seller_address']['state']['name']
    else:
        buy_box_winner_price = None
        buy_box_winner_currency_id = None
        category_id = None
        seller_id = None
        seller_city = None
        seller_state = None
    picture_url = product['pictures'][0]['url']
    brand = next((attr['value_name'] for attr in product['attributes'] if attr['id'] == 'BRAND'), '')
    model = next((attr['value_name'] for attr in product['attributes'] if attr['id'] == 'MODEL'), '')
    color = next((attr['value_name'] for attr in product['attributes'] if attr['id'] == 'COLOR'), '')
    with_bluetooth = next((attr['meta']['value'] for attr in product['attributes'] if attr['id'] == 'WITH_BLUETOOTH'), False)
    with_usb = next((attr['meta']['value'] for attr in product['attributes'] if attr['id'] == 'WITH_USB'), False)
    includes_remote_control = next((attr['meta']['value'] for attr in product['attributes'] if attr['id'] == 'INCLUDES_REMOTE_CONTROL'), False)

    # Create a dictionary with product data
    product_dict = {
                'id': id,
                'name': name,
                'status': status,
                'sold_quantity': sold_quantity,
                'domain_id': domain_id,
                'permalink': permalink,
                'buy_box_winner_price': buy_box_winner_price,
                'buy_box_winner_currency_id': buy_box_winner_currency_id,
                'category_id': category_id,
                'seller_id': seller_id,
                'seller_city': seller_city,
                'seller_state': seller_state,
                'picture_url': picture_url,
                'brand': brand,
                'model': model,
                'color': color,
                'with_bluetooth': with_bluetooth,
                'with_usb': with_usb,
                'includes_remote_control': includes_remote_control
            }
    return product_dict

@flow(retries=3)
def products_api(df_best_sellers):
    """Download product information"""

    products_list = []
    items_list = []

    # Loop through the DataFrame and make an API query for each ID
    for idx, row in df_best_sellers.iterrows():
        ids = row['id']
        types = str(row['type']).lower()

        url = f'https://api.mercadolibre.com/{types}s/{ids}'
        # Make the query in the API
        #print(url)
        
        response = requests.get(url)
        
        if response.status_code == 200:
            
            if types == 'item':
                response = response.json()
                info_item = item_format(response)
                # Add to the list
                items_list.append(info_item)
                #print(info_item)
            elif types == 'product':
                if response.headers['content-type'] == 'application/json':
                    product = response.json()
                elif response.headers['content-type'] == 'application/x-ndjson':
                    product = response.json_lines()
                    
                #print(product)
                info_product = product_format(product)
                products_list.append(info_product)
        #else:
            #raise Exception('API error:', response.status_code)

    # Convert the list of dictionaries into a dataframe
    df_items = pd.DataFrame(items_list)
    df_products = pd.DataFrame(products_list)
    return df_products, df_items

@task()
def save_new_trends(df_trends: pd.DataFrame) -> pd.DataFrame:
    """Save the trends of each day"""

    hist_trends = pd.read_parquet('data/hist_trends.parquet')

    if not hist_trends.loc[hist_trends['date'] == (datetime.now()).strftime('%Y-%m-%d')].empty:
        print("There is data for today's date")
    else:   
        print("No data for today's date")
        df_trends['date'] = (datetime.now()).strftime('%Y-%m-%d')
        df_trends['ranking'] = range(1,len(df_trends)+1)
        df_trends_old=pd.read_parquet('data/hist_trends')
        df_merged = pd.concat([df_trends_old, df_trends], ignore_index=True)
        hist_trends = df_merged

    return hist_trends

@task()
def write_local(df: pd.DataFrame, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet file"""

    path = Path(f"data/{dataset_file}.parquet")
    df.to_parquet(path)
    return path

@task()
def write_gcs(path: Path) -> None:
    """Upload local parquet file to GCS"""

    gcs_block = GcsBucket.load("mla-bucket")
    gcs_block.upload_from_path(
        from_path=path, 
        to_path=path)
    return

@task()
def write_bq(df: pd.DataFrame, file:str) -> None:
    """Write DataFrame to BiqQuery"""

    gcp_credentials_block = GcpCredentials.load("mla-bucket-creds")

    table = f'mla_bq_zoom.{file}'

    df.to_gbq(
        destination_table=table,
        project_id="mla-dashboard-zoom",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        #if_exists="append",
        if_exists="replace",
    )

@flow()
def etl_parent_flow():

    trends = download_from_api('https://api.mercadolibre.com/trends/MLA')

    categories = download_from_api('https://api.mercadolibre.com/sites/MLA/categories')
    
    best_sellers = best_sellers_api(categories)

    products, items = products_api(best_sellers)

    files = ['categories', 'best_sellers', 'trends', 'items', 'products']
    df = [categories, best_sellers, trends, items, products]

    for i, file in enumerate(files):
        print(f'Writing file: {file}')
        path = write_local(df[i], file)
        write_gcs(path)
        write_bq(df[i], file)
   
if __name__ == "__main__":
    etl_parent_flow()