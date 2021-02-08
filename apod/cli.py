import json
import os
from pathlib import Path, PurePath

import click
import pendulum

from apod.blogger import Blogger


@click.group()
def cli():
    pass


@cli.command()
@click.option("-o", "--output_folder")
@click.option(
    "-f",
    "--output_format",
    default="YYYY/MM/YYYYMMDD",
    help="Paht format for output files",
)
@click.option("-b", "--blog_id", envvar="BLOGGER_BLOG_ID")
@click.option(
    "-i",
    "--client_id",
    envvar="GCP_CLIENT_ID",
    help="OAuth 2.0 Client ID from Credentials of GCP APIs & Services",
)
@click.option(
    "-s",
    "--client_secret",
    envvar="GCP_CLIENT_SECRET",
    help="OAuth 2.0 Client ID from Credentials of GCP APIs & Services",
)
@click.option(
    "-t",
    "--refresh_token",
    envvar="GCP_REFRESH_TOKEN",
    help="Refresh token to workaround OAuth 2.0 process",
)
@click.option(
    "-k",
    "--api_key",
    envvar="GCP_API_KEY",
    help="API Key from Credentials of GCP APIs & Services",
)
def backup(
    output_folder,
    output_format,
    blog_id,
    client_id,
    client_secret,
    refresh_token,
    api_key,
):
    """
    Save blogger posts as json files
    """
    blogger = Blogger(
        client_id=client_id,
        client_secret=client_secret,
        refresh_token=refresh_token,
        api_key=api_key,
    )

    for post in blogger.list(blog_id):
        path = PurePath(post["url"])
        try:
            publish_time = pendulum.from_format(path.name.split(".")[0], "YYYYMMDD")
        except ValueError:
            continue

        output_path = Path(
            os.path.join(output_folder, f"{publish_time.format(output_format)}.json")
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as fp:
            json.dump(post, fp, indent=2, ensure_ascii=False)
            fp.write("\n")  # add newline to end of file
            click.echo(f"Saved: {output_path}")
