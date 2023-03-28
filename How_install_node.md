# Step 1: Get NVM
Open a new terminal window and check if you have a .zshrc profile by running the following command:
```
ls -a
```
If you can see .zshrc in the list, then you can skip this step. Otherwise, if you don't see it, it means you don't have it, and you need to create one by running this command:
```
touch .zshrc
```
Now that you have a .zshrc profile, you can get NVM. Visit [this website](https://github.com/nvm-sh/nvm#install--update-script) to find the cURL install command for NVM under the section called "Install & Update Script". The command looks like this:

```
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash
```

Copy the command and paste it into your terminal. This installs NVM and makes it available for use.
Since this installation affects your .zshrc profile, you need to refresh things by running this command:
```
source .zshrc
```
NVM is now installed! You can confirm this by running the command nvm.

# Step 2: Get Node
To install Node, simply run this command in your terminal:
nvm install node
Node is now downloaded but you need to run the following command to actually use it:
```
nvm use node
```

# Step 3: Confirm Everything Works
It's time to double-check that everything works. You can run the following commands to make sure you're using the correct versions of Node, NPM, and NVM:
```
node -v
npm -v
nvm -v
```
If you see version numbers pop up for each of these commands, then you're good to go!