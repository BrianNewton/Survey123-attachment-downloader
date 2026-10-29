import argparse
import csv
import os
import re
import sys

from arcgis.gis import GIS
from tqdm import tqdm


def survey_download(url, username, password, survey_item_id, save_path, keep_org_item, store_csv_w_attachments):

    ### Authenticate credentials
    print("Authenticating arcgis account... ", end = "", flush=True)
    try:
        gis = GIS(url, username, password)
    except Exception:
        print("Account authentication failed, please verify account details")
        sys.exit(1)
    else:
        print("Done")

    ### Fetch survey ID
    print(f"Fetching survey by ID {survey_item_id}... ", end = "", flush = True)
    try:
        survey_by_id = gis.content.get(survey_item_id)
        rel_fs = survey_by_id.related_items('Survey2Service', 'forward')[0]
        item_excel = rel_fs.export(title=survey_by_id.title, export_format='Excel')
        item_excel.download(save_path=save_path)
        if not bool(keep_org_item):
            item_excel.delete(force=True)
    except Exception:
        print("Failed to fetch survey, please verify survey ID")
        sys.exit(1)
    else:
        print("Done")

    ### Download
    layers = rel_fs.layers + rel_fs.tables
    for i in layers:
        name = i.properties.name

        if i.properties.hasAttachments == True:
            safe_name = re.sub(r'[^A-Za-z0-9]+', '', name)
            feature_layer_folder = os.path.join(save_path, f'{safe_name}_attachments')
            os.makedirs(feature_layer_folder, exist_ok=True)

            if bool(store_csv_w_attachments):
                path = os.path.join(feature_layer_folder, f"{name}_attachments.csv")
            else:
                path = os.path.join(save_path, f"{name}_attachments.csv")

            csv_fields = ['Parent objectId', 'Attachment path']
            with open(path, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(csv_fields)

                feature_object_ids = i.query(where="1=1", return_ids_only=True, order_by_fields='objectid ASC')
                oids = feature_object_ids['objectIds']

                for current_oid in tqdm(oids, desc=f"Downloading {name}"):
                    current_oid_attachments = i.attachments.get_list(oid=current_oid)

                    for attachment in current_oid_attachments:
                        current_attachment_path = i.attachments.download(
                            oid=current_oid,
                            attachment_id=attachment['id'],
                            save_path=feature_layer_folder,
                        )
                        csvwriter.writerow([
                            current_oid,
                            os.path.join(f'{safe_name}_attachments', os.path.split(current_attachment_path[0])[1]),
                        ])
        else:
            tqdm.write(f"Skipping {name} (no attachments)")


def main():
    ### Parse arguments
    parser = argparse.ArgumentParser(
        prog = "Survey123 Download",
        description = "Downloads survey data and all associated attachments for a given survey ID"
    )

    parser.add_argument('url', help = "The URL for your ArcGIS organization (eg. https://wlugeography.maps.arcgis.com)")
    parser.add_argument('username', help = "Username of associated ESRI online account, account must have access to the survey ID")
    parser.add_argument('password', help = "Password of associated ESRI online account")
    parser.add_argument('destination', help = "Destination directory for downloaded files and attachments")
    parser.add_argument('surveyID', help = "Survey ID of survey to be downloaded")
    parser.add_argument('-k', '--keep_org_item', action = 'store_true', help = "Set True if you want to keep the exported item in your organization content. Default False")
    parser.add_argument('-s', '--store_csv_w_attachments', action = 'store_true', help = 'Choose if the .csv file that maps each attachment to its parent object ID is stored in the root download folder (false, default), or in each individual layer folder (true)')

    args = parser.parse_args()

    ### Execute downloader
    survey_download(args.url, args.username, args.password, args.surveyID, args.destination, args.keep_org_item, args.store_csv_w_attachments)


if __name__ == "__main__":
    main()
