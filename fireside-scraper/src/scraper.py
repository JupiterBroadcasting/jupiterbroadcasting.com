import concurrent.futures
import json
import operator
import os
from re import S
from urllib.parse import urlparse

import html2text
import requests
import yaml
from bs4 import BeautifulSoup
from dateutil.parser import parse as date_parse
from jinja2 import Template

DATA_ROOT_DIR = "/data"

# Missing data found in a show. Used to scrape and/or create these files after the
# episode files been created.
MISSING_SPONSORS = {}
MISSING_HOSTS = set()
MISSING_GUESTS = set()


with open("templates/episode.md.j2") as f:
    TEMPLATE = Template(f.read())


def log_warn(show, ep, msg):
    print(f"WARN | {show} {ep} | {msg}")


def mkdir_safe(directory):
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass


def get_list(soup, pre_title):
    """
    Blocks of links are preceded by a `p` saying what it is.
    """
    pre_element = soup.find("p", string=pre_title)
    if pre_element is None:
        return None
    return pre_element.find_next_sibling("ul")


def get_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def get_plain_title(title: str):
    """
    Get just the show title, without any numbering etc
    """
    # Remove number before colon
    title = title.split(":", 1)[-1]

    # Remove data after the pipe
    title = title.rsplit("|", 1)[0]

    # Strip any stray spaces
    return title.strip()


def create_episode(api_episode, show_config, hugo_data, output_dir):
    try:
        mkdir_safe(output_dir)

        # RANT: What kind of API doesn't give the episode number?!
        episode_number = int(api_episode["url"].split("/")[-1])
        episode_number_padded = f"{episode_number:03}"

        output_file = f"{output_dir}/{episode_number}.md"

        if os.path.isfile(output_file):
            print("Skipping", api_episode['url'], "as it already exists")
            return

        publish_date = date_parse(api_episode['date_published'])

        api_soup = BeautifulSoup(api_episode["content_html"], "html.parser")
        page_soup = BeautifulSoup(requests.get(
            api_episode["url"]).content, "html.parser")

        blurb = api_episode["summary"]

        sponsors = parse_sponsors(
            hugo_data, api_soup, page_soup, show_config["acronym"], episode_number)

        links = html2text.html2text(
            str(get_list(api_soup, "Links:") or get_list(api_soup, "Episode Links:")))

        tags = []
        for link in page_soup.find_all("a", class_="tag"):
            tags.append(link.get_text().strip())

        tags = sorted(tags)

        hosts = parse_hosts(hugo_data, page_soup,
                            show_config, episode_number)

        guests = parse_guests(hugo_data, page_soup,
                            show_config, episode_number)

        show_attachment = api_episode["attachments"][0]

        output = TEMPLATE.render(
            {
                # "title": api_episode["title"],
                "title_plain": get_plain_title(api_episode["title"]),
                "blurb": blurb,
                "date_published": publish_date.date().isoformat(),
                "is_draft": "false",
                # TODO: In what case should the "Featured" category be added?
                "categories": [show_config["name"]],
                "tags": tags,
                "hosts": hosts,
                "guests": guests,
                "sponsors": sponsors,
                "header_image": show_config["header_image"],

                "episode_number": episode_number,
                "episode_number_padded": episode_number_padded,
                "podcast_duration": get_duration(int(show_attachment['duration_in_seconds'])),
                # TODO: the url in fireside is prefixed using https://chtbl.com not http://www.podtrac.com. Should this be left as is or changed to use podtrac?
                "podcast_file": show_attachment["url"],
                "podcast_bytes": show_attachment["size_in_bytes"],
                # "url": api_episode["url"],

                "youtube_link": "",  # TODO: leave empty or use None?
                "video_file": "",  # TODO: leave empty or use None?
                "links": links
            }
        )

        with open(output_file, "w") as f:
            print("Saving", api_episode["url"])
            f.write(output)
            
    except Exception as e:
        print(f"ERROR | Failed to create an episode from url `{api_episode.get('url')}`. Exception: {e}")

def parse_hosts(hugo_data, page_soup: BeautifulSoup, show_config, ep):
    show = show_config["acronym"]
    base_url = show_config["fireside_url"]

    hosts = []

    # assumes the hosts are ALWAYS the first <ul> and guests are in the second one
    hosts_links = page_soup.find("ul", class_="episode-hosts").find_all("a")

    # hosts_links = page_soup.select(".episode-hosts ul:first-child a")
    for link in hosts_links:
        try:
            host_name = link.get("title").strip()

            host = hugo_data["hosts"]["_data"].get(host_name)
            if host:
                hosts.append(host["username"])
            else:
                log_warn(show, ep, f"Missing HOST definition for `{host_name}`")
                host_page_url = base_url + link.get("href")
                MISSING_HOSTS.add(host_page_url)
                hosts.append(get_username_from_url(host_page_url))
        except Exception as e:
            print(f"ERROR | {show} {ep} | Failed to parse host for link href `{link.get('href')}`. Exception: {e}")
    return hosts


def parse_guests(hugo_data, page_soup, show_config, ep):
    show = show_config["acronym"]
    base_url = show_config["fireside_url"]

    guests = []

    # assumes the hosts are ALWAYS the first <ul> and guests are in the second one
    hosts_list = page_soup.find("ul", class_="episode-hosts")  # <- this would always be the hosts list
    # look for the NEXT `ul.episode-hosts`, that should be the guests list (might not exist)
    guests_list = hosts_list.find_next("ul", class_="episode-hosts")
    if not guests_list:
        return guests
    
    guests_links = guests_list.find_all("a")
    for link in guests_links:
        try:
            guest_name = link.get("title").strip()

            guest = hugo_data["guests"]["_data"].get(guest_name)
            # Sometimes the guests are already defined in the hosts, for example if they
            # are hosts in a different show. So try to find the within hosts.
            host_guest = hugo_data["hosts"]["_data"].get(guest_name)

            if guest:
                guests.append(guest["username"])
            elif host_guest:
                guests.append(host_guest["username"])
            else:
                log_warn(show, ep, f"Missing GUEST definition for `{guest_name}`")
                guest_page_url = base_url + link.get("href")
                MISSING_GUESTS.add(guest_page_url)
                guests.append(get_username_from_url(guest_page_url))
        
        except Exception as e:
            print(f"ERROR | {show} {ep} | Failed to parse episode guest for link href `{link.get('href')}`. Exception: {e}")
        

    return guests


def parse_sponsors(hugo_data, api_soup, page_soup, show, ep):
    # Get only the links of all the sponsors
    sponsors_ul = get_list(api_soup, "Sponsored By:")
    if not sponsors_ul:
        log_warn(show, ep, "No sponsors found for this episode")
        return []

    sponsors_links = [a["href"]
                      for a in sponsors_ul.select('li > a:first-child')]

    sponsors = []
    for sl in sponsors_links:
        try:
            s = hugo_data["sponsors"]["_data"].get(sl)
            if s:
                sponsors.append(s["shortname"])
            else:
                log_warn(show, ep, f"Missing SPONSOR definition for `{sl}`")

                # Very ugly but works. The goal is to get the hostname of the sponsor link
                # without the subdomain. It would fail on tlds like "co.uk" - But I don't
                # think JB had any sponsors like that so it's fine.
                sponsor_slug = ".".join(urlparse(sl).hostname.split(".")[-2:])
                shortname = f"{sponsor_slug}-{show}".lower()
                sponsors.append(shortname)

                filename = f"{shortname}.json"

                # Find the <a> element on the page with the link
                sponsor_a = page_soup.find("div", class_="episode-sponsors").find("a", attrs={"href": sl})
                if sponsor_a:
                    MISSING_SPONSORS.update({
                        filename: {
                            "shortname": shortname,
                            "name": sponsor_a.find("header").text.strip(),
                            "description": sponsor_a.find("p").text.strip(),
                            "link": sl
                        }
                    })
        except Exception as e:
            print(f"ERROR | {show} {ep} | Failed to collect/parse sponsor data for `{sl}`! Exception: {e}")

    return sponsors


def save_json_file(filename, json_obj, dest_dir):
    mkdir_safe(dest_dir)

    file_path = os.path.join(dest_dir, filename)

    with open(file_path, "w") as f:
        f.write(json.dumps(json_obj, indent=4))

    print(f"Saved new json file `{file_path}`")


def read_hugo_data():
    hugo_data = {
        "guests": {
            "_key": "name",
            "_data": {}
        },
        "hosts": {
            "_key": "name",
            "_data": {}
        },
        "sponsors": {
            "_key": "link",
            "_data": {}
        }
    }

    for key, item in hugo_data.items():
        files_dir = f"/hugo-data/{key}"
        json_files = os.listdir(files_dir)

        for file in json_files:
            file_path = f"{files_dir}/{file}"
            with open(file_path, "r") as f:
                json_data = json.loads(f.read())
                data_key = json_data.get(item["_key"])

                if not data_key:
                    print(f"read_hugo_data: skipping file `{file_path}` since it "
                          "doesn't have the expected key `{item._key}`")
                    continue

                item["_data"].update({data_key: json_data})

    hugo_data_debug = json.dumps(hugo_data, indent=2)
    print(f"read_hugo_data: {hugo_data_debug}")

    return hugo_data

def get_username_from_url(url):
    """
    Get the last path part of the url which is the username for the hosts and guests
    """
    return urlparse(url).path.split("/")[-1]

def create_host_or_guest(url, dirname):
    try:
        valid_dirnames = {"hosts", "guests"}
        assert dirname in valid_dirnames, "dirname arg must be either `hosts` or `guests`"

        page_soup = BeautifulSoup(requests.get(url).content, "html.parser")
        
        name = page_soup.find("h1").text.strip()

        username = get_username_from_url(url)

        # It's possible to replace url part "avatar_small.jpg" to "avatar.jpg" to get higher
        # res img, but not sure if required.
        avatar_url = page_soup.find("div", class_="hero-avatar").find("img").get("src")
        resp = requests.get(avatar_url)
        avatar_bytes = resp.content
        file_ext = resp.headers.get("x-bz-file-name").split(".")[-1]

        avatars_dir = os.path.join(DATA_ROOT_DIR, "static", "images", dirname)
        mkdir_safe(avatars_dir)

        filename = f"{username}.{file_ext}"
        avatar_file = os.path.join(avatars_dir, filename)

        with open(avatar_file, "wb") as f:
            f.write(avatar_bytes)


        # Get social links

        homepage = None
        twitter = None
        linkedin = None
        instagram = None
        gplus = None
        youtube = None
        links = page_soup.find("nav", class_="links").find_all("a")

        # NOTE: This will work only if none of the links are shortened urls
        for link in links:
            href = link.get("href").lower()
            if "Website" in link.text:
                homepage = href
            elif "twitter" in href:
                twitter = href
            elif "linkedin" in href:
                linkedin = href
            elif "instagram" in href:
                instagram = href
            elif "google" in href:
                gplus = href
            elif "youtube" in href:
                youtube = href

        host_json = {
            "username": username, # e.g. "alexktz"
            "name": name, # e.g. "Alex Kretzschmar"
            "bio":  page_soup.find("section").text.strip(), # e.g. "Red Hatter. Drone Racer. Photographer. Dog lover."
            "avatar":  f"/images/{dirname}/{filename}", # e.g. "/images/guests/alex_kretzschmar.jpeg"
            "homepage": homepage, # e.g. "https://www.linuxserver.io/"
            "twitter": twitter, # e.g. "https://twitter.com/ironicbadger"
            "linkedin": linkedin, # e.g. "https://www.linkedin.com/in/alex-kretzschmar/""
            "instagram": instagram,
            "gplus": gplus,
            "youtube": youtube,
        }

        hosts_dir = os.path.join(DATA_ROOT_DIR, "data", dirname)
        save_json_file(f"{username}.json", host_json, hosts_dir)
    except Exception as e:
        print(f"ERROR | Failed to create/save a new host/guest file from `{url}`. Exception: {e}")


def main():
    with open("config.yml") as f:
        shows = yaml.load(f, Loader=yaml.SafeLoader)['shows']

    hugo_data = read_hugo_data()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for show_slug, show_config in shows.items():
            # Use same structure as in the root project for easy copy over
            output_dir = os.path.join(
                DATA_ROOT_DIR, "content", "show", show_slug)
            mkdir_safe(output_dir)

            api_data = requests.get(
                show_config['fireside_url'] + "/json").json()

            for idx, api_episode in enumerate(api_data["items"]):
                futures.append(executor.submit(
                    create_episode, api_episode, show_config, hugo_data, output_dir))

        # Drain to get exceptions. This is important in order to collect all the
        # MISSING_* globals first before proceeding
        for future in concurrent.futures.as_completed(futures):
            future.result()

        # Now process the MISSING_* globals...

        output_dir = os.path.join(DATA_ROOT_DIR, "data", "sponsors")
        mkdir_safe(output_dir)

        futures = []  # reset futures

        # MISSING_SPONSORS:
        for filename, sponsor in MISSING_SPONSORS.items():
            futures.append(executor.submit(
                save_json_file, filename, sponsor, output_dir))

        # MISSING_HOSTS:
        for url in MISSING_HOSTS:
            futures.append(executor.submit(create_host_or_guest, url, "hosts"))

        # MISSING_GUESTS:
        for url in MISSING_GUESTS:
            futures.append(executor.submit(create_host_or_guest, url, "guests"))

        # Drain to get exceptions. Still have to mash CTRL-C, though.
        for future in concurrent.futures.as_completed(futures):
            future.result()


if __name__ == "__main__":
    main()
