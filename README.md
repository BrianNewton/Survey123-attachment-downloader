# Survey123 Download

A command-line script that downloads the data and all attachments for a Survey123 survey from ArcGIS Online.

For a given survey ID, the script:

1. Authenticates with your ArcGIS Online organization.
2. Exports the survey's response data to an Excel file and downloads it.
3. Downloads every attachment (photos, files, etc.) from each layer and table in the survey.
4. Writes a CSV for each layer/table that maps each attachment file to its parent record's object ID.

## Requirements

- Python 3.9 or newer (check which versions your installed `arcgis` release supports)
- An ArcGIS Online account with access to the survey
- The URL of your ArcGIS organization (for example, `https://wlugeography.maps.arcgis.com`)
- The survey's item ID

## Installation

1. **Download the files** and place `requirements.txt` and the script in the same folder.

2. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   `requirements.txt` contains:

   ```
   arcgis
   tqdm
   ```

   > The `arcgis` package is large and pulls in many dependencies (numpy, pandas, and others), so the first install can take a few minutes.
   > If `pip` installation fails, Esri recommends using conda for the ArcGIS API for Python. See [Esri's installation guide](https://developers.arcgis.com/python/latest/guide/install-and-set-up/).

## Usage

```bash
python survey123_attachments_download.py <url> <username> <password> <destination> <surveyID> [options]
```

### Arguments

| Argument | Description |
| --- | --- |
| `url` | URL of your ArcGIS organization, for example `https://wlugeography.maps.arcgis.com`. |
| `username` | Username of your ArcGIS Online account. The account must have access to the survey. |
| `password` | Password for that account. |
| `destination` | Directory where the Excel file and attachments will be saved. |
| `surveyID` | Item ID of the survey to download. |

### Options

| Option | Description |
| --- | --- |
| `-k`, `--keep_org_item` | Keep the exported Excel item in your organization's content. By default it is deleted after download. |
| `-s`, `--store_csv_w_attachments` | Save each attachment-mapping CSV inside its layer's attachment folder. By default the CSVs are saved in the root destination folder. |
| `-h`, `--help` | Show the help message and exit. |

### Finding your survey ID

Open the survey in your ArcGIS Online content. The survey ID is the 32-character string at the end of the item page URL:

```
https://<your-org>.maps.arcgis.com/home/item.html?id=<surveyID>
```

### Examples

Basic download:

```bash
python survey123_attachments_download.py https://wlugeography.maps.arcgis.com jsmith "myPassword" ./downloads 0123456789abcdef0123456789abcdef
```

Keep the exported item in your organization and store the CSVs with the attachments:

```bash
python survey123_attachments_download.py https://wlugeography.maps.arcgis.com jsmith "myPassword" ./downloads 0123456789abcdef0123456789abcdef -k -s
```

If your password contains special characters, wrap it in quotes.

## Output

Given a destination of `./downloads`, the output looks like this:

```
downloads/
├── <Survey Title>.xlsx                  # Exported survey data
├── <LayerName>_attachments.csv          # Attachment-to-record mapping (default location)
├── <LayerName>_attachments/             # Attachment files for that layer
│   ├── photo1.jpg
│   └── photo2.jpg
└── ...
```

With `-s`, each `<LayerName>_attachments.csv` is placed inside its matching `<LayerName>_attachments/` folder instead.

Layer folder names have all non-alphanumeric characters removed (for example, `Site Photos (2)` becomes `SitePhotos2_attachments`).

### Attachment CSV format

Each CSV has two columns:

| Column | Description |
| --- | --- |
| `Parent objectId` | The object ID of the record the attachment belongs to. Matches the object ID in the exported Excel data. |
| `Attachment path` | Path to the attachment file, relative to the destination folder. |

Layers and tables with no attachments are skipped.

## Security note

Passing your password as a command-line argument means it may be stored in your shell history and visible to other users on a shared machine. Avoid running this on shared systems, and consider clearing your shell history afterward.

## Troubleshooting

- **"Account authentication failed"**: Check your username and password, and confirm the organization URL is correct and the account belongs to that organization.
- **"Failed to fetch survey"**: Verify the survey ID and confirm your account has access to the survey and its related feature service.
- **Install errors**: Make sure you are using a supported Python version, or try a conda environment as recommended by Esri.

## Acknowledgements

This script is adapted from the example in Esri's Survey123 documentation, [Export survey data with attachments](https://developers.arcgis.com/survey123/guide/export-survey-data-with-attachments/).
