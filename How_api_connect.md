# How to connect to MLA API

## 1. Have an active MLA account.
To create a new account, enter www.mercadolibre.com.ar and select the option Create your account.
##  2. Go to devcenter.
Once logged into your account, go to https://developers.mercadolibre.com.ar/ there you can read all the API documentation.
## 3. Connect accounts.
Go to https://developers.mercadolibre.com.ar/devcenter/accountLink to link your account with the API.
## 4. Create the APP.
Now that the account is linked, it is necessary to create an application. You can follow the steps indicated in the documentation at https://developers.mercadolibre.com.ar/es_ar/registra-tu-aplicacion.
## 5. Create a URL.
As the application asks us for a URL, use [Localtunnel](https://theboroer.github.io/localtunnel-www/).
Localtunnel allows you to easily share a web service on your local development machine without messing with DNS and firewall settings.

- Localtunnel requires the installation of NodeJS.
- [Instructions to install NodeJS on Mac M1](/How_install_node.md).
- Now we can install Localtunnel with:
```
npm install -g localtunnel
```
- Start a webserver on some local port (eg http://localhost:8000) and use the command line interface to request a tunnel to your local server:
```
lt --port 8000
```
- This gives us a URL like for example: https://tough-monkeys-fly-179-60-102-147.loca.lt that we can use in the application settings.

## 6. Associate user & app.
Now we must paste this URL into the browser to associate the user with the app that we have just created. Replacing the APP_ID and the URL.
```
https://auth.mercadolibre.com.ar/authorization?response_type=code&client_id= APP_ID&redirect_uri=URL
```
The web will ask us to confirm the user's association and once ready, it returns a code in the URL like this:

```
https://tough-monkeys-fly-179-60-102-147.loca.lt/?code=TG-6422043f4adbc600012d921b-831918494
```

## 7. Generate the token.
Now we use all this information to generate a token to communicate with the API like this:

- Format:
```
curl -X POST \
-H 'accept: application/json' \
-H 'content-type: application/x-www-form-urlencoded' \
'https://api.mercadolibre.com/oauth/token' \
-d 'grant_type=authorization_code' \
-d 'client_id=$APP_ID' \
-d 'client_secret=$SECRET_KEY' \
-d 'code=$SERVER_GENERATED_AUTHORIZATION_CODE' \
-d 'redirect_uri=$REDIRECT_URI' \
-d 'code_verifier=$CODE_VERIFIER' 
```
- For example:
```
curl -X POST \
-H 'accept: application/json' \
-H 'content-type: application/x-www-form-urlencoded' \
'https://api.mercadolibre.com/oauth/token' \
-d 'grant_type=authorization_code' \
-d 'client_id=813255345445XXXX' \
-d 'client_secret=c1DvvNzya35i1hSXrz0hkNdSMoknXXXX' \
-d 'code=TG-6422043f4adbc600012d921b-XX1918XX4' \
-d 'redirect_uri=https://tough-monkeys-fly-179-60-102-147.loca.lt' \
-d 'code_verifier=TG-6422043f4adbc600012d921b-XX1918XX4'
```
As a result we get a token like this:
```
{"access_token":"APP_USR-8432553454451839-003271-be93880a331bXXXXXe2156cb10e2fade-XX1918XX4","token_type":"Bearer","expires_in":21600,"scope":"offline_access read","user_id":XX1918XX4,"refresh_token":"TG-6422051fa006d10001ab3f57-XX1918XX4"}
```

## 8. Communicate with API.
Now you can test the API with this command for example to check the trends:
```
curl -X GET -H 'Authorization: Bearer APP_USR-8432553454451839-003271-be93880a331bXXXXXe2156cb10e2fade-XX1918XX4' https://api.mercadolibre.com/trends/MLA
```

## 9. Save the API Information in a file.
Save the api information in a config.json file, with this format and the data obtained for your app:
```
{"access_token": "APP_USR-XXX-XXX-XX-X", 
"token_type": "Bearer", 
"expires_in": 21600, 
"scope": "offline_access read", 
"user_id": XXX, 
"refresh_token": "TG-XXX", 
"expiration_time": "2023-04-04T16:22:24.152470", "secret_key": "XXX"}
```
This allows us to then update the token directly from the python script.

### All API documentation available at:
https://developers.mercadolibre.com.ar/es_ar/api-docs-es
