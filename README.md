# Greenhouse automation stuff

## Install

```bash
git clone git@github.com:tvansteenburgh/greenhouse.git
cd greenhouse
virtualenv -p python3 .venv
source .venv/bin/activate
pip install selenium
```

## Duplicate job posts to different locations

Start with a Greenhouse job with one job posting (the one that will be
duplicated).

Get the numeric id for the job. You can get this by going to the job
dashboard and copying the id out of the url. It will look something like
this:

`https://canonical.greenhouse.io/sdash/1592880`

That number at the end of the url is the job id.

Now run the script and tell it which job id(s) you want to update with
new job posts, and which regions you want to post in:

```bash
SSO_EMAIL=myemail@gmail.com \
SSO_PASSWORD=mysecretpassword \
./post-job.py 1592880 1726996 --region americas emea
```

The browser will open and things will happen:

- New posts will be created for each city in the region that doesn't
  already have a post
- The new posts (and any others that are OFF) will be turned ON (made
  live on the 'Canonical - Jobs' board)

If the script fails partway through you can safely rerun it, since it won't
create a duplicate job post for cities that already have one.

### Browsers

Default browser is Chrome but you can alternatively pass the `--browser firefox` option.

I have only tested on Chrome.

### Regions

The available regions are `americas`, `emea`, and `apac`. You can
view/update the lists of cities in those regions directly in the source
file.

The `apac` region currently has no cities defined.
