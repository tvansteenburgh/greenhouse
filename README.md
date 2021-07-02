# Greenhouse automation stuff

## Install

```bash
git clone https://github.com/desrod/greenhouse
cd greenhouse
python3 -m venv .env
source .env/bin/activate
pip install selenium appdirs
```

If you are using Chrome you'll need to install the appropriate version
of ChromeDriver for your browser, see
https://chromedriver.chromium.org/downloads

Make sure you choose the version that is in the same major version as your installed version of Chrome. 

``` bash
$ google-chrome --version
Google Chrome 91.0.4472.114 
```

You can download the matching version, and unpack it into somewhere in your $PATH, or place it in a location you can append to $PATH later. I've put it into `/opt/bin` here: 

``` bash
$ /opt/bin/chromedriver --version
ChromeDriver 91.0.4472.101 (af52a90bf87030dd1523486a1cd3ae25c5d76c9b-refs/branch-heads/4472@{#1462})
```

You will also need to put this in your default `$PATH`, or export a new `$PATH` environment variable to include this location, eg: 

```bash
export PATH=$PATH:/opt/bin
```

## Adding your credentials to be used for the cloning/duplication
---
 The [oroginal automation](https://github.com/tvansteenburgh/greenhouse) this repo was forked from used environment variables to hodl the SSO_EMAIL and SSO_PASSWORD. This forked version puts these in a managed file in `~/.local/share/greenhouse/` called `login.tokens`, with the following format: 

``` json
{
    "username": "your.name@canonical.com",
    "password": "So0perSe3kre7P4ssw0rd"
}
```
Keep in mind that any 'foreign' characters you may have in your password may need to be escaped in this file, so it will be parsed correctly. For example, if you have a forward-slash '/' in your password, you'd need to escape that as follows: 

``` yaml
    "password": "So0per\\/Se3kre7\\/P4ssw0rd"
```

The same rule applies for backslashes: 

``` yaml
    "password": "So0per\\\\Se3kre7\\\\P4ssw0rd"
```
Protect this file with your standard operating system permissions. `chmod 0400` should be sufficient to secure it against any unintentional snooping.

## Duplicate job posts to different locations
---
Start with a Greenhouse job with one job posting (the one that will be duplicated).

Get the numeric id for the job. You can get this by going to the job dashboard and copying the id out of the url. It will look something like this:

`https://canonical.greenhouse.io/sdash/1592880`

That number at the end of the url is the job id.

Now run the script and tell it which job id(s) you want to update with new job posts, and which regions you want to post in:

``` bash
./post-job.py 1592880 1726996 --region americas emea
```

> Note: If you're cloning to multiple regions, you **must** provide them at the time of cloning. You cannot clone to 'emea' and then in a second pass, clone to 'americas', as this will fail. 

The browser will open and things will happen:

- Script will log you in to Ubuntu SSO and then pause for you to 2FA.
- New posts will be created for each city in the region that doesn't already have an existing post in that location.
- The new posts (and any others that are currently 'OFF') will be turned ON (made live on the 'Canonical - Jobs' board).
  
  > Note: Please make sure you review the posts when complete, so any that you intended to remain off, are disabled after cloning. 

If the script fails partway through you can safely rerun it, since it won't create a duplicate job post for cities that already have one.

> Note: If the script does fail, it may leave lingering 'chromedriver' processes running. You can kill those off easily with the following: 

``` bash 
kill -9 $(pgrep -f chromedriver)
```

### Browsers
---
Default browser is Chrome but you can alternatively pass the `--browser firefox` option.

I have only tested on Chrome.

### Regions

The available regions are `americas`, `emea`, `eu`, `brasil`, and `apac`. You can view/update the lists of cities in those regions directly in the source file.

### Troubleshooting
---
#### The script crashes with an error about `element click intercepted`.

- The script is trying to 'click' on something, but another element on the page is blocking the click.
- Try making your browser bigger (especially wider). This is most likely the quickest workaround.
- Create an issue with the full error message and I'll fix it if I can.
